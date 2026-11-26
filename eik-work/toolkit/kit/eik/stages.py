"""The evaluation as separate stages, each a pure function of its inputs that returns a JSON report.
A coordinator runs them as jobs (docs/DEPLOY.md); `python -m eik evaluate` chains them locally.

  gate       static rules, builds for every target, the duplicate check   seconds    any host
  measure    instruction counts on the seed's inputs, every scored output   minutes    x86-64
             checked, peak stack, a stratified target-side sample
  decide     the takeover rule on two measurements with the same seed      instant    anywhere
  compare    measure the entry and the champions on one seed, then decide  minutes    x86-64
  fullcheck  all 2^32 inputs of one function (or one shard of chunks)      ~40 min    many cores
             under UBSan + ASan, against the reference digests              per fn
  merge      the shards of a full check into one verdict                    instant    anywhere

Verdicts: gate -> accepted | rejected; measure and fullcheck -> passed | rejected. A rejection
names the stage and the reasons, and is always the entry's fault. Anything that is not the entry's
fault (configuration, sandbox, missing reference, a harness bug) raises InfraError, which the CLI
reports with exit code 3, so a coordinator retries it instead of rejecting the miner.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import signal
import struct
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from . import config as K
from . import fingerprint as FP
from . import inputs as I
from . import policy as P
from . import production
from . import sandbox as SB
from . import score as S
from . import toolchain as T
from .production import InfraError

SCHEMA = "eik-report-1"
ASAN_EXIT, UBSAN_EXIT = 66, 67
SANITIZER_ENV = {
    "ASAN_OPTIONS": f"exitcode={ASAN_EXIT}:detect_leaks=0:abort_on_error=0:handle_abort=1:symbolize=1",
    "UBSAN_OPTIONS": f"halt_on_error=1:exitcode={UBSAN_EXIT}:print_stacktrace=1",
}

__all__ = ["InfraError", "gate", "measure", "decide", "compare", "fullcheck", "merge_fullchecks"]


def _base(kind: str, src: Path) -> dict:
    if not Path(src).is_file():
        raise InfraError(f"no such entry file: {src}")
    return {"schema": SCHEMA, "kind": kind, "competition": K.COMPETITION_SLUG, "sha256": T.sha(src),
            "fingerprint": FP.ids()}


def _reject(rep: dict, stage: str, reasons, **kw) -> dict:
    rep.update(verdict="rejected", stage=stage, reasons=list(reasons), **kw)
    return rep


# --- gate -----------------------------------------------------------------------------------------

def gate(src: Path, known_hashes=()) -> dict:
    """Static rules (text, AST, object files), guest images for every target, and the duplicate check
    against `known_hashes`: the normalised hashes of every entry already accepted."""
    production.enforce("gate")
    src = Path(src).resolve()
    rep = _base("gate", src)
    rep["source_bytes"] = src.stat().st_size
    try:
        info = P.check_all(src)
        for t in K.TARGETS:
            T.guest_image(src, t)
        norm = P.normalised_hash(src)
    except P.Reject as e:
        return _reject(rep, e.stage, e.reasons)
    except T.BuildError as e:
        return _reject(rep, "build", [str(e)])
    rep.update(bytes=info["bytes"], stack_bound=info["stack_bound"], normalised_sha256=norm)
    if norm in set(known_hashes):
        return _reject(rep, "duplicate", ["same normalised source as an accepted entry (whitespace, comments, "
                                          "macros and identifier names are ignored)"])
    rep.update(verdict="accepted", stage=None, reasons=[])
    return rep


# --- measure --------------------------------------------------------------------------------------

def _inputs_digest(seed: int) -> str:
    """The exact words every function is measured on for this seed; equal digests mean equal inputs."""
    h = hashlib.sha256()
    for fn in K.FUNCTIONS:
        for name, words in I.draw(seed, fn).items():
            h.update(f"{fn}:{name}:".encode() + b"".join(w.to_bytes(4, "little") for w in words))
    return h.hexdigest()


def _job(args):
    src, target, seed, sample = args
    return S.measure(Path(src), target, seed, sample)


def _measure_many(specs, seed: int) -> list:
    """[(src, targets, sample)] -> one measure report each, all targets of all entries in one pool."""
    production.enforce("measure")
    I.prepare_fresh_pools(seed)
    inputs = _inputs_digest(seed)
    hard = ({"source": "hardscan", "samples": I.FRESH_SAMPLES, "threshold_log2_ulps": I.FRESH_THRESHOLD,
             "sizes": {fn: len(I.hard_pool(fn, seed)) for fn in K.FUNCTIONS}}
            if I.FRESH else {"source": "published", "files": [f"reference/hard-{fn}.txt" for fn in K.FUNCTIONS]})
    reps, jobs, owners = [], [], []
    for i, (src, targets, sample) in enumerate(specs):
        src = Path(src).resolve()
        rep = _base("measure", src)
        rep.update(seed=seed, inputs_sha256=inputs, hard_pool=hard, sampled=sample)
        reps.append(rep)
        try:
            rep["bytes"] = P.check_all(src)["bytes"]
            rep["images"] = {t: T.sha(T.guest_image(src, t)) for t in targets}
        except P.Reject as e:
            _reject(rep, e.stage, e.reasons)
            continue
        except T.BuildError as e:
            _reject(rep, "build", [str(e)])
            continue
        for t in targets:
            jobs.append((str(src), t, seed, sample))
            owners.append(i)
    if jobs:
        with ProcessPoolExecutor(max_workers=max(1, min(len(jobs), K.HOST_THREADS))) as ex:
            results = list(ex.map(_job, jobs))
        for i, m in zip(owners, results):
            reps[i].setdefault("targets", {})[m["target"]] = m
    for rep in reps:
        if rep.get("verdict") != "rejected":
            _judge(rep)
    return reps


def _judge(rep: dict):
    """Rejection on any target, else the scores of every board this measurement covers."""
    for t, m in rep["targets"].items():
        if m.get("timeout"):
            return _reject(rep, f"run:{t}", [m["timeout"]])
        if m["wrong"]:
            return _reject(rep, f"outputs:{t}", ["wrong output on a scored input"], examples=m["wrong"])
        if m["sample"] and m["sample"]["mismatches"]:
            return _reject(rep, f"target-sample:{t}", [
                f"{m['sample']['mismatches']} wrong outputs in a stratified sample of {m['sample']['words']} words"],
                examples=m["sample"]["examples"])
        if m["stack"] > K.CAP_STACK_BYTES:
            return _reject(rep, f"stack:{t}", [f"peak stack {m['stack']} > {K.CAP_STACK_BYTES} bytes"])
    scores = {}
    for t in rep["targets"]:
        s, parts = S.score(rep["targets"][t], rep["bytes"][t])
        scores[t] = {"S": s, **parts, **({} if K.TARGETS[t]["scored"] else {"reported_only": True})}
    if all(t in scores for t in K.SCORED):
        scores["overall"] = {"S": math.sqrt(math.prod(scores[t]["S"] for t in K.SCORED))}
    rep.update(scores=scores, verdict="passed", stage=None, reasons=[])


def measure(src: Path, seed: int, targets=None, sample=True) -> dict:
    """Instruction counts of one entry on the inputs drawn from `seed`, on every target (or `targets`),
    with every output checked. `sample` also batch-checks a stratified sample of all 2^32 words per
    target: on for a challenger, off when re-measuring a champion that already passed it."""
    return _measure_many([(src, list(targets or K.TARGETS), sample)], seed)[0]


# --- decide ---------------------------------------------------------------------------------------

def _require_comparable(entry: dict, other: dict, what: str):
    for key, label in (("seed", "seed"), ("inputs_sha256", "inputs")):
        if entry.get(key) != other.get(key):
            raise InfraError(f"{what} was measured on different {label} ({other.get(key)} vs {entry.get(key)})")
    if entry["fingerprint"]["measurement"] != other["fingerprint"]["measurement"]:
        raise InfraError(f"{what} was measured by a different harness (measurement identity differs)")


def decide(entry: dict, champions: dict) -> dict:
    """The takeover rule. `entry` is a passed measure report; `champions` maps a board to its
    champion's measure report on the same seed, or to None for a board nobody holds yet.

    An entry is a candidate for a board when S_entry <= TAKEOVER_RATIO x S_champion (or the board is
    unheld). Candidacy is final only after a complete full check of all three functions."""
    if entry.get("kind") != "measure" or entry.get("verdict") != "passed":
        raise InfraError("decide needs a passed measure report of the entry")
    boards, candidates = {}, []
    for b in K.BOARDS:
        c = champions.get(b)
        e_s = entry["scores"][b]["S"]
        if c is None:
            boards[b] = {"champion_sha256": None, "entry_S": e_s, "champion_S": None, "ratio": None, "beats": True}
        else:
            if c.get("kind") != "measure" or c.get("verdict") != "passed" or b not in c.get("scores", {}):
                raise InfraError(f"the champion of {b} has no passed measurement covering that board")
            _require_comparable(entry, c, f"the champion of {b}")
            c_s = c["scores"][b]["S"]
            ratio = e_s / c_s
            boards[b] = {"champion_sha256": c["sha256"], "entry_S": e_s, "champion_S": c_s, "ratio": ratio,
                         "beats": ratio <= K.TAKEOVER_RATIO}
        if boards[b]["beats"]:
            candidates.append(b)
    return {"schema": SCHEMA, "kind": "decision", "competition": K.COMPETITION_SLUG, "sha256": entry["sha256"],
            "seed": entry["seed"], "takeover_ratio": K.TAKEOVER_RATIO, "boards": boards,
            "candidate_boards": candidates, "needs_fullcheck": bool(candidates),
            "fingerprint": entry["fingerprint"]}


def compare(src: Path, seed: int, champion_files: dict) -> dict:
    """Measure the entry (every target, with the sample) and each board's champion (scored targets,
    no sample) on one seed in one job, then decide. `champion_files` maps board -> source path, or
    None for an unheld board; a champion holding several boards is measured once."""
    distinct = []
    for path in champion_files.values():
        if path is not None and Path(path).resolve() not in distinct:
            distinct.append(Path(path).resolve())
    reps = _measure_many([(src, list(K.TARGETS), True)] + [(p, list(K.SCORED), False) for p in distinct], seed)
    entry, champs = reps[0], dict(zip(distinct, reps[1:]))
    out = {"schema": SCHEMA, "kind": "compare", "competition": K.COMPETITION_SLUG, "sha256": entry["sha256"],
           "seed": seed, "measure": entry, "champions": {r["sha256"]: r for r in champs.values()},
           "fingerprint": entry["fingerprint"]}
    for p, r in champs.items():
        if r["verdict"] != "passed":  # a champion that no longer measures cleanly is the harness's problem
            raise InfraError(f"champion {p.name} ({r['sha256'][:12]}) failed re-measurement at {r['stage']}: "
                             + "; ".join(r["reasons"]))
    if entry["verdict"] == "passed":
        out["decision"] = decide(entry, {b: (champs[Path(p).resolve()] if p is not None else None)
                                         for b, p in champion_files.items()})
    return out


# --- fullcheck ------------------------------------------------------------------------------------

def _sanitizer_report(stderr: str) -> str:
    keep = [l for l in stderr.splitlines() if "runtime error" in l or "ERROR: AddressSanitizer" in l
            or "SUMMARY:" in l or l.lstrip().startswith("#")]
    return "\n".join(keep)[:2000]


def fullcheck(src: Path, fn: str, chunks=None, quick=False, seed=1, threads=None) -> dict:
    """All 2^32 inputs of `fn` (or chunks lo..hi-1 of the 4,096, for a shard) under UBSan + ASan,
    compared with the reference digests. `quick` checks a seeded 3% sample instead (development)."""
    production.enforce("fullcheck")
    if fn not in K.FUNCTIONS:
        raise InfraError(f"unknown function {fn!r}")
    problems = FP.reference_problems()
    if problems:
        raise InfraError("reference digests: " + "; ".join(problems))
    src = Path(src).resolve()
    rep = _base("fullcheck", src)
    lo, hi = chunks if chunks else (0, K.CHUNKS)
    if not (0 <= lo < hi <= K.CHUNKS):
        raise InfraError(f"bad chunk range {lo}:{hi} (0 <= lo < hi <= {K.CHUNKS})")
    rep.update(function=fn, chunk_lo=lo, chunk_hi=hi, quick=bool(quick and not chunks))
    try:
        exe = T.host_checker(src)
    except T.BuildError as e:
        return _reject(rep, "fullcheck:build", [str(e)])
    threads = threads or K.HOST_THREADS
    argv = [exe, fn, K.REFERENCE / f"{fn}.digest", threads,
            K.QUICK_CHUNKS if rep["quick"] else 0, seed] + ([lo, hi] if chunks else [])
    budget = K.check_budget("host", K.QUICK_CHUNKS if rep["quick"] else hi - lo, threads)
    rep["budget_seconds"] = budget
    try:
        p = SB.run(argv, ro=[exe, K.REFERENCE], env=SANITIZER_ENV, timeout=budget)
    except subprocess.TimeoutExpired:
        return _reject(rep, "fullcheck:timeout", [f"the check of {fn} took longer than {budget} s, "
                                                  f"{K.BUDGET_FACTOR} times what the incumbent needs; the entry is "
                                                  "too slow on some inputs"])
    line = next((l for l in p.stdout.splitlines() if l.startswith("{")), None)
    result = json.loads(line) if line else None
    san = _sanitizer_report(p.stderr)
    rep["exit"] = p.returncode
    if p.returncode in (ASAN_EXIT, UBSAN_EXIT) or (san and p.returncode != 0):
        return _reject(rep, "fullcheck:sanitizer", ["undefined behaviour or a memory error on some input"],
                       sanitizer=san)
    if result is None or p.returncode not in (0, 1):
        sig = f" (signal {signal.Signals(-p.returncode).name})" if p.returncode < 0 else ""
        raise InfraError(f"check binary exited {p.returncode}{sig} without a result: {p.stderr.strip()[-1500:]}")
    rep.update(words_checked=result["words_checked"], mismatches=result["mismatches"], seconds=result["seconds"],
               complete=result["complete"], range_complete=result["range_complete"],
               examples=[{"input": a, "got": b, "want": c} for a, b, c in result["examples"]])
    if result["mismatches"]:
        return _reject(rep, "fullcheck:outputs", [f"{result['mismatches']} wrong outputs of {fn}"])
    if p.returncode != 0:
        raise InfraError(f"check binary exited {p.returncode} with no mismatch: {p.stderr.strip()[-1500:]}")
    rep.update(verdict="passed", stage=None, reasons=[])
    return rep


# --- targetcheck ----------------------------------------------------------------------------------

QEMU = {"rv32im": ["qemu-riscv32"], "thumbv6m": ["qemu-arm", "-cpu", "max"], "thumbv7em": ["qemu-arm", "-cpu", "max"]}
CHUNK_BYTES = 4 << 20


def _target_range(argv, digests, lo, hi, state, idx):
    """One QEMU process over chunks lo..hi-1: hash each streamed chunk against the reference."""
    proc = None
    try:
        cmd, env = SB.command(argv + [str(lo), str(hi)], ro=state["ro"])
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env or None,
                                preexec_fn=SB._limits(None, None))
        state["procs"][idx] = proc
        for c in range(lo, hi):
            if state["stop"].is_set():
                break
            data = proc.stdout.read(CHUNK_BYTES)
            if len(data) != CHUNK_BYTES:
                break
            if hashlib.sha256(data).digest() != digests[c * 32:(c + 1) * 32]:
                with state["lock"]:
                    state["bad"].append((c, data))
                state["stop"].set()
                break
            with state["lock"]:
                state["done"] += 1
        if state["stop"].is_set():
            proc.kill()
        proc.stdout.close()
        state["stderr"][idx] = proc.stderr.read().decode(errors="replace")[-2000:]
        proc.stderr.close()
        state["exit"][idx] = proc.wait()
    except Exception as e:  # recorded; the caller turns it into an InfraError
        state["errors"].append(f"{type(e).__name__}: {e}")
        state["stop"].set()
        if proc is not None:
            proc.kill()


def targetcheck(src: Path, fn: str, target: str, chunks=None, jobs=None) -> dict:
    """All 2^32 inputs of `fn` (or chunks lo..hi-1) on `target`'s object code under QEMU user mode,
    against the reference digests: the same code the emulator scored, so a compiler that miscompiles
    for one ISA, or behaviour that differs between the targets and the host, is caught. `jobs`
    QEMU processes split the range (default: one per core)."""
    import threading
    from . import reference as R
    production.enforce("fullcheck")
    if fn not in K.FUNCTIONS or target not in K.TARGETS:
        raise InfraError(f"unknown function or target {fn!r} {target!r}")
    problems = FP.reference_problems()
    if problems:
        raise InfraError("reference digests: " + "; ".join(problems))
    qemu = shutil.which(QEMU[target][0])
    if qemu is None:
        raise InfraError(f"{QEMU[target][0]} is not installed (QEMU user mode)")
    src = Path(src).resolve()
    rep = _base("targetcheck", src)
    lo, hi = chunks if chunks else (0, K.CHUNKS)
    if not (0 <= lo < hi <= K.CHUNKS):
        raise InfraError(f"bad chunk range {lo}:{hi} (0 <= lo < hi <= {K.CHUNKS})")
    rep.update(function=fn, target=target, chunk_lo=lo, chunk_hi=hi)
    try:
        exe = T.target_checker(src, target)
    except T.BuildError as e:
        return _reject(rep, f"targetcheck:build:{target}", [str(e)])
    rep["image_sha256"] = T.sha(exe)
    digests = (K.REFERENCE / f"{fn}.digest").read_bytes()
    jobs = max(1, min(jobs or K.HOST_THREADS, hi - lo))
    bounds = [lo + (hi - lo) * i // jobs for i in range(jobs + 1)]
    argv = [qemu, *QEMU[target][1:], str(exe), str(K.FUNCTIONS.index(fn))]
    state = {"ro": [exe, Path(qemu).resolve()], "stop": threading.Event(), "lock": threading.Lock(), "done": 0,
             "bad": [], "errors": [], "procs": [None] * jobs, "stderr": [""] * jobs, "exit": [None] * jobs}
    threads = [threading.Thread(target=_target_range, args=(argv, digests, bounds[i], bounds[i + 1], state, i),
                                daemon=True) for i in range(jobs)]
    t0 = time.monotonic()
    for t in threads:
        t.start()
    # Each process has a fixed range, so the budget is set by the longest one.
    budget = K.check_budget(target, max(bounds[i + 1] - bounds[i] for i in range(jobs)), 1)
    rep["budget_seconds"] = budget
    deadline = t0 + budget
    timed_out = False
    while any(t.is_alive() for t in threads):
        # Stop every process as soon as one shard fails or time is up, rather than when each
        # finishes its current chunk (minutes, for slow code).
        if state["stop"].is_set() or time.monotonic() > deadline:
            timed_out = not state["stop"].is_set()
            state["stop"].set()
            for p in state["procs"]:
                if p is not None and p.poll() is None:
                    p.kill()
            for t in threads:
                t.join(30)
            break
        state["stop"].wait(0.5)
    rep.update(seconds=round(time.monotonic() - t0, 1), words_checked=state["done"] << 20, jobs=jobs)
    if state["errors"]:
        raise InfraError("target check failed: " + "; ".join(state["errors"][:3]))
    if state["bad"]:
        c, data = min(state["bad"])
        words = list(range(c << 20, (c + 1) << 20))
        got = struct.unpack(f"<{1 << 20}I", data)
        want = R.outputs(fn, words)
        wrong = [(w, g, e) for w, g, e in zip(words, got, want) if g != e]
        rep.update(mismatches=len(wrong), chunk=c,
                   examples=[{"input": f"{w:08x}", "got": f"{g:08x}", "want": f"{e:08x}"} for w, g, e in wrong[:8]])
        return _reject(rep, f"targetcheck:outputs:{target}", [f"{len(wrong)} wrong outputs of {fn} in chunk {c} "
                                                              f"on {target}"])
    if timed_out:
        return _reject(rep, "targetcheck:timeout", [f"the check of {fn} on {target} took longer than {budget} s, "
                                                    f"{K.BUDGET_FACTOR} times what the incumbent needs"])
    crashed = [(i, x) for i, x in enumerate(state["exit"]) if x != 0]
    if crashed:
        i, code = crashed[0]
        detail = state["stderr"][i].strip()
        if code == 2 or "qemu" in detail and "uncaught target signal" not in detail:
            raise InfraError(f"target check exited {code}: {detail}")
        return _reject(rep, f"targetcheck:crash:{target}", [f"the entry crashed on {target} in chunks "
                                                            f"{bounds[i]}..{bounds[i + 1] - 1}: {detail[-300:]}"])
    rep.update(mismatches=0, range_complete=state["done"] == hi - lo, verdict="passed", stage=None, reasons=[])
    rep["complete"] = rep["range_complete"] and (lo, hi) == (0, K.CHUNKS)
    return rep


def _coverage(reports, fn) -> tuple:
    covered = bytearray(K.CHUNKS)
    words = 0
    for r in reports:
        if r.get("function") == fn and r.get("range_complete") and not r.get("quick"):
            covered[r["chunk_lo"]:r["chunk_hi"]] = b"\1" * (r["chunk_hi"] - r["chunk_lo"])
            words += r["words_checked"]
    return sum(covered), words


def merge_fullchecks(reports: list, require_targets=()) -> dict:
    """One verdict from fullcheck (host) and targetcheck shards: passed only when the host shards
    cover all 4,096 chunks of every function, and so do the target shards of every target in
    `require_targets`; all for the same source and verifier, with no shard rejected."""
    if not reports:
        raise InfraError("no fullcheck reports to merge")
    first = reports[0]
    for r in reports:
        if r.get("kind") not in ("fullcheck", "targetcheck"):
            raise InfraError("merge takes fullcheck and targetcheck reports only")
        if r["sha256"] != first["sha256"] or r["fingerprint"]["verifier"] != first["fingerprint"]["verifier"]:
            raise InfraError("shards of different sources or verifiers cannot be merged")
    out = {"schema": SCHEMA, "kind": "fullcheck-merged", "competition": K.COMPETITION_SLUG,
           "sha256": first["sha256"], "fingerprint": first["fingerprint"], "functions": {}}
    rejected = [r for r in reports if r.get("verdict") == "rejected"]
    if rejected:
        r = rejected[0]
        out.update(verdict="rejected", stage=r["stage"], reasons=r["reasons"], function=r.get("function"),
                   **{k: r[k] for k in ("examples", "sanitizer") if k in r})
        return out
    missing = []
    host = [r for r in reports if r["kind"] == "fullcheck"]
    for fn in K.FUNCTIONS:
        n, words = _coverage(host, fn)
        out["functions"][fn] = {"chunks_covered": n, "words_checked": words}
        if n != K.CHUNKS:
            missing.append(f"{fn}: {K.CHUNKS - n} of {K.CHUNKS} chunks not checked on the host")
    out["targets"] = {}
    for t in sorted({r["target"] for r in reports if r["kind"] == "targetcheck"} | set(require_targets)):
        shards = [r for r in reports if r["kind"] == "targetcheck" and r["target"] == t]
        out["targets"][t] = {}
        for fn in K.FUNCTIONS:
            n, words = _coverage(shards, fn)
            out["targets"][t][fn] = {"chunks_covered": n, "words_checked": words}
            if t in require_targets and n != K.CHUNKS:
                missing.append(f"{fn} on {t}: {K.CHUNKS - n} of {K.CHUNKS} chunks not checked")
    out["required_targets"] = sorted(require_targets)
    if missing:
        out.update(verdict="incomplete", stage=None, reasons=missing)
    else:
        out.update(verdict="passed", stage=None, reasons=[])
    return out
