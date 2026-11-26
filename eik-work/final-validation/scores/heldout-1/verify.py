#!/usr/bin/env python3
"""Offline verifier for the held-out paired score comparison on seed 849230117.

Standard library only. Run from the repository root:
    python3 eik-work/final-validation/scores/heldout-1/verify.py [--root DIR]
It re-hashes every retained artifact, binds the measured sources and the pinned kit files to the
repository, recomputes every S, overall S and ratio from the raw per-class instruction means, checks
that only reports with equal seed / inputs_sha256 / kit / measurement identity are paired, and rejects
a status or eligibility claim the evidence does not support.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = "eik-work/final-validation/scores/heldout-1"
SEED = 849230117
CAND_SHA = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
ID50_SHA = "88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3"
CAND_PATH = "entry.c"
ID50_PATH = "eik-work/baselines/former-50/entry.c"
KIT = "eik-work/toolkit/kit"
BOARDS = ("rv32im", "thumbv6m", "overall")
SCORED = ("rv32im", "thumbv6m")
TARGETS = ("rv32im", "thumbv6m", "thumbv7em")
FUNCTIONS = ("sigmoid", "tanh", "exp")
BAR = 0.97
TOL = 1e-12


class Fail(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise Fail(msg)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        raise Fail(f"cannot read {path}: {e}")


def close(a, b):
    return isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) <= TOL * max(abs(a), abs(b), 1.0)


def score(target, nbytes, k):
    """The kit's formula (eik/score.py), from the raw per-class statistics of one target."""
    tf, ts, te = k["tail"]
    su, se = k["size"]
    logs = []
    for fn in k["functions"]:
        d = target["functions"][fn]
        base = sum(w * math.log(d[s]["mean"]) for s, w in k["sets"].items())
        tail = (1 + max(0.0, d["hard"]["p999"] - tf * d["typical"]["mean"]) / ts) ** te
        logs.append(base + math.log(tail))
    return math.exp(sum(logs) / len(logs)) * (1 + nbytes / su) ** se


def norm(rep, what):
    """A measure report or an evaluate report -> one common shape."""
    targets = rep.get("targets") if "targets" in rep else rep.get("measurements")
    need(isinstance(targets, dict) and targets, f"{what}: no per-target measurements")
    for key in ("sha256", "seed", "inputs_sha256", "fingerprint", "hard_pool", "bytes", "scores"):
        need(key in rep, f"{what}: missing {key}")
    return {"what": what, "sha256": rep["sha256"], "seed": rep["seed"], "inputs_sha256": rep["inputs_sha256"],
            "fingerprint": rep["fingerprint"], "hard_pool": rep["hard_pool"], "bytes": rep["bytes"],
            "scores": rep["scores"], "targets": targets, "images": rep.get("images")}


def check_report(r, k, targets, sampled):
    """Populations, correctness facts and S of one normalised report; returns the recomputed S."""
    w = r["what"]
    need(r["seed"] == SEED, f"{w}: seed {r['seed']} is not {SEED}")
    need(set(r["targets"]) == set(targets), f"{w}: targets {sorted(r['targets'])} != {sorted(targets)}")
    out = {}
    for t in targets:
        m = r["targets"][t]
        need(not m.get("timeout"), f"{w}/{t}: emulator timeout")
        need(m.get("wrong") == [], f"{w}/{t}: wrong outputs on scored inputs")
        need(set(m["functions"]) == set(k["functions"]), f"{w}/{t}: functions differ")
        for fn in k["functions"]:
            need(set(m["functions"][fn]) == set(k["sets"]), f"{w}/{t}/{fn}: input classes differ")
            for s, n in k["set_sizes"].items():
                c = m["functions"][fn][s]
                need(c["n"] == n, f"{w}/{t}/{fn}/{s}: population {c['n']} is not the full {n}")
                need(0 < c["mean"] <= c["max"] and c["median"] <= c["p999"] <= c["max"], f"{w}/{t}/{fn}/{s}: inconsistent statistics")
        if sampled:
            smp = m.get("sample")
            need(isinstance(smp, dict), f"{w}/{t}: target sample missing")
            need(smp["words"] == k["target_sample"] * len(k["functions"]), f"{w}/{t}: target sample is not the full size")
            need(smp["mismatches"] == 0 and smp["examples"] == [], f"{w}/{t}: target sample mismatches")
        else:
            need(m.get("sample") is None, f"{w}/{t}: unexpected sample")
        need(isinstance(m.get("stack"), int) and m["stack"] <= 8192, f"{w}/{t}: stack")
        s = score(m, r["bytes"][t], k)
        need(close(s, r["scores"][t]["S"]), f"{w}/{t}: reported S {r['scores'][t]['S']} != recomputed {s}")
        need(r["scores"][t]["bytes"] == r["bytes"][t], f"{w}/{t}: size differs")
        out[t] = s
    out["overall"] = math.sqrt(out["rv32im"] * out["thumbv6m"])
    need(close(out["overall"], r["scores"]["overall"]["S"]), f"{w}: overall S is not sqrt(rv32im * thumbv6m)")
    return out


def paired(a, b):
    """Reports may be paired only on equal seed, inputs, hard pools, kit and measurement identity."""
    for key in ("seed", "inputs_sha256", "hard_pool", "fingerprint"):
        need(a[key] == b[key], f"{a['what']} and {b['what']} differ in {key}: not comparable")


def main():
    root = Path.cwd()
    if "--root" in sys.argv:
        root = Path(sys.argv[sys.argv.index("--root") + 1]).resolve()
    need((root / REL / "verify.py").exists(), f"run from the repository root ({REL} not found under {root})")
    here = root / REL
    result = load(here / "result.json")
    scores = load(here / "scores.json")

    # 1. artifacts: every listed file is present with its hash; nothing unlisted is in the directory
    arts = result.get("artifacts")
    need(isinstance(arts, dict) and arts, "result.json lists no artifacts")
    for rel, digest in arts.items():
        p = root / rel
        need(p.is_file(), f"missing artifact {rel}")
        need(sha(p) == digest, f"artifact {rel} does not match its recorded sha256 (tampered or replaced)")
    present = {f"{REL}/{p.relative_to(here).as_posix()}" for p in here.rglob("*")
               if p.is_file() and "__pycache__" not in p.parts}
    own = {a for a in arts if a.startswith(REL + "/")}
    need(present - {f"{REL}/result.json"} == own, "files in the directory and the artifact list differ: "
         + ", ".join(sorted((present - {f'{REL}/result.json'}) ^ own)[:6]))
    for must in ("scores.json", "scores.md", "verify.py", "raw/cand/evaluate-849230117.stdout",
                 "raw/id50/evaluate-849230117.stdout", "raw/cand/historical-compare-id50.stdout",
                 "raw/id50/measure-849230117.stdout", "raw/cand/fingerprint.stdout", "raw/cand/commands.json",
                 "raw/id50/commands.json", "current-references.json"):
        need(f"{REL}/{must}" in arts, f"required evidence {must} is not listed")

    # 2. the measured sources are the frozen candidate and the unchanged former champion 50
    need(sha(root / CAND_PATH) == CAND_SHA, "root entry.c is not the frozen candidate")
    need(sha(root / ID50_PATH) == ID50_SHA, "eik-work/baselines/former-50/entry.c is not the id50 source")
    src = result.get("sources", {})
    need(src.get("candidate", {}).get("sha256") == CAND_SHA and src["candidate"].get("path") == CAND_PATH, "result.json: candidate identity")
    need(src.get("id50", {}).get("sha256") == ID50_SHA and src["id50"].get("path") == ID50_PATH, "result.json: id50 identity")

    # 3. tool identity: fingerprint, and every kit file it names is the pinned file in this repository
    fp = load(here / "raw/cand/fingerprint.stdout")
    need(fp == load(here / "raw/id50/fingerprint.stdout"), "the two cases ran different kits")
    ident = {k: fp[k] for k in ("verifier", "measurement", "sandbox")}
    k = fp["details"]["measurement"]["constants"]
    need(k["sets"] == {"typical": 0.55, "wide": 0.30, "hard": 0.10, "uniform": 0.05}, "class weights changed")
    need(k["set_sizes"] == {"typical": 2000, "wide": 1000, "hard": 300, "uniform": 1000}, "populations are not full size")
    need(k["target_sample"] == 32768 and k["hard_fresh"] is True and k["takeover_ratio"] == BAR, "sample/hard pool/bar constants changed")
    need(k["tail"] == [20, 1e6, 0.1] and k["size"] == [65536, 0.5] and tuple(k["functions"]) == FUNCTIONS, "score constants changed")
    for part in ("measurement", "verifier"):
        for rel, digest in fp["details"][part]["files"].items():
            p = root / KIT / rel
            need(p.is_file() and sha(p) == digest, f"kit file {rel} differs from the fingerprinted one")
    manifest = load(root / "eik-work/toolkit/manifest.json")
    need(manifest["fingerprint"]["measurement"] == ident["measurement"] and manifest["fingerprint"]["verifier"] == ident["verifier"],
         "fingerprint is not the toolkit's pinned identity")
    need(result.get("tools", {}).get("fingerprint") == ident, "result.json: tool fingerprint")
    need(result["tools"].get("versions") == fp["details"]["tools"], "result.json: tool versions")

    # 4. commands: recorded exits, logs bound by hash, the runner's own records agree
    listed = []
    for case, source in (("cand", CAND_SHA), ("id50", ID50_SHA)):
        cmds = load(here / f"raw/{case}/commands.json")
        labels = [c["label"] for c in cmds]
        need(len(set(labels)) == len(labels), f"{case}: duplicate command labels")
        for c in cmds:
            need(c["case"] == case, f"{case}: foreign command record")
            for stream in ("stdout", "stderr"):
                need(sha(here / c[stream]) == c[f"{stream}_sha256"], f"{case}/{c['label']}: {stream} does not match its record")
            need(c["exit_code"] == 0 and c["timed_out"] is False, f"{case}/{c['label']}: exit {c['exit_code']}, timed_out {c['timed_out']}")
            need(c["runner_record"], f"{case}/{c['label']}: the runner's own record is missing")
            rr = load(here / c["runner_record"])
            need(rr["exit_code"] == 0 and rr["stdout_sha256"] == c["stdout_sha256"] and rr["stderr_sha256"] == c["stderr_sha256"],
                 f"{case}/{c['label']}: runner record disagrees")
            need(rr["argv"][1:3] == ["-m", "eik"] and rr["argv"][3:4] == c["argv"][5:6], f"{case}/{c['label']}: runner argv")
            if rr["source_sha256"] is not None:
                need(rr["source_sha256"] == source, f"{case}/{c['label']}: measured a different source")
            listed.append(c)
        need({"setup", "fingerprint", "check", "evaluate-849230117"} <= set(labels), f"{case}: required commands missing")
        ev = next(c for c in cmds if c["label"] == "evaluate-849230117")
        need(ev["argv"][5:] == ["evaluate", CAND_PATH if case == "cand" else ID50_PATH, "--quick", "--json", "--seed", str(SEED)],
             f"{case}: evaluate was not run as eik evaluate --quick --json --seed {SEED}")
        need(ev["cap_seconds"] == 600 and ev["seconds"] < 600, f"{case}: evaluate cap")
        need((here / f"raw/{case}/check.stdout").read_text().startswith("PASS "), f"{case}: static check did not pass")
    need(result.get("commands") == listed + load(here / "raw/setup-commands.json"), "result.json: commands differ from the retained records")
    need((here / "raw/bootstrap.exit").read_text().strip() == "0", "toolkit bootstrap did not pass")
    cmp_cmd = next(c for c in listed if c["label"] == "historical-compare-id50")
    need(cmp_cmd["argv"][5:] == ["compare", CAND_PATH, "--seed", str(SEED)] + [x for b in BOARDS for x in ("--champion", f"{b}={ID50_PATH}")],
         "compare was not run with explicit --champion BOARD=FILE for id50")

    # 5. raw reports
    ev_c = load(here / "raw/cand/evaluate-849230117.stdout")
    ev_i = load(here / "raw/id50/evaluate-849230117.stdout")
    cmp_ = load(here / "raw/cand/historical-compare-id50.stdout")
    ms_i = load(here / "raw/id50/measure-849230117.stdout")
    need(cmp_.get("kind") == "compare" and cmp_["measure"].get("verdict") == "passed", "compare: entry measurement did not pass")
    need(list(cmp_["champions"]) == [ID50_SHA] and cmp_["champions"][ID50_SHA]["verdict"] == "passed", "compare: champion is not id50")
    need(ms_i.get("kind") == "measure" and ms_i.get("verdict") == "passed" and ms_i.get("sampled") is True, "id50 measure did not pass")
    A = norm(ev_c, "candidate evaluate")
    B = norm(cmp_["measure"], "candidate compare/measure")
    C = norm(cmp_["champions"][ID50_SHA], "id50 compare/champion")
    Dn = norm(ev_i, "id50 evaluate")
    E = norm(ms_i, "id50 measure")
    for r, digest in ((A, CAND_SHA), (B, CAND_SHA), (C, ID50_SHA), (Dn, ID50_SHA), (E, ID50_SHA)):
        need(r["sha256"] == digest, f"{r['what']}: source hash")
        need(r["fingerprint"] == ident, f"{r['what']}: kit/measurement identity differs from the fingerprint")
        paired(A, r)
    sa = check_report(A, k, TARGETS, True)
    sb = check_report(B, k, TARGETS, True)
    sc = check_report(C, k, SCORED, False)
    sd = check_report(Dn, k, TARGETS, True)
    se = check_report(E, k, TARGETS, True)
    need(A["targets"] == B["targets"] and A["bytes"] == B["bytes"], "candidate: evaluate and compare measurements differ")
    need(Dn["targets"] == E["targets"] and Dn["bytes"] == E["bytes"], "id50: evaluate and measure differ")
    for t in SCORED:
        need(C["targets"][t]["functions"] == E["targets"][t]["functions"], f"id50: compare and measure differ on {t}")
    need(sa == sb and sd == se and all(sc[b] == se[b] for b in BOARDS), "repeat measurements give different S")

    # hard pools: fresh (hardscan), retained, identical in both cases, sizes as reported
    hp = A["hard_pool"]
    need(hp["source"] == "hardscan" and hp["samples"] == k["hard_samples"] and hp["threshold_log2_ulps"] == k["hard_threshold"], "hard pool is not the fresh pinned scan")
    for fn in FUNCTIONS:
        files = [sorted((here / f"raw/{case}/hard").glob(f"hardscan-*-{hp['samples']}-{SEED}-{fn}.txt")) for case in ("cand", "id50")]
        need(all(len(f) == 1 for f in files), f"hard pool file for {fn} missing")
        need(files[0][0].read_bytes() == files[1][0].read_bytes() and files[0][0].name == files[1][0].name, f"hard pool {fn} differs between cases")
        lines = [l for l in files[0][0].read_text().splitlines() if l.strip()]
        need(len(lines) == hp["sizes"][fn], f"hard pool {fn}: {len(lines)} lines, report says {hp['sizes'][fn]}")
        rec = scores["hard_pool"]["files"][fn]
        need(rec["sha256"] == sha(files[0][0]) and rec["lines"] == len(lines), f"scores.json: hard pool {fn}")

    # quick host checks inside evaluate (3% sample: not exhaustive correctness)
    for rep, w in ((ev_c, "candidate"), (ev_i, "id50")):
        need(rep["status"] == "would-take-over-after-full-check" and rep["seed"] == SEED, f"{w}: evaluate status {rep['status']}")
        hc = rep["host_check"]
        need(hc["ok"] is True and hc["quick"] is True and hc["complete"] is False, f"{w}: quick host check")
        for fn in FUNCTIONS:
            f = hc["functions"][fn]
            need(f["verdict"] == "passed" and f["mismatches"] == 0 and f["words_checked"] == 128 << 20, f"{w}: quick host check {fn}")
        for b in BOARDS:
            need(rep["comparison"][b]["champion"] == "incumbent", f"{w}: evaluate compared against something other than the kit incumbent")
    for b in BOARDS:
        need(ev_c["comparison"][b]["champion_S"] == ev_i["comparison"][b]["champion_S"], "kit incumbent S differs between cases")

    # 6. scores.json against the recomputation
    need(scores["seed"] == SEED and scores["inputs_sha256"] == A["inputs_sha256"] and scores["fingerprint"] == ident, "scores.json: pairing identity")
    need(scores["takeover_ratio"] == BAR, "scores.json: bar")
    for name, s, r in (("candidate", sb, B), ("id50", se, E)):
        e = scores["entries"][name]
        need(e["sha256"] == r["sha256"] and e["bytes"] == r["bytes"], f"scores.json: {name} identity/sizes")
        for key in (*TARGETS, "overall"):
            need(close(e["S"][key], s[key]), f"scores.json: {name} S[{key}] does not match the raw data")
        need(e["classes"] == {t: r["targets"][t]["functions"] for t in TARGETS}, f"scores.json: {name} class statistics")
        need(e["sample"] == {t: {"words": r["targets"][t]["sample"]["words"], "mismatches": 0} for t in TARGETS}, f"scores.json: {name} samples")
        need(e["wrong_outputs"] == {t: 0 for t in TARGETS}, f"scores.json: {name} wrong outputs")
        need(e["stack"] == {t: r["targets"][t]["stack"] for t in TARGETS}, f"scores.json: {name} stack")
        need(e["tail_p999_hard"] == {t: {fn: r["targets"][t]["functions"][fn]["hard"]["p999"] for fn in FUNCTIONS} for t in TARGETS}, f"scores.json: {name} tails")
    dec = cmp_["decision"]["boards"]
    any_id50 = False
    for b in BOARDS:
        row = scores["id50_comparison"][b]
        ratio = sb[b] / se[b]
        need(close(row["candidate_S"], sb[b]) and close(row["id50_S"], se[b]) and close(row["ratio"], ratio), f"scores.json: id50 ratio on {b}")
        need(row["le_0970"] is (ratio <= BAR), f"scores.json: id50 <=0.970 flag on {b}")
        need(close(dec[b]["ratio"], ratio) and dec[b]["beats"] is (ratio <= BAR) and dec[b]["champion_sha256"] == ID50_SHA, f"kit decision on {b} disagrees")
        any_id50 |= ratio <= BAR
        inc = scores["kit_incumbent"]["S"][b]
        need(inc == ev_c["comparison"][b]["champion_S"], f"scores.json: kit incumbent S on {b}")
    need(close(scores["id50_comparison"]["overall"]["id50_S"], math.sqrt(se["rv32im"] * se["thumbv6m"])), "overall denominator is not from the same source")

    # 7. current board references: none retained => null S/ratio and undetermined eligibility
    refs = load(here / "current-references.json")
    cur = scores["current_reference"]
    need(set(cur) == set(BOARDS) and set(refs["boards"]) == set(BOARDS), "current references: boards")
    for b in BOARDS:
        ref, row = refs["boards"][b], cur[b]
        need(ref["reference_path"] is None and ref["source_status"] == "withheld", f"{b}: a current reference is recorded as available but was not measured")
        need(row["submission"] == ref["champion_submission"] and row["declared_source_sha256"] == ref["declared_source_sha256"], f"{b}: current reference identity")
        need(row["reference_available"] is False and row["current_S"] is None and row["ratio"] is None and row["le_0970"] is None
             and row["eligibility"] == "undetermined", f"{b}: a current S, ratio or eligibility is claimed without a measured reference")
        m = manifest["entries"][f"current-{b}"]
        need(m["sha256"] == ref["declared_source_sha256"] and m["submission"] == ref["champion_submission"] and m["path"] is None,
             f"{b}: toolkit manifest disagrees about the current reference")
    snap = root / refs["snapshot_path"]
    if snap.is_file() and sha(snap) != refs["snapshot_file_sha256"]:
        print("note: the board snapshot file changed after this comparison; the retained extract describes "
              f"{refs['snapshot_utc']}")

    # 8. status: success is unsupported here
    need(result.get("status") in ("pass", "fail", "incomplete"), "result.json: status")
    need(result["status"] != "pass", "status pass is unsupported: no current-board reference was measured and "
         "exhaustive correctness is not established by this item")
    need(result["status"] == "incomplete", "with every current reference missing the outcome is incomplete")
    need(result.get("boards_candidate_would_take") == [], "result.json claims a board without a measured current reference")
    need(result.get("measured", {}).get("id50_any_le_0970") is any_id50, "result.json: id50 summary flag")
    need(isinstance(result.get("gaps"), list) and len(result["gaps"]) >= 3, "result.json: gaps must be stated")
    need(result.get("seed") == SEED and result.get("inputs_sha256") == A["inputs_sha256"], "result.json: seed/inputs")
    need(result["measured"].get("candidate_S") == scores["entries"]["candidate"]["S"]
         and result["measured"].get("id50_S") == scores["entries"]["id50"]["S"]
         and result["measured"].get("id50_ratio") == {b: scores["id50_comparison"][b]["ratio"] for b in BOARDS}, "result.json: measured facts differ from scores.json")
    print(f"verify: OK status={result['status']} seed={SEED} inputs={A['inputs_sha256'][:12]} "
          + " ".join(f"{b}: cand {sb[b]:.6f} / id50 {se[b]:.6f} = {sb[b] / se[b]:.6f}" for b in BOARDS)
          + " ; current references: none available (ratios null, eligibility undetermined)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fail as e:
        print(f"verify: FAIL: {e}")
        sys.exit(1)
    except (KeyError, TypeError, IndexError, StopIteration, OSError, ValueError) as e:
        print(f"verify: FAIL: malformed evidence: {type(e).__name__}: {e}")
        sys.exit(1)
