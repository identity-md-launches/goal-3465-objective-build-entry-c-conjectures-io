#!/usr/bin/env python3
"""Verify the held-out evidence offline using the Python standard library."""
import ast
import hashlib
import json
import math
import random
import re
import struct
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = HERE / "raw"
KIT = ROOT / "eik-work/toolkit"
SNAPSHOT = ROOT / "eik-work/final-validation/boards/snapshot.json"
SEED = 2715043869
FUNCTIONS = ("sigmoid", "tanh", "exp")
TARGETS = ("rv32im", "thumbv6m", "thumbv7em")
BOARDS = (*TARGETS[:2], "overall")
CLASSES = {"typical": (2000, .55), "wide": (1000, .30),
           "hard": (300, .10), "uniform": (1000, .05)}
CANDIDATE = "entry.c"
ID50 = "eik-work/baselines/former-50/entry.c"
PINS = {
    CANDIDATE: "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b",
    ID50: "88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3",
    "eik-work/toolkit/manifest.json": "c22729dc9c28b9e54740e639a2cad1bcf58b5665aaf9ba32ccf2abea08b1cb3a",
    "eik-work/toolkit/files.json": "dfde917987ab51e848f8705cfe46d9c8dbbb1c7035db2b1130d1077d59d064f9",
    "eik-work/toolkit/dependencies.json": "ea29b3e0e7ea1c14df66e20a6f1a733111f427a52f3fbf9a00849fa77f6f9015",
    str(SNAPSHOT.relative_to(ROOT)): "9c6628300f95c89b0c5bbaf9bf60469e0070c82cc7a6d7091309045032164676",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    require(path.is_file() and not path.is_symlink(), f"missing or linked file {path.name}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def unique(pairs):
        result = dict(pairs)
        require(len(result) == len(pairs), f"duplicate JSON keys in {path.name}")
        return result

    return json.loads(path.read_text(), object_pairs_hook=unique,
                      parse_constant=lambda value: require(False, f"invalid JSON number {value}"))


def fingerprint():
    manifest = read(KIT / "manifest.json")
    files = read(KIT / "files.json")
    for relative, expected in manifest["kit"]["file_hashes"].items():
        require(digest(KIT / relative) == expected, f"kit pin mismatch {relative}")
    for relative in ("run.py", "provision.py", "verify.py"):
        require(digest(KIT / relative) == files[relative], f"runner pin mismatch {relative}")

    report = read(RAW / "fingerprint.stdout")
    tools = report["details"]["tools"]
    require(tools["python"].startswith("3.12.") and tools["machine"] == "x86_64"
            and tools["host_cc"].startswith("gcc "), "unexpected evaluator platform")
    pinned_tools = manifest["fingerprint"]["details"]["tools"]
    require(dict(tools, host_cc=pinned_tools["host_cc"], python=pinned_tools["python"]) == pinned_tools,
            "evaluator tool versions differ from the pins")
    require(not report["production_problems"], "evaluator fingerprint reports problems")
    for field in ("measurement", "verifier"):
        component = report["details"][field]
        require(hashlib.sha256(json.dumps(component, sort_keys=True).encode()).hexdigest()
                == report[field], f"wrong {field} identity")
        pinned = manifest["fingerprint"]["details"][field]
        normalized = dict(component, tools=dict(component["tools"]))
        require(normalized["tools"]["host_cc"] == tools["host_cc"], "inconsistent GCC identity")
        normalized["tools"]["host_cc"] = pinned["tools"]["host_cc"]
        require(normalized == pinned, f"{field} differs from pinned kit beyond GCC")
    return manifest["kit"]["commit"], {key: report[key] for key in ("measurement", "verifier", "sandbox")}


def commands():
    records = read(RAW / "commands.json")
    specifications = {
        "setup": ["setup"],
        "fingerprint": ["fingerprint", "--details"],
        "gate": ["gate", "$REPO/" + CANDIDATE],
        "evaluate": ["evaluate", "$REPO/" + CANDIDATE, "--quick", "--json", "--seed", str(SEED)],
        "candidate": ["measure", "$REPO/" + CANDIDATE, "--seed", str(SEED)],
        "id50": ["measure", "$REPO/" + ID50, "--seed", str(SEED)],
        "historical-compare": ["compare", "$REPO/" + CANDIDATE, "--seed", str(SEED),
                               "--champion", "overall=$REPO/" + ID50],
        **{f"quick-{fn}": ["fullcheck", "$REPO/" + CANDIDATE, "--quick", "--seed", str(SEED),
                            "--function", fn] for fn in FUNCTIONS},
    }
    require(set(records) == set(specifications) | {"provision", "bootstrap", "capture-inputs"},
            "incomplete command ledger")
    for label, record in records.items():
        start = datetime.fromisoformat(record["started_utc"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(record["ended_utc"].replace("Z", "+00:00"))
        require(start.utcoffset() is not None and end.utcoffset() is not None and end >= start,
                f"invalid UTC interval for {label}")
        require(record["started_utc"] == (RAW / f"{label}.start").read_text().strip()
                and record["ended_utc"] == (RAW / f"{label}.end").read_text().strip()
                and record["exit_code"] == int((RAW / f"{label}.exit").read_text()),
                f"command ledger differs from raw timing or exit for {label}")
        require(record["exit_code"] in ((0, 124, 137) if label == "evaluate" else (0,)),
                f"unexpected exit for {label}: {record['exit_code']}")
        if label not in specifications:
            continue
        case = "frozen" if label in ("setup", "fingerprint", "gate", "evaluate") else "measured"
        invocation = ["python3", "-B", "eik-work/toolkit/run.py", "--dependencies",
                      "test/scratch/heldout-2/deps", "test/scratch/heldout-2/work", case, label,
                      *[arg.replace("$REPO/", "") for arg in specifications[label]]]
        timed_out = label == "evaluate" and record["exit_code"] != 0
        if label == "evaluate":
            invocation = ["timeout", "--kill-after=5s", "600s", *invocation]
        require(record["argv"] == invocation, f"unexpected invocation of {label}")
        if timed_out:
            require(599 <= (end - start).total_seconds() <= 620 and not (RAW / "evaluate.json").exists()
                    and not (RAW / "evaluate.outer.stdout").read_bytes(),
                    "timeout incorrectly represented as a completed evaluation")
            continue
        job = read(RAW / f"{label}.json")
        require(job["argv"] == ["$REPO/test/scratch/heldout-2/work/runtime/bin/python",
                                 "-m", "eik", *specifications[label]]
                and job["exit_code"] == record["exit_code"] and job["seconds"] >= 0,
                f"mismatched evaluator command record for {label}")
        src = specifications[label][1] if len(specifications[label]) > 1 else ""
        require(job["source_sha256"] == PINS.get(src.removeprefix("$REPO/")),
                f"unbound evaluator source for {label}")
        for stream in ("stdout", "stderr"):
            require(digest(RAW / f"{label}.{stream}") == job[f"{stream}_sha256"]
                    == digest(RAW / f"{label}.outer.{stream}"), f"unbound {label} {stream}")
    expected_support = {
        "provision": ["python3", "-B", "eik-work/toolkit/provision.py", "--fetch",
                      "--dependencies", "test/scratch/heldout-2/deps"],
        "bootstrap": ["python3", "-B", "eik-work/toolkit/verify.py", "bootstrap", "--offline",
                      "--dependencies", "test/scratch/heldout-2/deps"],
        "capture-inputs": ["python3", "-B", str((HERE / "capture_inputs.py").relative_to(ROOT))],
    }
    for label, argv in expected_support.items():
        require(records[label]["argv"] == argv, f"unexpected support command {label}")
    require("Pinned wheels, QEMU executables and QEMU source archives verified"
            in (RAW / "provision.stdout").read_text()
            and "bootstrap passed: offline setup, pinned fingerprints"
            in (RAW / "bootstrap.stdout").read_text(), "missing pinned runtime bootstrap evidence")
    return records


def bind_inputs():
    """Bind the concatenated input words and the stratified sample to the raw reports."""
    module = ast.parse((KIT / "kit/eik/inputs.py").read_text())
    fixed = {node.targets[0].id: ast.literal_eval(node.value)
             for node in module.body if isinstance(node, ast.Assign) and len(node.targets) == 1
             and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ("SPECIALS", "DEEP")}
    sizes = {}
    printed_threshold = float(format(2.0 ** -18, ".3e"))
    words = (RAW / "scored-inputs.bin").read_bytes()
    checksum = hashlib.sha256()
    offset = 0
    for fn in FUNCTIONS:
        pool = (RAW / f"hard-{fn}.txt").read_bytes()
        require(pool == (RAW / f"evaluate-hard-{fn}.txt").read_bytes(),
                f"evaluate and measure hard pools disagree for {fn}")
        rows = pool.decode("ascii").splitlines()
        pool_words = []
        for row in rows:
            word, distance = row.split()
            require(re.fullmatch(r"[0-9a-fA-F]{8}", word)
                    and 0 <= float(distance) <= printed_threshold, f"invalid hard pool row for {fn}")
            pool_words.append(int(word, 16))
        require(pool_words, f"empty hard pool for {fn}")
        sizes[fn] = len(pool_words)
        seed_words = draw_words(fn, fixed, pool_words)
        for name, (count, _) in CLASSES.items():
            block = words[offset:offset + count * 4]
            require(block == struct.pack(f"<{count}I", *seed_words[name]),
                    f"{fn}/{name}: scored words differ from the pinned draw")
            checksum.update(f"{fn}:{name}:".encode() + block)
            offset += count * 4
    require(offset == len(words), "extra scored input words")
    rng = random.Random(f"{SEED}:strata")
    size = 32768
    stride = (1 << 32) // size
    sample = struct.pack(f"<{size}I", *(i * stride + rng.randrange(stride) for i in range(size)))
    require((RAW / "target-sample.bin").read_bytes() == sample, "wrong stratified sample")
    return checksum.hexdigest(), {"source": "hardscan", "samples": 1 << 26,
                                  "threshold_log2_ulps": -18, "sizes": sizes}


def draw_words(fn, fixed, hard_pool):
    """Reproduce the seed binding without importing or running the evaluator."""
    def bits(value):
        return struct.unpack("<I", struct.pack("<f", value))[0]

    def around(value, radius):
        word = bits(value)
        return list(range(word - radius, word + radius + 1))

    rng = random.Random(f"{SEED}:{fn}")
    typical = []
    for _ in range(CLASSES["typical"][0]):
        if fn == "exp":
            value = rng.gauss(0, 3)
            typical.append(bits(-abs(value) if rng.random() < .8 else value))
        else:
            typical.append(bits(rng.gauss(0, 3 if rng.random() < .8 else 1)))
    wide = [rng.getrandbits(1) << 31 | rng.randint(96, 134) << 23 | rng.getrandbits(23)
            for _ in range(CLASSES["wide"][0])]
    if fn == "exp":
        ln2 = math.log(2)
        specials = (fixed["SPECIALS"][:12] + around(128 * ln2, 2) + around(89.0, 1)
                    + around(-126 * ln2, 2) + around(-149 * ln2, 2) + around(-150 * ln2, 2)
                    + around(-104.0, 1) + [word | sign for word in (0x33000000, 0x33800000, 0x34000000)
                                           for sign in (0, 0x80000000)])
    else:
        specials = fixed["SPECIALS"]
    hard = specials + fixed["DEEP"]
    hard += [rng.choice(hard_pool) for _ in range(CLASSES["hard"][0] - len(hard))]
    uniform_rng = random.Random(f"{SEED}:{fn}:uniform")
    uniform = [uniform_rng.getrandbits(32) for _ in range(CLASSES["uniform"][0])]
    return {"typical": typical, "wide": wide, "hard": hard, "uniform": uniform}


def recompute(report, label):
    scores = {}
    require(set(report["targets"]) == set(TARGETS) == set(report["bytes"]) == set(report["images"]),
            f"{label} misses a target")
    for target in TARGETS:
        row = report["targets"][target]
        nbytes = report["bytes"][target]
        require(row["target"] == target and report["sampled"] is True
                and row["wrong"] == [] and "timeout" not in row
                and 0 <= row["stack"] <= 8192 and type(nbytes) is int and 0 < nbytes <= 65536,
                f"{label}/{target}: incomplete or rejected measurement")
        require(row["sample"] == {"words": 98304, "mismatches": 0, "examples": []},
                f"{label}/{target}: incorrect or incomplete target sample")
        require(re.fullmatch(r"[a-f0-9]{64}", report["images"][target]),
                f"{label}/{target}: invalid scoring image hash")
        require(set(row["functions"]) == set(FUNCTIONS), f"{label}/{target}: missing function")
        size_factor = (1 + nbytes / 65536) ** .5
        parts = {}
        logs = []
        for fn in FUNCTIONS:
            classes = row["functions"][fn]
            require(set(classes) == set(CLASSES), f"{label}/{target}/{fn}: missing class")
            for name, (count, _) in CLASSES.items():
                d = classes[name]
                require(d["n"] == count and 0 < d["median"] <= d["p999"] <= d["max"] <= 20_000_000
                        and 0 < d["mean"] <= d["max"], f"{label}/{target}/{fn}/{name}: invalid counts")
                total = d["mean"] * count
                require(abs(total - round(total)) <= 2 * math.ulp(total),
                        f"{label}/{target}/{fn}/{name}: mean is inconsistent with integer counts")
            require(classes["hard"]["p999"] == classes["hard"]["max"], "wrong hard percentile")
            base = sum(weight * math.log(classes[name]["mean"]) for name, (_, weight) in CLASSES.items())
            tail = (1 + max(0., classes["hard"]["p999"] - 20 * classes["typical"]["mean"]) / 1e6) ** .1
            logs.append(base + math.log(tail))
            parts[fn] = {"geo_mean_instr": math.exp(base), "tail_factor": tail}
        scores[target] = {"S": math.exp(sum(logs) / len(logs)) * size_factor,
                          "bytes": nbytes, "functions": parts, "size_factor": size_factor}
        if target == "thumbv7em":
            scores[target]["reported_only"] = True
    scores["overall"] = {"S": math.sqrt(scores["rv32im"]["S"] * scores["thumbv6m"]["S"])}
    numeric_equal(scores, report["scores"], f"{label} harness score")
    return scores


def numeric_equal(actual, reported, label):
    if isinstance(actual, dict):
        require(isinstance(reported, dict) and set(actual) == set(reported), f"{label}: wrong keys")
        for key, value in actual.items():
            numeric_equal(value, reported[key], f"{label}/{key}")
    elif type(actual) is float:
        require(type(reported) is float and math.isclose(actual, reported, rel_tol=2e-15),
                f"{label}: expected {actual!r}, got {reported!r}")
    else:
        require(type(actual) is type(reported) and actual == reported, f"{label}: unexpected value")


def check_historical_compare(reports, fp):
    comparison = read(RAW / "historical-compare.stdout")
    candidate, id50 = reports["candidate"], reports["id50"]
    champion = comparison["champions"][PINS[ID50]]
    require(comparison["kind"] == "compare" and comparison["measure"] == candidate
            and comparison["sha256"] == PINS[CANDIDATE] and comparison["seed"] == SEED
            and comparison["fingerprint"] == fp and set(comparison["champions"]) == {PINS[ID50]},
            "unbound explicit historical comparison")
    for key in ("sha256", "seed", "inputs_sha256", "hard_pool", "fingerprint", "verdict", "bytes"):
        require(champion[key] == id50[key], f"historical compare has a different {key}")
    require(champion["sampled"] is False and set(champion["targets"]) == set(TARGETS[:2]),
            "unexpected historical comparison champion targets")
    for target in TARGETS[:2]:
        require(champion["images"][target] == id50["images"][target]
                and champion["targets"][target] == dict(id50["targets"][target], sample=None),
                f"historical compare differs from the full measurement on {target}")
    entry_S = candidate["scores"]["overall"]["S"]
    ref_S = id50["scores"]["overall"]["S"]
    ratio = entry_S / ref_S
    require(champion["scores"] == {board: id50["scores"][board] for board in BOARDS}
            and comparison["decision"]["boards"]["overall"]
            == {"champion_sha256": PINS[ID50], "entry_S": entry_S, "champion_S": ref_S,
                "ratio": ratio, "beats": ratio <= .970},
            "explicit overall historical decision disagrees with the paired score")


def review():
    for path, expected in PINS.items():
        require(digest(ROOT / path) == expected, f"input pin mismatch {path}")
    kit, fp = fingerprint()
    ledger = commands()
    inputs, pool = bind_inputs()
    require((RAW / "kit-boards.before.json").read_bytes() == (RAW / "kit-boards.after.json").read_bytes(),
            "evaluate changed kit board state")
    state = read(RAW / "kit-boards.before.json")
    require(set(state["boards"]) == set(BOARDS) and all(row["champion"] == "incumbent"
                                                        for row in state["boards"].values())
            and state["entries"]["incumbent"]["sha256"] == digest(KIT / "kit/examples/incumbent.c"),
            "missing pinned kit incumbent")
    gate = read(RAW / "gate.stdout")
    require(gate["kind"] == "gate" and gate["verdict"] == "accepted" and gate["fingerprint"] == fp
            and gate["sha256"] == PINS[CANDIDATE], "unbound candidate gate")
    results = {}
    reports = {}
    for label, src in (("candidate", CANDIDATE), ("id50", ID50)):
        report = read(RAW / f"{label}.stdout")
        require(report["schema"] == "eik-report-1" and report["kind"] == "measure"
                and report["competition"] == "exact-integer-kernels" and report["verdict"] == "passed"
                and report["sha256"] == PINS[src] and report["seed"] == SEED
                and report["inputs_sha256"] == inputs and report["hard_pool"] == pool
                and report["fingerprint"] == fp, f"unpaired {label} measure report")
        reports[label] = report
        results[label] = recompute(report, label)
    check_historical_compare(reports, fp)
    require(gate["bytes"] == reports["candidate"]["bytes"], "gate and measure byte counts disagree")
    checks = {}
    for fn in FUNCTIONS:
        q = read(RAW / f"quick-{fn}.stdout")
        require(q["kind"] == "fullcheck" and q["verdict"] == "passed" and q["function"] == fn
                and q["sha256"] == PINS[CANDIDATE] and q["fingerprint"] == fp and q["exit"] == 0
                and q["quick"] is True and q["complete"] is False and q["range_complete"] is False
                and q["chunk_lo"] == 0 and q["chunk_hi"] == 4096 and q["mismatches"] == 0
                and q["words_checked"] == 128 * 2**20 and q["examples"] == [] and not q.get("sanitizer"),
                f"unbound or failing quick host check for {fn}")
        checks[fn] = q["words_checked"]

    evaluate_exit = ledger["evaluate"]["exit_code"]
    evaluate_completed = evaluate_exit == 0
    phase = read(RAW / "evaluate-phase.json")
    require(phase["fresh_pool_files"] == len(FUNCTIONS), "evaluate did not produce all fresh pools")
    if evaluate_completed:
        evaluation = read(RAW / "evaluate.stdout")
        candidate = reports["candidate"]
        require(evaluation["sha256"] == PINS[CANDIDATE] and evaluation["seed"] == SEED
                and evaluation["fingerprint"] == fp and evaluation["inputs_sha256"] == inputs
                and evaluation["hard_pool"] == pool and evaluation["measurements"] == candidate["targets"]
                and evaluation["scores"] == candidate["scores"]
                and all(evaluation["comparison"][b]["champion"] == "incumbent" for b in BOARDS),
                "unbound completed evaluate")
    else:
        require(phase["host_checker_artifacts"] == 0 and phase["result_files"] == 0,
                "evaluate timeout phase differs from the recorded comparison cutoff")
    snapshot = read(SNAPSHOT)
    rows = {}
    for board in (*BOARDS, "thumbv7em"):
        candidate_S = results["candidate"][board]["S"]
        id50_S = results["id50"][board]["S"]
        ratio = candidate_S / id50_S
        reference = snapshot["per_board"].get(board)
        current = None
        if reference is not None:
            require(reference["reference_path"] is None and reference["reference_sha256"] is None
                    and reference["source_status"] == "withheld"
                    and reference["source_reason_code"] == "SOURCE_WITHHELD",
                    f"current {board} reference is available or missing withholding evidence")
            require(fp["measurement"] in reference["measurement_identity"],
                    f"{board} snapshot measurement identity differs")
            response = SNAPSHOT.parent / reference["source_response"]
            require(digest(response) == reference["source_response_sha256"], "withholding response hash mismatch")
            request = snapshot["requests"][f"source-{reference['champion_submission']}"]
            problem = read(response)
            require(request["http_status"] == problem["status"] == 403
                    and request["path"] == reference["source_response"]
                    and request["sha256"] == reference["source_response_sha256"]
                    and problem["reason_code"] == "SOURCE_WITHHELD",
                    "withholding response lacks HTTP 403 evidence")
            current = {"submission": reference["champion_submission"],
                       "promotion": reference["current_promotion_id"],
                       "sha256": reference["declared_source_sha256"],
                       "source_response": str(response.relative_to(ROOT)),
                       "source_response_sha256": request["sha256"],
                       "source_response_utc": request["finished_utc"],
                       "source_status": "SOURCE_WITHHELD"}
        rows[board] = {"candidate_S": candidate_S, "id50_S": id50_S, "candidate_over_id50": ratio,
                       "historical_le_0_970": ratio <= .970 if reference else None,
                       "current_reference": current, "current_S": None, "candidate_over_current": None,
                       "current_le_0_970": None,
                       "eligibility": "undetermined" if reference else "reported_only"}
    return {"seed": SEED, "inputs_sha256": inputs, "kit_commit": kit, "fingerprint": fp,
            "hard_pool": pool, "takeover_ratio": .970, "boards": rows,
            "scored_words_per_function_per_target": {name: count for name, (count, _) in CLASSES.items()},
            "stratified_words_per_function_per_target": 32768,
            "evaluate_completed": evaluate_completed, "evaluate_exit": evaluate_exit,
            "evaluate_phase_artifacts": phase,
            "paired_measure_stage": True, "quick_host_words": checks,
            "explicit_compare": {"historical_submission": 50, "board": "overall", "exit_code": 0},
            "exhaustive_correctness_certified_here": False}, ledger


def table(scores):
    lines = [
        "# Held-out seed 2715043869", "",
        "| Board | Candidate S | Former 50 S | Candidate / 50 | ≤ 0.970 vs 50 | Current submission | Current S | Candidate / current | Eligibility |",
        "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for board, row in scores["boards"].items():
        threshold = {True: "yes", False: "no", None: "—"}[row["historical_le_0_970"]]
        submission = row["current_reference"]["submission"] if row["current_reference"] else "—"
        lines.append(f"| {board} | {row['candidate_S']:.9f} | {row['id50_S']:.9f} | "
                     f"{row['candidate_over_id50']:.9f} | {threshold} | {submission} | — | — | "
                     f"{row['eligibility'].replace('_', ' ')} |")
    lines += ["", "The overall score uses the RV32IM and Thumbv6-M measurements from the same source.",
              "An explicit kit comparison corroborated the overall former-50 ratio. Only its supplied overall row is used.",
              "Each current source returned HTTP 403 SOURCE_WITHHELD in the board snapshot.",
              "A current-board ratio at or below 0.970 would still require exhaustive correctness.",
              "Each independent measurement scored 4,300 words and checked 32,768 stratified words per function on every target.",
              "The three quick host sanitizer checks covered 134,217,728 words per function.",
              "All scored words, target samples and quick host checks had zero wrong outputs."]
    if not scores["evaluate_completed"]:
        lines += ["", f"The quick evaluate command exited {scores['evaluate_exit']} at its ten-minute limit.",
                  "It had generated the fresh pools and was cut off before producing a report or host checker.",
                  "The paired scores come from the unchanged measure stage with all target samples.",
                  "Separate quick fullcheck stages supplied the host sample evidence."]
    lines += ["", "Full-precision scores and eligibility are in `scores.json`. The command ledger and raw reports are in `raw/`.",
              "The offline bootstrap used the exact toolkit dependency pins. The fetch command restored payloads omitted from the reduced runtime export."]
    return "\n".join(lines) + "\n"


def artifact_hashes():
    require(RAW.is_dir() and not RAW.is_symlink(), "missing raw evidence directory")
    paths = [*RAW.iterdir(), HERE / "scores.json", HERE / "scores.md",
             HERE / "verify.py", HERE / "capture_inputs.py"]
    return {str(path.relative_to(HERE)): digest(path) for path in sorted(paths)}


def main():
    result = read(HERE / "result.json")
    require(result["artifacts"] == artifact_hashes(), "asset inventory or SHA-256 mismatch")
    scores, ledger = review()
    numeric_equal(scores, read(HERE / "scores.json"), "scores.json")
    require((HERE / "scores.md").read_text() == table(scores), "score table differs")
    require(result["status"] == "incomplete" and result["commands"] == ledger
            and result["source"] == PINS and result["measured_facts"] == read(HERE / "scores.json")
            and result["tool"] == {"kit_commit": scores["kit_commit"], **scores["fingerprint"],
                                   "versions": read(RAW / "fingerprint.stdout")["details"]["tools"]},
            "result misstates evidence or claims unsupported success")
    require(set(result["gaps"]) == ({"current_sources", "exhaustive_correctness"}
                                    | ({"evaluate_timeout"} if not scores["evaluate_completed"] else set())),
            "result omits limitations")
    print(f"heldout-2: verified seed {SEED}, paired candidate and former-50 scores, "
          "all current-board eligibility undetermined")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        print(f"heldout-2: FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
