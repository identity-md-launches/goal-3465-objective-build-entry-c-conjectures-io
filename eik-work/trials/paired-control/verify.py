#!/usr/bin/env python3
"""Paired two-seed control/trial packets for the e03 kernel trials (standard library only).

    python3 eik-work/trials/paired-control/verify.py DIR
        Verify one packet: the control (eik-work/trials/paired-control) or a trial
        (eik-work/trials/<key>). A trial is checked against this control, which is verified first.

    python3 eik-work/trials/paired-control/verify.py assemble DIR --logs LOGS --source PATH
            [--kind trial|control] [--status measured|duplicate|rejected] [--note TEXT]
        Copy raw run.py logs (LOGS = <work>/cases/<case>/logs) into DIR and write DIR/packet.json
        with the index recomputed from those logs, then verify it. Refuses to overwrite packet.json.

See README.md in this directory for the layout and fields.
"""
import json
import math
from hashlib import sha256
from pathlib import Path
import re
import shutil
import sys

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TOOLKIT = REPO / "eik-work/toolkit"
SCHEMA = "eik-paired-1"
SEEDS = (1874435642, 1947282751)
CONTROL_SOURCE = "eik-work/baselines/former-50/entry.c"
CONTROL_SHA256 = "88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3"
TARGETS = ("rv32im", "thumbv6m", "thumbv7em")
BOARDS = ("rv32im", "thumbv6m", "overall")
FUNCTIONS = ("sigmoid", "tanh", "exp")
MEASURED_STATUSES = {"evaluated", "would-take-over-after-full-check", "would-take-over", "measured-by-stages"}
PROBES = re.compile(r"__(riscv|arm|ARM_\w+|thumb\w*|clang\w*|GNUC\w*|x86_64|i386|aarch64|SANITIZE_\w+|"
                    r"SIZEOF_\w+|LP64|ILP32|ORDER_\w+|BYTE_ORDER|has_\w+)__?")


class Bad(ValueError):
    pass


def require(cond, msg):
    if not cond:
        raise Bad(msg)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def positive(v):
    return type(v) in (int, float) and math.isfinite(v) and v > 0


def inside(root, rel):
    p = (root / rel)
    require(p.resolve().is_relative_to(root.resolve()) and p.is_file(), f"missing or out-of-scope file {rel}")
    return p


def manifest():
    return read_json(TOOLKIT / "manifest.json")


def identity(component):
    return sha256(json.dumps(component, sort_keys=True, default=list).encode()).hexdigest()


def evaluator_ok(fp, d, m):
    """Pinned verifier/measurement IDs, or a retained fingerprint log showing only the host GCC line differs."""
    pinned = m["fingerprint"]
    if all(fp[f] == pinned[f] for f in ("verifier", "measurement")):
        return
    rec, out = log(d, "fingerprint", "fingerprint", None)
    require(rec["exit_code"] == 0, "fingerprint run failed")
    rep = json.loads(out)
    require(not rep["production_problems"], "evaluator production problems")
    require(all(fp[f] == rep[f] for f in ("verifier", "measurement")), "report fingerprint differs from fingerprint log")
    for f in ("verifier", "measurement"):
        require(identity(rep["details"][f]) == rep[f], f"fingerprint {f} details inconsistent")
        part = json.loads(json.dumps(rep["details"][f]))
        require(str(part["tools"]["host_cc"]).startswith("gcc "), "host compiler is not GCC")
        part["tools"]["host_cc"] = pinned["details"][f]["tools"]["host_cc"]
        require(identity(part) == pinned[f], f"{f} fingerprint differs beyond the host compiler line")


def log(d, label, command, source_path):
    """Recompute hashes of one raw run.py record and return (record, stdout text)."""
    rec = read_json(inside(d, f"{label}.json"))
    out, err = inside(d, f"{label}.stdout"), inside(d, f"{label}.stderr")
    require(rec["stdout_sha256"] == digest(out) and rec["stderr_sha256"] == digest(err), f"{label}: log hash mismatch")
    argv = rec["argv"]
    require(argv[1:4] == ["-m", "eik", command], f"{label}: not an eik {command} run")
    require(type(rec["exit_code"]) is int and positive(rec["seconds"]), f"{label}: invalid exit or runtime")
    if source_path is not None:
        require(argv[4] == "$REPO/" + source_path, f"{label}: ran on {argv[4]}, not {source_path}")
        require(rec["source_sha256"] == digest(REPO / source_path), f"{label}: source bytes differ from the run")
    else:
        require(argv[1:] == ["-m", "eik", "fingerprint", "--details"], "fingerprint log is not --details")
    packet_run = PACKET_RUNS.get(label)
    require(packet_run is not None, f"{label}: command not recorded in packet.json runs")
    require(packet_run["exit_code"] == rec["exit_code"], f"{label}: recorded exit differs")
    files = {f"{label}.{e}": digest(d / f"{label}.{e}") for e in ("json", "stdout", "stderr")}
    require(packet_run["files"] == files, f"{label}: packet file hashes differ")
    if source_path is not None:
        require(source_path in packet_run["command"], f"{label}: command lacks the source path")
    return rec, out.read_text()


PACKET_RUNS = {}


def evaluate_args(rec, seed):
    args = rec["argv"][5:]
    require("--quick" in args and "--json" in args and args.count("--seed") == 1
            and args[args.index("--seed") + 1] == str(seed), f"evaluate-{seed}: not --quick --json --seed {seed}")
    require(not any(a in args for a in ("--champion", "--force-check")) and str(seed) in PACKET_RUNS[f"evaluate-{seed}"]["command"],
            f"evaluate-{seed}: altered scorer settings or missing seed in command")


def stage_report(d, seed, src, gate, allow_reject=False):
    """The evaluation of one seed built from the kit stages `evaluate` itself runs, for hosts where the
    incumbent champion's re-measurement cannot finish (it decides only the incumbent ratio, never S):
    measure-SEED  = `eik measure SRC --seed SEED` (every target, with the stratified target sample), and
    fullcheck-SEED-FN = `eik fullcheck SRC --function FN --quick --seed SEED` (evaluate's quick host check).
    Returns an evaluate-shaped report (status "measured-by-stages", or "rejected")."""
    rec, out = log(d, f"measure-{seed}", "measure", src)
    args = rec["argv"][5:]
    require(args == ["--seed", str(seed)] and str(seed) in PACKET_RUNS[f"measure-{seed}"]["command"],
            f"measure-{seed}: must be exactly --seed {seed} (all targets, with sample)")
    require(rec["exit_code"] in (0, 1), f"measure-{seed}: infrastructure error (exit {rec['exit_code']})")
    mrep = json.loads(out)
    require(mrep["kind"] == "measure" and mrep["seed"] == seed and mrep["sha256"] == digest(REPO / src)
            and mrep["sampled"] is True, f"measure-{seed}: other seed/source or no sample")
    rep = {"seed": seed, "sha256": mrep["sha256"], "fingerprint": mrep["fingerprint"],
           "inputs_sha256": mrep.get("inputs_sha256"), "hard_pool": mrep.get("hard_pool"),
           "measurements": mrep.get("targets", {}), "bytes": mrep.get("bytes"),
           "normalised_sha256": gate.get("normalised_sha256"), "comparison": None}
    if rec["exit_code"] == 1 or mrep["verdict"] != "passed":
        require(allow_reject and rec["exit_code"] == 1 and mrep["verdict"] == "rejected" and mrep["stage"],
                f"measure-{seed}: not passed")
        rep.update(status="rejected", stage=mrep["stage"], reasons=mrep["reasons"], examples=mrep.get("examples", []))
        return rep
    rep["scores"] = mrep["scores"]
    host = {"ok": True, "quick": True, "complete": False, "functions": {}}
    for fn in FUNCTIONS:
        frec, fout = log(d, f"fullcheck-{seed}-{fn}", "fullcheck", src)
        require(frec["argv"][5:] == ["--function", fn, "--quick", "--seed", str(seed)],
                f"fullcheck-{seed}-{fn}: must be --function {fn} --quick --seed {seed}")
        require(frec["exit_code"] in (0, 1), f"fullcheck-{seed}-{fn}: infrastructure error")
        f = json.loads(fout)
        require(f["kind"] == "fullcheck" and f["function"] == fn and f["sha256"] == rep["sha256"] and f["quick"] is True
                and f["fingerprint"] == rep["fingerprint"], f"fullcheck-{seed}-{fn}: other run")
        host["functions"][fn] = f
        if f["verdict"] != "passed":
            host["ok"] = False
            require(allow_reject and frec["exit_code"] == 1, f"fullcheck-{seed}-{fn}: {f['verdict']}")
            rep.update(status="rejected", stage="host-check", reasons=[f"{f['stage']}: {f['reasons']}"],
                       examples=f.get("examples", []))
            return rep
    rep.update(host_check=host, status="measured-by-stages")
    return rep


def seed_report(d, seed, src, gate, allow_reject=False):
    """One seed's report: the `evaluate-SEED` run when the packet has one, else the stage form."""
    if f"evaluate-{seed}" in PACKET_RUNS:
        rec, out = log(d, f"evaluate-{seed}", "evaluate", src)
        evaluate_args(rec, seed)
        require(rec["exit_code"] in ((0, 1) if allow_reject else (0,)), f"evaluate-{seed}: exit {rec['exit_code']}")
        rep = json.loads(out)
        require(rep.get("seed") == seed and rep.get("sha256") == digest(REPO / src), f"evaluate-{seed}: other seed/source")
        if rec["exit_code"] == 1:
            require(rep["status"] == "rejected" and rep.get("stage") and rep.get("reasons"), f"evaluate-{seed}: rejection lacks stage")
        return rep
    return stage_report(d, seed, src, gate, allow_reject)


def score_row(rep, static, gate, m):
    """Recompute and check every scored number of one measured evaluation; return its index row."""
    c = m["fingerprint"]["details"]["measurement"]["constants"]
    require(rep["status"] in MEASURED_STATUSES, f"not a measured status: {rep['status']}")
    require(re.fullmatch("[0-9a-f]{64}", rep["inputs_sha256"] or "") and rep["normalised_sha256"] == gate["normalised_sha256"],
            "missing inputs digest or normalised hash differs from gate")
    require(rep["bytes"] == static["bytes"] == gate["bytes"], "bytes differ between check, gate and evaluate")
    hp = rep["hard_pool"]
    require(hp["source"] == "hardscan" and hp["samples"] == c["hard_samples"] and hp["threshold_log2_ulps"] == c["hard_threshold"]
            and set(hp["sizes"]) == set(FUNCTIONS) and all(type(n) is int and n > 0 for n in hp["sizes"].values()),
            "altered or incomplete hard pools")
    meas, scores = rep["measurements"], rep["scores"]
    require(set(meas) == set(TARGETS) and set(scores) == set(TARGETS) | {"overall"}, "incomplete targets")
    factor, scale, exponent = c["tail"]
    unit, sexp = c["size"]
    row = {"seed": rep["seed"], "inputs_sha256": rep["inputs_sha256"], "sha256": rep["sha256"],
           "normalised_sha256": rep["normalised_sha256"], "status": rep["status"],
           "verifier": rep["fingerprint"]["verifier"], "measurement": rep["fingerprint"]["measurement"],
           "sandbox": rep["fingerprint"]["sandbox"], "hard_pool_sizes": hp["sizes"],
           "S": {b: scores[b]["S"] for b in BOARDS}, "S_thumbv7em_reported_only": scores["thumbv7em"]["S"],
           "printed_incumbent_ratio": {b: (rep.get("comparison") or {}).get(b, {}).get("ratio") for b in BOARDS},
           "form": "stages" if rep["status"] == "measured-by-stages" else "evaluate",
           "targets": {}}
    for t in TARGETS:
        data = meas[t]
        require(data["target"] == t and not data.get("timeout") and data["wrong"] == []
                and data["sample"]["mismatches"] == 0 and data["sample"]["words"] == 3 * c["target_sample"]
                and set(data["functions"]) == set(FUNCTIONS), f"{t}: incomplete measurement or wrong outputs")
        require(type(data["stack"]) is int and 0 <= data["stack"] <= 8192 and 0 < static["stack_bound"][t] <= 8192,
                f"{t}: stack out of limits")
        require(0 < rep["bytes"][t] <= 65536, f"{t}: code size out of limits")
        trow = {"bytes": rep["bytes"][t], "stack": data["stack"], "stack_bound": static["stack_bound"][t],
                "sample_words": data["sample"]["words"], "sample_mismatches": 0, "wrong": 0, "functions": {}}
        logs_ = []
        for fn in FUNCTIONS:
            sets = data["functions"][fn]
            require(set(sets) == set(c["sets"]), f"{t}/{fn}: missing input classes")
            for name, v in sets.items():
                require(v["n"] == c["set_sizes"][name] and all(positive(v[k]) for k in ("mean", "median", "p999", "max"))
                        and max(v["mean"], v["median"], v["p999"]) <= v["max"] <= c["cap_instr"],
                        f"{t}/{fn}/{name}: invalid counts")
            base = sum(w * math.log(sets[n]["mean"]) for n, w in c["sets"].items())
            tail = (1 + max(0.0, sets["hard"]["p999"] - factor * sets["typical"]["mean"]) / scale) ** exponent
            logs_.append(base + math.log(tail))
            sf = scores[t]["functions"][fn]
            require(math.isclose(sf["geo_mean_instr"], math.exp(base), rel_tol=1e-9)
                    and math.isclose(sf["tail_factor"], tail, rel_tol=1e-12), f"{t}/{fn}: reported mean/tail differ")
            trow["functions"][fn] = {"means": {n: sets[n]["mean"] for n in c["sets"]},
                                     "n": {n: sets[n]["n"] for n in c["sets"]},
                                     "hard_p999": sets["hard"]["p999"], "tail_factor": tail}
        size_factor = (1 + rep["bytes"][t] / unit) ** sexp
        expected = math.exp(sum(logs_) / len(logs_)) * size_factor
        require(positive(scores[t]["S"]) and math.isclose(scores[t]["S"], expected, rel_tol=1e-12), f"{t}: S does not recompute")
        trow["size_factor"] = size_factor
        row["targets"][t] = trow
    gm = math.sqrt(scores["rv32im"]["S"] * scores["thumbv6m"]["S"])
    require(positive(scores["overall"]["S"]) and math.isclose(scores["overall"]["S"], gm, rel_tol=1e-12), "overall is not the GM")
    host = rep.get("host_check")
    require(host is not None, "a measured row needs the passing quick host check (evaluate's or the fullcheck stages')")
    if host is not None:
        require(host["ok"] is True and host["quick"] is True and set(host["functions"]) == set(FUNCTIONS),
                "quick host check did not pass")
        for fn, h in host["functions"].items():
            require(h["verdict"] == "passed" and h["mismatches"] == 0 and h["words_checked"] == 128 * (1 << 20)
                    and not h.get("sanitizer"), f"quick host check of {fn} incomplete")
        row["quick_host_check"] = {fn: {"words": h["words_checked"], "mismatches": 0, "complete": h["complete"]}
                                  for fn, h in host["functions"].items()}
    return row


def static_pass(d, src, m):
    rec, out = log(d, "check", "check", src)
    require(rec["exit_code"] == 0 and out.startswith("PASS "), "static check did not pass")
    static = json.loads(out.removeprefix("PASS "))
    grec, gout = log(d, "gate", "gate", src)
    gate = json.loads(gout)
    require(gate["kind"] == "gate" and gate["sha256"] == digest(REPO / src), "gate report is for another source")
    evaluator_ok(gate["fingerprint"], d, m)
    return static, grec, gate


def source_rules(src):
    text = (REPO / src).read_text()
    require(len(text.encode()) <= 256 * 1024, "source over 256 KiB")
    require(not PROBES.search(text), "source contains a target or compiler probe macro")


def build_index(d, packet, m):
    """Recompute the packet's index from raw logs. Returns the index dict."""
    PACKET_RUNS.clear()
    PACKET_RUNS.update(packet.get("runs", {}))
    src = packet["source"]["path"]
    require(digest(REPO / src) == packet["source"]["sha256"], "source SHA-256 differs from packet")
    require(packet["seeds"] == list(SEEDS), "seeds differ from the trial seeds")
    kind, status = packet["kind"], packet["status"]
    index = {"source_sha256": packet["source"]["sha256"]}
    if status == "measured":
        source_rules(src)
        static, grec, gate = static_pass(d, src, m)
        require(grec["exit_code"] == 0 and gate["verdict"] == "accepted", "gate did not accept the source")
        index.update(normalised_sha256=gate["normalised_sha256"], gate_stage=gate["stage"], rows={})
        for seed in SEEDS:
            rep = seed_report(d, seed, src, gate)
            evaluator_ok(rep["fingerprint"], d, m)
            index["rows"][str(seed)] = score_row(rep, static, gate, m)
        return index
    require(kind == "trial", "the control must be measured")
    if status == "duplicate":
        grec, gout = log(d, "gate", "gate", src)
        gate = json.loads(gout)
        require(gate["kind"] == "gate" and gate["sha256"] == packet["source"]["sha256"], "gate report for another source")
        evaluator_ok(gate["fingerprint"], d, m)
        ctl = control_index(m)
        dup = (grec["exit_code"] == 1 and gate["stage"] == "duplicate") or \
              (grec["exit_code"] == 0 and gate["verdict"] == "accepted" and gate["normalised_sha256"] == ctl["normalised_sha256"])
        require(dup, "not a duplicate: gate neither rejects as duplicate nor matches the control's normalised hash")
        index.update(normalised_sha256=gate.get("normalised_sha256"), gate_stage=gate["stage"], duplicate_of=CONTROL_SHA256)
        return index
    require(status == "rejected", f"unknown status {status}")
    grec, gout = log(d, "gate", "gate", src)
    gate = json.loads(gout)
    require(gate.get("kind") == "gate" and grec["exit_code"] in (0, 1) and gate["sha256"] == packet["source"]["sha256"],
            "gate run is an infrastructure error or for another source")
    evaluator_ok(gate["fingerprint"], d, m)
    crec, cout = log(d, "check", "check", src)
    require(crec["exit_code"] in (0, 1), "check run is an infrastructure error")
    if grec["exit_code"] == 1:
        require(gate["verdict"] == "rejected" and gate["stage"] and gate["reasons"], "gate rejection lacks stage/reasons")
        require((crec["exit_code"] == 1 and cout.startswith(f"REJECT [{gate['stage']}]"))
                or (crec["exit_code"] == 0 and gate["stage"] in ("build", "duplicate")), "check inconsistent with gate")
        index.update(rejected_at="gate", stage=gate["stage"], reasons=gate["reasons"])
        return index
    require(crec["exit_code"] == 0 and gate["verdict"] == "accepted", "check/gate inconsistent")
    ctl = control_index(m)
    rejections = {}
    for seed in SEEDS:
        rep = seed_report(d, seed, src, gate, allow_reject=True)
        evaluator_ok(rep["fingerprint"], d, m)
        if rep.get("inputs_sha256") is not None:
            require(rep["inputs_sha256"] == ctl["rows"][str(seed)]["inputs_sha256"], f"seed {seed}: inputs differ from control")
        if rep["status"] == "rejected":
            rejections[str(seed)] = {"stage": rep["stage"], "reasons": rep["reasons"], "examples": rep.get("examples", [])[:5]}
    require(rejections, "no seed shows the claimed rejection")
    index.update(rejected_at="evaluation", rejections=rejections)
    return index


_CONTROL = {}


def control_index(m):
    if "index" not in _CONTROL:
        saved = dict(PACKET_RUNS)
        _CONTROL["index"] = verify(HERE, m, quiet=True)
        PACKET_RUNS.clear()
        PACKET_RUNS.update(saved)
    return _CONTROL["index"]


def ratios(index, ctl):
    return {s: {b: index["rows"][s]["S"][b] / ctl["rows"][s]["S"][b] for b in BOARDS} for s in index["rows"]}


def verify(d, m, quiet=False):
    d = d.resolve()
    packet = read_json(inside(d, "packet.json"))
    require(packet["schema"] == SCHEMA and packet["target"] == d.name, "wrong schema or target name")
    is_control = d == HERE
    require(packet["kind"] == ("control" if is_control else "trial"), "kind does not match the directory")
    if is_control:
        require(packet["source"] == {"path": CONTROL_SOURCE, "sha256": CONTROL_SHA256}, "control must link id50 unchanged")
        require(digest(REPO / CONTROL_SOURCE) == CONTROL_SHA256, "id50 source bytes changed")
    else:
        require(packet["control"] == "eik-work/trials/paired-control" and packet["base"] == {"path": CONTROL_SOURCE, "sha256": CONTROL_SHA256},
                "trial must name this control and the id50 base")
        require((REPO / packet["source"]["path"]).resolve().is_relative_to(d), "trial source must be inside its directory")
    require(isinstance(packet.get("note"), str) and packet["note"].strip(), "missing note")
    index = build_index(d, packet, m)
    require(packet["index"] == json.loads(json.dumps(index)), "packet index differs from what the raw logs give")
    if not is_control and packet["status"] == "measured":
        ctl = control_index(m)
        for s in index["rows"]:
            require(index["rows"][s]["inputs_sha256"] == ctl["rows"][s]["inputs_sha256"]
                    and index["rows"][s]["hard_pool_sizes"] == ctl["rows"][s]["hard_pool_sizes"],
                    f"seed {s}: inputs digest differs from the control")
            require(index["rows"][s]["verifier"] == ctl["rows"][s]["verifier"]
                    and index["rows"][s]["measurement"] == ctl["rows"][s]["measurement"], f"seed {s}: other evaluator")
        require(index["normalised_sha256"] != ctl["normalised_sha256"],
                "same normalised source as the control: record it as a duplicate, not a measured trial")
        r = ratios(index, ctl)
        require(packet["ratio_vs_control"] == json.loads(json.dumps(r)), "ratio_vs_control does not recompute")
        if not quiet:
            print(f"{d.name}: ratio candidate/id50 " + json.dumps(r, sort_keys=True))
    if not quiet:
        if packet["status"] == "measured":
            print(f"{d.name}: {packet['kind']} measured, absolute S " +
                  json.dumps({s: row["S"] for s, row in index["rows"].items()}, sort_keys=True))
        else:
            print(f"{d.name}: negative trial ({packet['status']}) " + json.dumps(
                {k: v for k, v in index.items() if k in ("stage", "rejected_at", "gate_stage", "duplicate_of")}))
    return index


def assemble(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="verify.py assemble")
    ap.add_argument("directory", type=Path)
    ap.add_argument("--logs", type=Path, action="append", required=True,
                    help="a case logs directory; repeat for several cases (a repeated label is kept as LABEL@CASE)")
    ap.add_argument("--source", required=True, help="repository-relative source path")
    ap.add_argument("--kind", choices=("control", "trial"), default="trial")
    ap.add_argument("--status", choices=("measured", "duplicate", "rejected"), default="measured")
    ap.add_argument("--note", required=True)
    a = ap.parse_args(argv)
    d = a.directory.resolve()
    d.mkdir(parents=True, exist_ok=True)
    require(not (d / "packet.json").exists(), "packet.json already exists")
    runs = {}
    for logs in a.logs:
        case = logs.resolve().parent
        work = case.parent.parent
        for rec_path in sorted(logs.glob("*.json")):
            raw = label = rec_path.stem
            if not all((logs / f"{raw}.{e}").exists() for e in ("stdout", "stderr")):
                continue
            if label in runs:  # same label from a later case: kept as evidence under LABEL@CASE
                label = f"{raw}@{case.name}"
            for e in ("json", "stdout", "stderr"):
                shutil.copyfile(logs / f"{raw}.{e}", d / f"{label}.{e}")
            rec = read_json(rec_path)
            args = [x.replace("$REPO/", "") for x in rec["argv"][3:]]
            cmd = ["python3", "eik-work/toolkit/run.py", str(work.relative_to(REPO)) if work.is_relative_to(REPO) else str(work),
                   case.name, raw, *args]
            runs[label] = {"command": " ".join(cmd), "exit_code": rec["exit_code"],
                           "files": {f"{label}.{e}": digest(d / f"{label}.{e}") for e in ("json", "stdout", "stderr")}}
    packet = {"schema": SCHEMA, "kind": a.kind, "target": d.name, "status": a.status,
              "source": {"path": a.source, "sha256": digest(REPO / a.source)}, "seeds": list(SEEDS),
              "note": a.note, "runs": runs}
    if a.kind == "trial":
        packet.update(control="eik-work/trials/paired-control", base={"path": CONTROL_SOURCE, "sha256": CONTROL_SHA256})
    m = manifest()
    packet["index"] = json.loads(json.dumps(build_index(d, packet, m)))
    if a.kind == "trial" and a.status == "measured":
        packet["ratio_vs_control"] = json.loads(json.dumps(ratios(packet["index"], control_index(m))))
    (d / "packet.json").write_text(json.dumps(packet, indent=1, sort_keys=True) + "\n")
    verify(d, m)


def main():
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "assemble":
            assemble(sys.argv[2:])
            return 0
        require(len(sys.argv) == 2, "usage: verify.py DIR | verify.py assemble DIR --logs LOGS --source PATH --note TEXT")
        verify(Path(sys.argv[1]), manifest())
        print("PASS")
        return 0
    except (Bad, ValueError, KeyError, IndexError, TypeError, OSError, AttributeError) as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
