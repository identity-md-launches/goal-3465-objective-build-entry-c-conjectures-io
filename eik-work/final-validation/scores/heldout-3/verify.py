#!/usr/bin/env python3
"""Verify the held-out score packet without an evaluator runtime or network."""
from datetime import datetime
import hashlib
import importlib.util
import json
import math
import random
from pathlib import Path
import re
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = HERE / "raw"
TOOLKIT = ROOT / "eik-work/toolkit"
KIT = TOOLKIT / "kit"
BOARD = ROOT / "eik-work/final-validation/boards"
SEED = 396172055
RAW_MANIFEST_SHA256 = "9a0b0450fe084f1228433bbccf9b503782580636ce0e22856ca3fdf408a536f3"
FUNCTIONS = ("sigmoid", "tanh", "exp")
POPULATIONS = {"typical": 2000, "wide": 1000, "hard": 300, "uniform": 1000}
WEIGHTS = {"typical": .55, "wide": .30, "hard": .10, "uniform": .05}
TARGETS = ("rv32im", "thumbv6m", "thumbv7em")
BOARDS = ("rv32im", "thumbv6m", "overall")
MEASUREMENT = "2c8fd1f3a6711f0639685319fb25262b02bfecf4c6589c52cb58928270a46322"
VERIFIER = "ebbf9d5cac596a718532b34798dc452e4050d6940594005c44f9a729c699c5a8"
SOURCES = {
    "candidate": ("entry.c", "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"),
    "id50": ("eik-work/baselines/former-50/entry.c",
             "88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3"),
    "incumbent": ("eik-work/toolkit/kit/examples/incumbent.c",
                  "a8dd149453e54363c359ac82c9cee870006c7bf066a590ec7c8147a064622713"),
}
PINS = {
    "eik-work/final-validation/boards/snapshot.json":
        "9c6628300f95c89b0c5bbaf9bf60469e0070c82cc7a6d7091309045032164676",
    "eik-work/toolkit/files.json": "dfde917987ab51e848f8705cfe46d9c8dbbb1c7035db2b1130d1077d59d064f9",
    "eik-work/toolkit/dependencies.json": "ea29b3e0e7ea1c14df66e20a6f1a733111f427a52f3fbf9a00849fa77f6f9015",
    "eik-work/offline-runtime/manifest.json": "fe7340f53675006f4d258a6ef4fa20910a56dc4eb7fda0f1d9078586403fd950",
    "eik-work/offline-runtime/prepare.py": "0142541f00c6bf3304eaec1481da27b7b95e4a282f7ebe23aef4753f9745f35b",
}
RUNTIME = "$REPO/test/scratch/heldout-3/work/runtime/bin/python"
WRAPPER = "$REPO/eik-work/final-validation/scores/heldout-3/cap_evaluate.py"
SEED_ARGS = ["--seed", str(SEED)]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ordinary(path):
    require(path.is_file() and path.resolve() == path, f"missing or nonordinary file: {path.name}")
    return path


def digest(path):
    return hashlib.sha256(ordinary(path).read_bytes()).hexdigest()


def unique_dict(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON keys")
    return result


def read(path):
    return json.loads(ordinary(path).read_bytes(), parse_constant=invalid_constant,
                      object_pairs_hook=unique_dict)


def invalid_constant(value):
    raise ValueError(f"invalid JSON constant {value}")


def report(label):
    return read(RAW / f"{label}.stdout")


def json_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def same_float(observed, expected):
    return type(observed) is float and math.isclose(observed, expected, rel_tol=2e-15)


def pinned_data():
    for name, wanted in PINS.items():
        require(digest(ROOT / name) == wanted, f"pin mismatch: {name}")
    for name, wanted in SOURCES.values():
        require(digest(ROOT / name) == wanted, f"source mismatch: {name}")
    index = read(TOOLKIT / "files.json")
    for name, wanted in index.items():
        if name.startswith("kit/") or name in ("run.py", "verify.py", "provision.py"):
            require(digest(TOOLKIT / name) == wanted, f"toolkit mismatch: {name}")
    bundle = read(ROOT / "eik-work/offline-runtime/manifest.json")
    assets = {name: bundle["files"][name]["sha256"] for name in bundle["omitted"]}
    installation = (RAW / "install.log").read_text()
    for name, wanted in assets.items():
        if name.startswith("wheels/"):
            require(f"{name} sha256={wanted}" in installation, f"runtime install missing {name}")
    require("Prepared 33 pinned files" in (RAW / "prepare.stdout").read_text()
            and "bootstrap passed: offline setup, pinned fingerprints" in (RAW / "bootstrap.stdout").read_text(),
            "runtime validation records")
    for label in ("prepare", "bootstrap"):
        require((RAW / f"{label}.exit").read_text().strip() == "0", f"{label} failed")
    snapshot = read(BOARD / "snapshot.json")
    require(set(snapshot["board_references"]) == set(BOARDS), "snapshot boards")
    references = {}
    for board in BOARDS:
        ref = snapshot["board_references"][board]
        row = snapshot["entries"][str(ref["submission"])]
        path = BOARD / row["path"]
        require(snapshot["boards"][board]["measurement_identity"] == [MEASUREMENT]
                and snapshot["boards"][board]["promotion_bar"] == .97, f"{board}: board identity")
        require(row["declared_source_sha256"] == ref["source_sha256"]
                and digest(path) == row["downloaded_sha256"], f"{board}: source response binding")
        response = read(path)
        require(response["status"] == 403 and response["reason_code"] == "SOURCE_WITHHELD",
                f"{board}: source HTTP response")
        metadata_path = f"raw/submission-{ref['submission']}.json"
        require(digest(BOARD / metadata_path) == snapshot["files"][metadata_path]["sha256"],
                f"{board}: submission metadata hash")
        metadata = read(BOARD / metadata_path)
        require(metadata["source_sha256"] == ref["source_sha256"], f"{board}: source declaration")
        require(not ref["shipped"] and row["status"] == "withheld"
                and row["reason_code"] == "SOURCE_WITHHELD", f"{board}: reference needs measurement")
        require(not any(digest(p) == ref["source_sha256"] for p in (BOARD / "references").rglob("*.c")),
                f"{board}: available reference omitted")
        references[board] = {**ref, "availability": row["reason_code"]}
    require(digest(BOARD / "references/id50.c") == SOURCES["id50"][1], "id50 snapshot binding")
    return references, assets


def fingerprint():
    fp = report("fingerprint")
    require(fp["schema"] == "eik-report-1" and fp["kind"] == "fingerprint"
            and fp["competition"] == "exact-integer-kernels"
            and fp["production_problems"] == [], "fingerprint report")
    for key, wanted in (("verifier", VERIFIER), ("measurement", MEASUREMENT)):
        detail = fp["details"][key]
        require(fp[key] == wanted == json_hash(detail), f"{key} identity")
        for name, expected in detail["files"].items():
            require(digest(KIT / name) == expected, f"{key} file {name}")
    t = fp["details"]["tools"]
    require(t["python"].startswith("3.12.") and t["machine"] == "x86_64"
            and (RAW / "uname.stdout").read_text().strip() == "Linux x86_64"
            and t["host_cc"] == (RAW / "gcc.stdout").read_text().splitlines()[0], "platform identity")
    return {key: fp[key] for key in ("verifier", "measurement", "sandbox")}


def input_binding():
    # Load only the hash-checked, standard-library input generator. Supply retained fresh pools
    # directly, so neither hardscan nor the runtime is needed on the verifier machine.
    pools = {}
    scans = read(RAW / "hardscan.json")
    require(set(scans) == set(FUNCTIONS), "fresh scanner functions")
    scanner_hashes = set()
    for fn in FUNCTIONS:
        path = RAW / f"pool-{fn}.txt"
        data = [line.split() for line in ordinary(path).read_text().splitlines()]
        require(data and all(len(row) == 2 and re.fullmatch(r"[0-9a-fA-F]{8}", row[0])
                             and 0 <= float(row[1]) <= 3.815e-6 for row in data),
                f"malformed fresh pool: {fn}")
        pools[fn] = [int(row[0], 16) for row in data]
        scan = scans[fn]
        executable = scan["argv"][0]
        scan_seed = int.from_bytes(random.Random(f"{SEED}:{fn}:hardscan").randbytes(8), "little")
        require(re.fullmatch(r"hardscan-[0-9a-f]{12}", executable)
                and scan["argv"] == [executable, fn, str(1 << 26), "-18", str(scan_seed)]
                and scan["cache_file"] == f"{executable}-{1 << 26}-{SEED}-{fn}.txt"
                and scan["pool_sha256"] == digest(path) and scan["pool_words"] == len(data)
                and re.fullmatch(r"[0-9a-f]{64}", scan["scanner_sha256"]),
                f"fresh scanner binding: {fn}")
        scanner_hashes.add(scan["scanner_sha256"])
    require(len(scanner_hashes) == 1, "hard pools came from different scanner executables")
    package = types.ModuleType("_heldout_eik")
    package.__path__ = [str(KIT / "eik")]
    sys.modules[package.__name__] = package
    # The draw path needs only the population constants once hard_pool is supplied.
    config = types.ModuleType("_heldout_eik.config")
    config.SET_SIZES = POPULATIONS
    sys.modules[config.__name__] = config
    spec = importlib.util.spec_from_file_location("_heldout_eik.inputs", KIT / "eik/inputs.py")
    inputs = importlib.util.module_from_spec(spec)
    code = compile(ordinary(KIT / "eik/inputs.py").read_bytes(), str(KIT / "eik/inputs.py"), "exec")
    exec(code, inputs.__dict__)
    inputs.hard_pool = lambda fn, seed: pools[fn]
    h = hashlib.sha256()
    for fn in FUNCTIONS:
        for name, words in inputs.draw(SEED, fn).items():
            require(len(words) == POPULATIONS[name], f"{fn}/{name}: reproduced input size")
            h.update(f"{fn}:{name}:".encode())
            h.update(b"".join(word.to_bytes(4, "little") for word in words))
    sample = inputs.target_sample(SEED, 32768)
    sample_hash = hashlib.sha256(b"".join(word.to_bytes(4, "little") for word in sample)).hexdigest()
    return h.hexdigest(), sample_hash, {
        "source": "hardscan", "sizes": {fn: len(pool) for fn, pool in pools.items()},
        "samples": 1 << 26, "threshold_log2_ulps": -18,
    }


def measured(label, ids, inputs_sha256, hard_pool):
    raw = report(label)
    require(raw["kind"] == "measure" and raw["schema"] == "eik-report-1"
            and raw["competition"] == "exact-integer-kernels"
            and raw["verdict"] == "passed" and raw["stage"] is None and raw["reasons"] == []
            and raw["sha256"] == SOURCES[label][1] and raw["seed"] == SEED
            and raw["fingerprint"] == ids and raw["inputs_sha256"] == inputs_sha256
            and raw["hard_pool"] == hard_pool and raw["sampled"] is True, f"{label}: measurement binding")
    for key in ("targets", "bytes", "images"):
        require(set(raw[key]) == set(TARGETS), f"{label}: incomplete {key}")
    require(set(raw["scores"]) == {*TARGETS, "overall"}, f"{label}: score names")
    scores = {}
    for t in TARGETS:
        m, size, parts = raw["targets"][t], raw["bytes"][t], raw["scores"][t]
        require(m["target"] == t and "timeout" not in m and m["wrong"] == []
                and m["sample"] == {"words": 98304, "mismatches": 0, "examples": []}
                and 0 <= m["stack"] <= 8192, f"{label}/{t}: wrong, timeout, stack or sample")
        require(set(m["functions"]) == set(FUNCTIONS), f"{label}/{t}: functions")
        require(type(size) is int and 0 < size <= 65536 and parts["bytes"] == size
                and re.fullmatch(r"[0-9a-f]{64}", raw["images"][t]), f"{label}/{t}: bytes or image")
        require(parts.get("reported_only", False) == (t == "thumbv7em"),
                f"{label}/{t}: reported-only flag")
        logs = []
        for fn in FUNCTIONS:
            data = m["functions"][fn]
            require(set(data) == set(POPULATIONS), f"{label}/{t}/{fn}: populations")
            for name, count in POPULATIONS.items():
                stats = data[name]
                require(stats["n"] == count and 0 < stats["mean"] <= stats["max"] <= 20_000_000
                        and 0 < stats["median"] <= stats["p999"] <= stats["max"]
                        and (name != "hard" or stats["p999"] == stats["max"]),
                        f"{label}/{t}/{fn}/{name}: invalid statistics")
            base = sum(w * math.log(data[n]["mean"]) for n, w in WEIGHTS.items())
            excess = max(0, data["hard"]["p999"] - 20 * data["typical"]["mean"])
            tail = (1 + excess / 1e6) ** .1
            p = parts["functions"][fn]
            require(same_float(p["geo_mean_instr"], math.exp(base)) and same_float(p["tail_factor"], tail),
                    f"{label}/{t}/{fn}: score components")
            logs.append(base + math.log(tail))
        size_factor = (1 + size / 65536) ** .5
        calculated = math.exp(sum(logs) / 3) * size_factor
        require(same_float(parts["size_factor"], size_factor) and same_float(parts["S"], calculated),
                f"{label}/{t}: score")
        scores[t] = parts["S"]
    overall = math.sqrt(scores["rv32im"] * scores["thumbv6m"])
    require(same_float(raw["scores"]["overall"]["S"], overall), f"{label}: overall score")
    scores["overall"] = raw["scores"]["overall"]["S"]
    return scores


def checked_commands(ids, candidate_raw):
    commands = read(RAW / "commands.json")
    eik = [RUNTIME, "-m", "eik"]
    expected = {
        "uname": (["uname", "-sm"], None),
        "gcc": (["gcc", "--version"], None),
        "fingerprint": (eik + ["fingerprint", "--details"], None),
        "evaluate": ([RUNTIME, WRAPPER, "evaluate", "$REPO/entry.c", "--quick", "--json", *SEED_ARGS],
                     SOURCES["candidate"][1]),
    }
    for label in ("candidate", "id50"):
        path, source = SOURCES[label]
        expected[label] = (eik + ["measure", "$REPO/" + path, *SEED_ARGS], source)
    for fn in FUNCTIONS:
        expected[f"quick-{fn}"] = (eik + ["fullcheck", "$REPO/entry.c", "--quick",
                                         "--function", fn, *SEED_ARGS], SOURCES["candidate"][1])
    require(set(commands) == set(expected), "missing or unexpected stage commands")
    for label, (argv, source) in expected.items():
        record = commands[label]
        require(record["argv"] == argv and record["source_sha256"] == source
                and type(record["exit_code"]) is int and record["seconds"] >= 0
                and datetime.fromisoformat(record["started_utc"]).utcoffset().total_seconds() == 0,
                f"{label}: command binding")
        if label != "evaluate":
            require(record["exit_code"] == 0, f"{label}: unexpected exit")
    setup = read(RAW / "setup.json")
    require(setup["exit_code"] == 0 and setup["argv"] == eik + ["setup"]
            and setup["source_sha256"] is None and setup["seconds"] >= 0, "setup command")
    for ext in ("stdout", "stderr"):
        require(digest(RAW / f"setup.{ext}") == setup[f"{ext}_sha256"], "setup output binding")
    before = read(RAW / "boards-before.json")
    require(digest(RAW / "boards-after.json") == digest(RAW / "boards-before.json")
            and set(before["boards"]) == set(BOARDS)
            and set(before["entries"]) == {"incumbent"}
            and before["entries"]["incumbent"]["sha256"] == SOURCES["incumbent"][1]
            and all(v["champion"] == "incumbent" for v in before["boards"].values()),
            "local incumbent state")

    ev = commands["evaluate"]
    log = (RAW / "evaluate.stderr").read_text()
    eval_start = datetime.fromisoformat(ev["started_utc"])
    measure_start = datetime.fromisoformat(commands["candidate"]["started_utc"])
    require(all(eval_start <= datetime.fromisoformat(scan["pool_mtime_utc"]) <= measure_start
                for scan in read(RAW / "hardscan.json").values()), "hard pools predate this evaluation")
    marker = re.search(r"^Incumbent worker started after ([0-9.]+)s \((rv32im|thumbv6m)\); 600s cap armed$",
                       log, re.MULTILINE)
    require(marker is not None, "missing incumbent phase observation")
    if ev["exit_code"] == 124:
        require(599.9 <= ev["seconds"] - float(marker[1])
                and "Timeout: incumbent comparison exceeded 600s" in log
                and log.count("Incumbent worker finished") < 2
                and (RAW / "evaluate.stdout").stat().st_size == 0, "incumbent timeout evidence")
        evaluation = {"outcome": "incumbent_timeout", "cap_seconds": 600,
                      "mode": "standalone measure and quick fullcheck fallback"}
    else:
        require(ev["exit_code"] == 0 and log.count("Incumbent worker finished") == 2
                and "Timeout:" not in log, "evaluate exit or incomplete incumbent phase")
        evaluation_raw = report("evaluate")
        require(evaluation_raw["status"] in ("would-take-over-after-full-check", "evaluated")
                and evaluation_raw["seed"] == SEED
                and evaluation_raw["sha256"] == SOURCES["candidate"][1]
                and evaluation_raw["fingerprint"] == ids
                and evaluation_raw["inputs_sha256"] == candidate_raw["inputs_sha256"]
                and evaluation_raw["hard_pool"] == candidate_raw["hard_pool"]
                and evaluation_raw["measurements"] == candidate_raw["targets"]
                and evaluation_raw["scores"] == candidate_raw["scores"],
                "completed evaluate does not agree with standalone candidate measurement")
        require(set(evaluation_raw["comparison"]) == set(BOARDS)
                and all(row["champion"] == "incumbent" for row in evaluation_raw["comparison"].values()),
                "evaluate baseline")
        evaluation = {"outcome": "completed", "cap_seconds": 600, "mode": "evaluate against kit incumbent"}

    quick = {}
    for fn in FUNCTIONS:
        raw = report(f"quick-{fn}")
        require(raw["kind"] == "fullcheck" and raw["schema"] == "eik-report-1"
                and raw["competition"] == "exact-integer-kernels"
                and raw["function"] == fn and raw["sha256"] == SOURCES["candidate"][1]
                and raw["fingerprint"] == ids and raw["verdict"] == "passed" and raw["exit"] == 0
                and (raw["chunk_lo"], raw["chunk_hi"]) == (0, 4096)
                and raw["quick"] is True and raw["complete"] is False and raw["range_complete"] is False
                and raw["mismatches"] == 0 and raw["words_checked"] == (128 << 20)
                and raw["examples"] == [] and "sanitizer" not in raw and raw["seconds"] >= 0,
                f"{fn}: invalid quick fullcheck evidence")
        quick[fn] = {k: raw[k] for k in ("words_checked", "mismatches", "seconds", "complete")}
    infrastructure = {
        "prepare": {
            "argv": ["python3", "test/scratch/heldout-3/offline-runtime/prepare.py",
                     "test/scratch/heldout-3/deps"],
            "exit_code": int((RAW / "prepare.exit").read_text()),
        },
        "bootstrap": {
            "argv": ["python3", "eik-work/toolkit/verify.py", "bootstrap", "--offline",
                     "--dependencies", "test/scratch/heldout-3/deps"],
            "exit_code": int((RAW / "bootstrap.exit").read_text()),
        },
        "setup": setup,
    }
    return {**infrastructure, **commands}, evaluation, quick


def table(scores):
    lines = [
        "# Held-out seed 396172055",
        "",
        "| Board | Frozen candidate S | Former id50 S | Candidate / id50 | Current submission | Current S | Candidate / current | Current eligibility |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for board in BOARDS:
        row = scores["boards"][board]
        lines.append(f"| {board} | {row['candidate_S']:.9f} | {row['id50_S']:.9f} | "
                     f"{row['id50_ratio']:.9f} | {row['current_reference']['submission']} | "
                     "— | — | Undetermined |")
    diagnostic = scores["reported_only"]["thumbv7em"]
    lines.extend((
        "",
        f"Thumbv7em, reported only, measured {diagnostic['candidate_S']:.9f} for the candidate "
        f"and {diagnostic['id50_S']:.9f} for id50.",
        "",
        "The current source endpoints returned HTTP 403 SOURCE_WITHHELD. Current scores and ratios "
        "are null. The official 0.970 threshold remains untested on this seed.",
        "",
        "The overall score uses the RV32IM and Thumbv6-M scores from the same source. "
        "Quick host checks cover 128 of 4,096 chunks per function. Board eligibility also "
        "requires exhaustive correctness. Each entry passed 98,304 stratified sample calls per target "
        "and all 12,900 scored calls per target.",
    ))
    if scores["evaluate"]["outcome"] == "incumbent_timeout":
        lines.extend(("", "The kit incumbent comparison reached its 600-second cap. "
                      "Scores come from standalone measure reports with full input populations "
                      "and all three target samples. Candidate quick fullcheck reports are retained separately."))
    else:
        lines.extend(("", "Evaluate completed against the kit incumbent. The table uses the "
                          "standalone full-population measurements of the candidate and former id50."))
    return "\n".join(lines) + "\n"


def recompute():
    refs, assets = pinned_data()
    ids = fingerprint()
    inputs, sample_inputs, pools = input_binding()
    candidate = measured("candidate", ids, inputs, pools)
    id50 = measured("id50", ids, inputs, pools)
    commands, evaluation, quick = checked_commands(ids, report("candidate"))
    scores = {
        "checks": {
            label: {t: {
                "guest_sha256": raw["images"][t],
                "scored_wrong_outputs": len(raw["targets"][t]["wrong"]),
                "target_sample": raw["targets"][t]["sample"],
                "code_table_bytes": raw["bytes"][t],
            } for t in TARGETS}
            for label, raw in ((label, report(label)) for label in ("candidate", "id50"))
        },
        "seed": SEED, "inputs_sha256": inputs, "target_sample_inputs_sha256": sample_inputs,
        "fingerprint": ids, "kit_index_sha256": PINS["eik-work/toolkit/files.json"],
        "hard_pool": pools, "populations_per_function": POPULATIONS, "evaluate": evaluation,
        "boards": {b: {"candidate_S": candidate[b], "id50_S": id50[b], "id50_ratio": candidate[b] / id50[b],
                       "id50_ratio_le_0_970": candidate[b] / id50[b] <= .970, "current_reference": refs[b],
                       "current_S": None, "current_ratio": None, "current_ratio_le_0_970": None,
                       "eligibility": "undetermined"} for b in BOARDS},
        "reported_only": {"thumbv7em": {"candidate_S": candidate["thumbv7em"],
                                       "id50_S": id50["thumbv7em"]}},
        "takeover_ratio": .970, "quick_host_checks": quick,
        "eligibility_requires_exhaustive_correctness": True,
    }
    gaps = ["The completed board snapshot withholds all current reference sources (HTTP 403). "
            "No explicit current champion compare is possible and eligibility is undetermined.",
            "The held-out host checks are sampled. Exhaustive correctness is outside this evidence item."]
    if evaluation["outcome"] == "incumbent_timeout":
        gaps.append("Evaluate timed out during the kit incumbent comparison. Standalone measure and quick "
                    "fullcheck stages supply the evidence.")
    result = {
        "status": "incomplete", "kind": "held-out score comparison", "seed": SEED,
        "sources": {k: {"path": name, "sha256": h} for k, (name, h) in SOURCES.items()},
        "tool_identities": report("fingerprint")["details"]["tools"], "fingerprint": ids,
        "pins": PINS, "restored_runtime_payloads": assets,
        "commands": commands, "measured_facts": scores, "gaps": gaps,
        "runtime_settings": {"mode": "development", "EIK_THREADS": 2, "EIK_SCALE": 1,
                             "EIK_HARD_FRESH": True, "host_sanitizers": ["undefined", "address"]},
        "artifacts": {},
    }
    return scores, result


def artifact_index():
    paths = [*RAW.iterdir(), *(HERE / name for name in
             ("collect.py", "cap_evaluate.py", "restore_payloads.py", "verify.py", "README.md",
              "raw-sha256.json", "scores.json", "scores.md"))]
    return {str(p.relative_to(HERE)): digest(p) for p in sorted(paths)}


def check_raw_manifest():
    manifest = HERE / "raw-sha256.json"
    require(digest(manifest) == RAW_MANIFEST_SHA256, "raw manifest hash")
    actual = {path.name: digest(path) for path in RAW.iterdir()}
    require(read(manifest) == actual, "raw evidence inventory or hash")


def main():
    try:
        check_raw_manifest()
        scores, result = recompute()
        result["artifacts"] = artifact_index()
        require(json_hash(read(HERE / "scores.json")) == json_hash(scores), "scores.json differs from recomputation")
        require(ordinary(HERE / "scores.md").read_text() == table(scores), "scores.md differs from recomputation")
        require(json_hash(read(HERE / "result.json")) == json_hash(result), "result or artifact hashes differ from recomputation")
    except (ValueError, OSError, KeyError, TypeError, IndexError, AttributeError) as exc:
        print(f"verify: FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"verify: OK: seed {SEED}, paired candidate/id50 scores, current eligibility undetermined")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
