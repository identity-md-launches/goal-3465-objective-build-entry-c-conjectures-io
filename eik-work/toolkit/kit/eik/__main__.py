"""Command line.

Local use (miners, development; state in state/boards.json):

  python -m eik setup [--full]          reference library, digests, hard-input pools; the incumbent
                                        becomes champion of every board (--full: also run its full check)
  python -m eik check FILE              static policy and builds only (seconds)
  python -m eik evaluate FILE [--seed N] [--quick] [--force-check]
                                        everything, without changing the boards
  python -m eik submit FILE --name NAME [--seed N] [--quick]
                                        evaluate and, if it wins and passes the full check, take over
  python -m eik board                   current champions and history

Stage commands (the validator runs each as a separate job). Each writes one JSON report to stdout, or to
--out, and exits 0 for accepted/passed, 1 for rejected (the entry's fault), 3 for an infrastructure
error (not the entry's fault: retry or page an operator). Usage errors exit 2.

  python -m eik gate FILE [--known-hashes FILE]
  python -m eik measure FILE --seed N [--targets rv32im,thumbv6m] [--no-sample]
  python -m eik compare FILE --seed N [--champion BOARD=FILE ...]
  python -m eik decide --entry REPORT [--champion BOARD=REPORT ...]
  python -m eik fullcheck FILE --function sigmoid|tanh|exp [--chunks LO:HI] [--threads N]
  python -m eik targetcheck FILE --function F --target T [--chunks LO:HI] [--jobs N]
                                        every input on the target's object code, in QEMU user mode
  python -m eik merge REPORT... [--require-targets rv32im,thumbv6m]
                                        fullcheck/targetcheck shards -> one verdict
  python -m eik fingerprint [--details] the verifier and measurement identities
"""
import argparse
import json
import subprocess
import sys
import traceback
from pathlib import Path

from . import board as B
from . import config as K
from . import fingerprint as FP
from . import policy as P
from . import production
from . import sandbox as SB
from . import stages as ST
from . import toolchain as T
from .evaluate import evaluate, host_check

EXIT_OK, EXIT_REJECTED, EXIT_USAGE, EXIT_INFRA = 0, 1, 2, 3


def setup(full):
    K.REFERENCE.mkdir(parents=True, exist_ok=True)
    T.reference_lib()
    for fn in K.FUNCTIONS:
        d = K.REFERENCE / f"{fn}.digest"
        if not d.exists():
            print(f"building reference digests for {fn} (all 2^32 inputs; 6-15 min on 12 threads)", flush=True)
            subprocess.run([str(T.reference_digester()), fn, str(d), str(K.HOST_THREADS)], check=True)
        h = K.REFERENCE / f"hard-{fn}.txt"
        if not h.exists():
            p = subprocess.run([str(T.hardscan()), fn, str(1 << 27), "-18", "11"], capture_output=True, text=True, check=True)
            h.write_text(p.stdout)
            print(f"hard pool {fn}: {len(p.stdout.splitlines())} near-midpoint inputs", flush=True)
    # The digests' own hashes, written from the files (never by hand), for review and pinning.
    lines = [f"{T.sha(K.REFERENCE / f'{fn}.digest')}  reference/{fn}.digest" for fn in K.FUNCTIONS]
    (K.REFERENCE / "digests.sha256").write_text("\n".join(lines) + "\n")
    st = B.load()
    if "incumbent" not in st["entries"]:
        src = K.ROOT / "examples" / "incumbent.c"
        info = P.check_all(src)
        B.add_entry(st, "incumbent", src, {"sha256": T.sha(src), "normalised_sha256": P.normalised_hash(src),
                                           "bytes": info["bytes"], "seed": None})
        for b in K.BOARDS:
            B.crown(st, b, "incumbent", None, None)
        B.save(st)
        print("incumbent registered as champion of", ", ".join(K.BOARDS))
    if full:
        r = host_check(B.entry_path("incumbent"), quick=False, seed=1)
        print(json.dumps(r, indent=1))


def show_board():
    st = B.load()
    for b in K.BOARDS:
        v = st["boards"].get(b, {})
        s = v.get("score_at_takeover")
        print(f"{b:10s} {v.get('champion', '-'):20s} S={s:,.1f}" if s else f"{b:10s} {v.get('champion', '-')}")
    for h in st["history"][-10:]:
        print(" ", h["time"], h["board"], h["from"], "->", h["to"], f"S={h['score']:,.1f}" if h["score"] else "")


def summary(r):
    lines = [f"{r['entry']}: {r['status'].upper()}  (seed {r['seed']}, {r.get('seconds')} s)"]
    if r.get("stage"):
        lines.append(f"  stage: {r['stage']}")
        lines += [f"  - {x}" for x in r.get("reasons", [])[:12]]
        lines += [f"    {e}" for e in r.get("examples", [])[:5]]
    for b, c in (r.get("comparison") or {}).items():
        if c.get("champion"):
            lines.append(f"  {b:10s} entry S={c['entry_S']:>12,.1f}  champion {c['champion']} S={c['champion_S']:>12,.1f}"
                         f"  ratio {c['ratio']:.4f}{'  BEATS' if c['beats'] else ''}")
    for t, m in (r.get("measurements") or {}).items():
        f = m.get("functions", {})
        row = "  ".join(f"{fn} typ {f[fn]['typical']['mean']:,.0f} wide {f[fn]['wide']['mean']:,.0f} "
                        f"hard {f[fn]['hard']['mean']:,.0f} (p99.9 {f[fn]['hard']['p999']:,})" for fn in f)
        smp = m.get("sample") or {}
        lines.append(f"  {t:9s} {row}  stack {m.get('stack')} B  sample {smp.get('words')} words "
                     f"{smp.get('mismatches')} wrong  code {r['bytes'][t]} B")
    hc = r.get("host_check")
    if hc:
        for fn, x in hc["functions"].items():
            lines.append(f"  host check {fn}: {x.get('words_checked', 0):,} words, {x.get('mismatches')} wrong, "
                         f"{x.get('seconds')} s, complete={x.get('complete')}" + (f"\n    {x['sanitizer']}" if x.get("sanitizer") else "")
                         + (f"\n    examples {x['examples']}" if x.get("examples") else ""))
    return "\n".join(lines)


# --- stage commands -------------------------------------------------------------------------------

def _pairs(items, what):
    """BOARD=PATH arguments -> {board: Path}."""
    out = {}
    for item in items or []:
        board, sep, path = item.partition("=")
        if not sep or board not in K.BOARDS:
            raise SystemExit(f"--champion takes BOARD=FILE with BOARD one of {', '.join(K.BOARDS)}; got {item!r}")
        out[board] = Path(path)
    return out


def _load(path: Path) -> dict:
    try:
        return json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as e:
        raise ST.InfraError(f"cannot read report {path}: {e}")


def _chunks(text):
    if text is None:
        return None
    lo, sep, hi = text.partition(":")
    if not sep or not lo.isdigit() or not hi.isdigit():
        raise SystemExit(f"--chunks takes LO:HI (0 <= LO < HI <= {K.CHUNKS}); got {text!r}")
    return int(lo), int(hi)


def run_stage(a) -> dict:
    if a.cmd == "gate":
        known = []
        if a.known_hashes:
            known = [l.strip() for l in Path(a.known_hashes).read_text().splitlines() if l.strip()]
        return ST.gate(Path(a.file), known)
    if a.cmd == "measure":
        targets = a.targets.split(",") if a.targets else None
        if targets and set(targets) - set(K.TARGETS):
            raise SystemExit(f"--targets: one or more of {', '.join(K.TARGETS)}")
        return ST.measure(Path(a.file), a.seed, targets, sample=not a.no_sample)
    if a.cmd == "compare":
        files = _pairs(a.champion, "champion")
        return ST.compare(Path(a.file), a.seed, {b: files.get(b) for b in K.BOARDS})
    if a.cmd == "decide":
        reports = {b: _load(p) for b, p in _pairs(a.champion, "champion").items()}
        return ST.decide(_load(a.entry), {b: reports.get(b) for b in K.BOARDS})
    if a.cmd == "fullcheck":
        return ST.fullcheck(Path(a.file), a.function, chunks=_chunks(a.chunks), quick=a.quick, seed=a.seed,
                            threads=a.threads)
    if a.cmd == "targetcheck":
        return ST.targetcheck(Path(a.file), a.function, a.target, chunks=_chunks(a.chunks), jobs=a.jobs)
    if a.cmd == "merge":
        targets = a.require_targets.split(",") if a.require_targets else []
        if set(targets) - set(K.TARGETS):
            raise SystemExit(f"--require-targets: one or more of {', '.join(K.TARGETS)}")
        return ST.merge_fullchecks([_load(p) for p in a.reports], require_targets=targets)
    if a.cmd == "fingerprint":
        out = {"schema": ST.SCHEMA, "kind": "fingerprint", "competition": K.COMPETITION_SLUG, **FP.ids(),
               "mode": K.MODE, "production_problems": production.problems("measure") + production.problems("fullcheck")}
        if a.details:
            out["details"] = FP.details()
        return out
    raise AssertionError(a.cmd)


def _exit_code(rep: dict) -> int:
    v = rep.get("verdict")
    if rep.get("kind") == "compare":
        v = rep["measure"]["verdict"]
    return EXIT_REJECTED if v in ("rejected", "incomplete") else EXIT_OK


def stage_main(a):
    try:
        rep = run_stage(a)
        code = _exit_code(rep)
    except (ST.InfraError, SB.SandboxUnavailable) as e:
        rep, code = {"schema": ST.SCHEMA, "kind": "error", "error": type(e).__name__, "detail": str(e)}, EXIT_INFRA
    except SystemExit:
        raise
    except Exception as e:  # a harness bug or a broken host: never the entry's fault
        rep = {"schema": ST.SCHEMA, "kind": "error", "error": type(e).__name__, "detail": str(e),
               "traceback": traceback.format_exc()[-4000:]}
        code = EXIT_INFRA
    text = json.dumps(rep, indent=1, sort_keys=True) + "\n"
    if a.out:
        tmp = Path(a.out).with_suffix(".tmp")
        tmp.write_text(text)
        tmp.replace(a.out)
    else:
        sys.stdout.write(text)
    sys.exit(code)


def main():
    ap = argparse.ArgumentParser(prog="eik", description="Exact integer kernels: harness and stage commands")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("setup"); s.add_argument("--full", action="store_true")
    c = sub.add_parser("check"); c.add_argument("file")
    for name in ("evaluate", "submit"):
        e = sub.add_parser(name)
        e.add_argument("file")
        e.add_argument("--name")
        e.add_argument("--seed", type=int)
        e.add_argument("--quick", action="store_true", help="host check on 3%% of inputs (no takeover)")
        e.add_argument("--force-check", action="store_true", help="run the host check even without a win")
        e.add_argument("--json", action="store_true")
    sub.add_parser("board")

    stage = {}
    stage["gate"] = g = sub.add_parser("gate", help="static rules, builds, duplicate check")
    g.add_argument("file")
    g.add_argument("--known-hashes", help="file of normalised hashes of accepted entries, one per line")
    stage["measure"] = m = sub.add_parser("measure", help="instruction counts on one seed's inputs")
    m.add_argument("file")
    m.add_argument("--seed", type=int, required=True)
    m.add_argument("--targets", help=f"comma-separated subset of {','.join(K.TARGETS)}")
    m.add_argument("--no-sample", action="store_true", help="skip the stratified target sample (champions)")
    stage["compare"] = cp = sub.add_parser("compare", help="measure entry and champions on one seed, then decide")
    cp.add_argument("file")
    cp.add_argument("--seed", type=int, required=True)
    cp.add_argument("--champion", action="append", metavar="BOARD=FILE")
    stage["decide"] = d = sub.add_parser("decide", help="the takeover rule on measure reports")
    d.add_argument("--entry", required=True)
    d.add_argument("--champion", action="append", metavar="BOARD=REPORT")
    stage["fullcheck"] = f = sub.add_parser("fullcheck", help="every input of one function under UBSan + ASan")
    f.add_argument("file")
    f.add_argument("--function", required=True, choices=K.FUNCTIONS)
    f.add_argument("--chunks", help=f"LO:HI, a shard of the {K.CHUNKS} chunks of 2^20 words")
    f.add_argument("--quick", action="store_true", help="a seeded 3%% sample (development)")
    f.add_argument("--seed", type=int, default=1, help="chunk order and quick sample")
    f.add_argument("--threads", type=int)
    stage["targetcheck"] = tc = sub.add_parser("targetcheck", help="every input of one function on a target, in QEMU")
    tc.add_argument("file")
    tc.add_argument("--function", required=True, choices=K.FUNCTIONS)
    tc.add_argument("--target", required=True, choices=list(K.TARGETS))
    tc.add_argument("--chunks", help=f"LO:HI, a shard of the {K.CHUNKS} chunks of 2^20 words")
    tc.add_argument("--jobs", type=int, help="QEMU processes (default: one per core)")
    stage["merge"] = mg = sub.add_parser("merge", help="fullcheck and targetcheck shards -> one verdict")
    mg.add_argument("reports", nargs="+")
    mg.add_argument("--require-targets", help="targets whose every input must also be checked, e.g. rv32im,thumbv6m")
    stage["fingerprint"] = fp = sub.add_parser("fingerprint", help="verifier and measurement identities")
    fp.add_argument("--details", action="store_true")
    for p in stage.values():
        p.add_argument("--out", help="write the JSON report here (atomically) instead of stdout")

    a = ap.parse_args()
    if a.cmd in stage:
        stage_main(a)
    elif a.cmd == "setup":
        setup(a.full)
    elif a.cmd == "check":
        try:
            info = P.check_all(Path(a.file))
            print("PASS", json.dumps(info))
        except P.Reject as e:
            print(f"REJECT [{e.stage}]")
            for x in e.reasons:
                print("  -", x)
            sys.exit(1)
    elif a.cmd in ("evaluate", "submit"):
        name = a.name or Path(a.file).stem
        r = evaluate(Path(a.file), name, seed=a.seed, quick=a.quick, force_check=a.force_check, submit=a.cmd == "submit")
        print(json.dumps(r, indent=1) if a.json else summary(r))
        sys.exit(0 if r["status"] not in ("rejected",) else 1)
    elif a.cmd == "board":
        show_board()


if __name__ == "__main__":
    main()
