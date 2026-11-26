"""One local evaluation, end to end, built from the same stages the validator runs (eik/stages.py):

  1. gate: static policy (text, AST, object files per target) and the duplicate check against the
     entries accepted locally                                                  -> reject early
  2. compare: on each target, instruction counts on fresh inputs, every output checked, peak stack,
     and a stratified sample of all 2^32 words batch-checked; the board champions are re-measured
     on the same inputs (same seed), so the comparison has no sampling noise between them
  3. decide: candidate boards where S <= 0.97 x champion
  4. fullcheck: all 2^32 inputs per function on the host under UBSan + ASan, against the reference
     digests (only for a candidate, or when forced)
  5. takeover of every candidate board whose full check passed (submit only; state/boards.json)
"""
import json
import secrets
import time
from pathlib import Path

from . import board as B
from . import config as K
from . import stages as ST


def host_check(src: Path, quick: bool, seed: int):
    """The full check of every function, failing fast; in the shape the local report has always had."""
    res = {}
    for fn in K.FUNCTIONS:
        r = ST.fullcheck(src, fn, quick=quick, seed=seed)
        res[fn] = {k: r.get(k) for k in ("verdict", "stage", "complete", "words_checked", "mismatches", "seconds",
                                         "examples", "sanitizer") if r.get(k) is not None}
        if r["verdict"] != "passed":
            break
    ok = len(res) == len(K.FUNCTIONS) and all(r["verdict"] == "passed" for r in res.values())
    complete = ok and all(r.get("complete") for r in res.values())
    return {"ok": ok, "complete": complete, "quick": quick, "functions": res}


def evaluate(src: Path, name: str, seed=None, quick=False, force_check=False, submit=False):
    src = Path(src).resolve()
    seed = seed if seed is not None else secrets.randbits(32)
    st = B.load()
    rep = {"entry": name, "file": str(src), "seed": seed, "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "status": None}
    t0 = time.time()

    def done(status, **kw):
        rep.update(status=status, seconds=round(time.time() - t0, 1), **kw)
        K.RESULTS.mkdir(parents=True, exist_ok=True)
        (K.RESULTS / f"{time.strftime('%Y%m%d-%H%M%S')}-{name}.json").write_text(json.dumps(rep, indent=1))
        return rep

    # 1. gate
    known = {m["normalised_sha256"] for other, m in st["entries"].items() if other != name}
    g = ST.gate(src, known)
    rep.update(sha256=g["sha256"], fingerprint=g["fingerprint"])
    if g["verdict"] != "accepted":
        return done("rejected", stage=g["stage"], reasons=g["reasons"])
    rep.update(bytes=g["bytes"], normalised_sha256=g["normalised_sha256"])

    # 2-3. measure the entry and the champions on one seed, then decide
    champs = B.champions(st)
    c = ST.compare(src, seed, {b: (B.entry_path(champs[b]) if b in champs else None) for b in K.BOARDS})
    m = c["measure"]
    rep.update(hard_pool=m["hard_pool"], inputs_sha256=m["inputs_sha256"], measurements=m.get("targets", {}))
    if m["verdict"] != "passed":
        return done("rejected", stage=m["stage"], reasons=m["reasons"], examples=m.get("examples", []))
    d = c["decision"]
    names = {st["entries"][e]["sha256"]: e for e in st["entries"]}
    rep["scores"] = m["scores"]
    rep["comparison"] = {b: ({"champion": None} if v["champion_sha256"] is None else
                             {"champion": names.get(v["champion_sha256"], v["champion_sha256"][:12]),
                              "champion_S": v["champion_S"], "entry_S": v["entry_S"], "ratio": v["ratio"],
                              "beats": v["beats"]})
                         for b, v in d["boards"].items()}
    cand = d["candidate_boards"]
    rep["candidate_boards"] = cand

    # 4. full check on the host
    if cand or force_check:
        hc = host_check(src, quick, seed)
        rep["host_check"] = hc
        if not hc["ok"]:
            bad = next(r for r in hc["functions"].values() if r["verdict"] != "passed")
            return done("rejected", stage="host-check", reasons=[
                f"{bad['stage']}: wrong output or undefined behaviour found by the full check on the host"])
    if not cand:
        return done("valid-no-takeover" if submit else "evaluated")

    # 5. takeover
    if not rep["host_check"]["complete"]:
        return done("would-take-over-after-full-check", boards=cand)
    if submit:
        meta = {"sha256": g["sha256"], "normalised_sha256": g["normalised_sha256"], "bytes": g["bytes"], "seed": seed}
        B.add_entry(st, name, src, meta)
        for b in cand:
            B.crown(st, b, name, m["scores"][b]["S"], seed)
        B.save(st)
        return done("took-over", boards=cand)
    return done("would-take-over", boards=cand)
