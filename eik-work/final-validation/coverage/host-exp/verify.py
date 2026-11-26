#!/usr/bin/env python3
"""Check the retained host exp evidence without executing the entry or toolkit."""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TRIAL = "eik-work/trials/m0-tanh-refine"
TOOLKIT = "eik-work/toolkit"
OFFLINE = "eik-work/offline-runtime/evidence"
FREEZE = "eik-work/freeze/manifest.json"
SOURCE = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
PACKET = TRIAL + "/packet.json"
RUNNER = TOOLKIT + "/run.py"
SANITIZE = ["-fsanitize=undefined,address", "-fno-sanitize-recover=all"]
WORDS = 1 << 32
PINS = {
    FREEZE: "7ed07bccda548cfc10ad76ed9bd22a836e1d6984f3d1c208a912fec86d7f990f",
    TOOLKIT + "/manifest.json": "c22729dc9c28b9e54740e639a2cad1bcf58b5665aaf9ba32ccf2abea08b1cb3a",
    TOOLKIT + "/files.json": "dfde917987ab51e848f8705cfe46d9c8dbbb1c7035db2b1130d1077d59d064f9",
    PACKET: "f87f8792533bf56d0a145248527f356dc5653147c3ad378e7d029591da390f8c",
    OFFLINE + "/kit-logs/fingerprint.json": "8ca299eb7a98c0d0bbd193b31967360dad3c97d941728d029c43e8067069ce7a",
    OFFLINE + "/gcc.stdout": "8497f84b2b8334c413d9c6166bd39d009ba55d2ff60a8f23e66dfa5819c2b048",
    OFFLINE + "/python.stdout": "5b3e43dc38ca01e3f5a7854ba50d4330864b0c1e0f646650b2c78cf072acc366",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    full = ROOT / path
    require(full.resolve().is_relative_to(ROOT), f"outside repository: {path}")
    return full.read_bytes()


def checked(path, expected):
    data = read(path)
    require(sha(data) == expected, f"hash mismatch: {path}")
    return data


def strict_equal(actual, expected, message):
    # JSON encoding distinguishes false from 0 and true from 1.
    require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), message)


def load_log(directory, label, argv, source, artifacts):
    paths = {ext: f"{directory}/{label}.{ext}" for ext in ("json", "stdout", "stderr")}
    record = json.loads(read(paths["json"]))
    strict_equal(record["argv"], argv, f"command mismatch: {label}")
    strict_equal(record["exit_code"], 0, f"nonzero command exit: {label}")
    require(record["source_sha256"] == source, f"source mismatch: {label}")
    stdout = checked(paths["stdout"], record["stdout_sha256"])
    require(checked(paths["stderr"], record["stderr_sha256"]) == b"", f"nonempty stderr: {label}")
    artifacts.update({path: sha(read(path)) for path in paths.values()})
    return record, json.loads(stdout)


def audit():
    artifacts = PINS.copy()
    pinned = {path: checked(path, expected) for path, expected in PINS.items()}
    freeze = json.loads(pinned[FREEZE])
    index = json.loads(pinned[TOOLKIT + "/files.json"])
    manifest = json.loads(pinned[TOOLKIT + "/manifest.json"])
    kit = {path: digest for path, digest in index.items() if path.startswith("kit/")}
    require(kit == manifest["kit"]["file_hashes"], "kit inventory mismatch")
    actual_kit = {
        path.relative_to(ROOT / TOOLKIT).as_posix()
        for path in (ROOT / TOOLKIT / "kit").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    require(actual_kit == kit.keys(), "unexpected or missing kit files")
    for path, digest in kit.items():
        checked(f"{TOOLKIT}/{path}", digest)
    for file in ("run.py", "provision.py", "dependencies.json"):
        path = f"{TOOLKIT}/{file}"
        checked(path, index[file])
        artifacts[path] = index[file]

    trial_source = f"{TRIAL}/entry.c"
    for path in ("entry.c", trial_source):
        checked(path, SOURCE)
        artifacts[path] = SOURCE
    require(freeze["entry"]["sha256"] == SOURCE and freeze["entry"]["same_bytes_as"] == trial_source,
            "freeze source mismatch")
    require(freeze["chosen_packet"] == {"path": PACKET, "sha256": PINS[PACKET]}, "freeze packet mismatch")
    packet = json.loads(pinned[PACKET])
    require(packet["source"] == {"path": trial_source, "sha256": SOURCE}, "packet source mismatch")

    work = "test/scratch/m0-tanh-refine"
    python = f"$REPO/{work}/runtime/bin/python"
    exp_args = ["fullcheck", f"$REPO/{trial_source}", "--function", "exp"]
    fp_args = ["fingerprint", "--details"]
    commands = []
    reports = {}
    for case, label, args, source in (
        ("trial", "fingerprint", fp_args, None),
        ("exhaustive", "exhaustive-exp", exp_args, SOURCE),
    ):
        wrapper = ["python3", RUNNER, work, case, label, *(arg.removeprefix("$REPO/") for arg in args)]
        matching = [run for run in packet["runs"].values() if run["command"] == " ".join(wrapper)]
        require(len(matching) == 1, f"missing or ambiguous packet entry: {label}")
        run = matching[0]
        strict_equal(run["exit_code"], 0, f"packet command failed: {label}")
        strict_equal(run["files"], {
            f"{label}.{ext}": sha(read(f"{TRIAL}/{label}.{ext}")) for ext in ("json", "stdout", "stderr")
        }, f"packet raw hashes mismatch: {label}")
        record, reports[label] = load_log(TRIAL, label, [python, "-m", "eik", *args], source, artifacts)
        commands.append({"wrapper_argv": wrapper, **record})

    fp = reports["fingerprint"]
    ids = {name: fp[name] for name in ("measurement", "verifier", "sandbox")}
    require(ids == freeze["evaluator"], "fingerprint differs from freeze")
    require(fp["kind"] == "fingerprint" and fp["production_problems"] == [], "invalid fingerprint report")
    details = fp["details"]
    for name in ("verifier", "measurement"):
        component = details[name]
        require(sha(json.dumps(component, sort_keys=True).encode()) == ids[name], f"invalid {name} fingerprint")
        for path, digest in component["files"].items():
            require(kit[f"kit/{path}"] == digest, f"fingerprint file differs from pinned kit: {path}")

    replay_python = "$REPO/test/scratch/offline-cold-replay/work/runtime/bin/python"
    record, replay = load_log(f"{OFFLINE}/kit-logs", "fingerprint",
                              [replay_python, "-m", "eik", *fp_args], None, artifacts)
    commands.append(record)
    require(record["stdout_sha256"] == artifacts[TRIAL + "/fingerprint.stdout"] and replay == fp,
            "cold replay fingerprint differs")
    tools = details["tools"]
    gcc = pinned[OFFLINE + "/gcc.stdout"].decode().splitlines()[0]
    require(gcc.startswith("gcc ") and gcc == tools["host_cc"] ==
            details["verifier"]["tools"]["host_cc"] == details["measurement"]["tools"]["host_cc"],
            "GCC identity mismatch")
    require(tools["machine"] == "x86_64" and re.fullmatch(r"3\.12\.\d+", tools["python"]) and
            pinned[OFFLINE + "/python.stdout"].decode().strip() == f"Python {tools['python']}",
            "Python or architecture identity mismatch")
    require(details["verifier"]["constants"]["host_sanitize"] == SANITIZE, "missing sanitizer flags")

    reference = details["verifier"]["files"]["reference/exp.digest"]
    ref_path = f"{TOOLKIT}/kit/reference/exp.digest"
    require(len(checked(ref_path, reference)) == 4096 * 32, "wrong exp digest size")
    artifacts[ref_path] = reference
    expected_report = {
        "schema": "eik-report-1", "competition": "exact-integer-kernels",
        "kind": "fullcheck", "function": "exp", "sha256": SOURCE, "fingerprint": ids,
        "chunk_lo": 0, "chunk_hi": 4096, "words_checked": WORDS, "quick": False,
        "complete": True, "range_complete": True, "mismatches": 0, "exit": 0,
        "verdict": "passed", "stage": None, "examples": [], "reasons": [],
    }
    report = reports["exhaustive-exp"]
    strict_equal({k: report[k] for k in expected_report}, expected_report,
                 "fullcheck report does not establish clean whole-domain coverage")
    require("sanitizer" not in report, "sanitizer error recorded")
    return {
        "schema": "host-exp-coverage-1", "status": "pass", "function": "exp", "runtime": "host",
        "source_sha256": SOURCE,
        "identities": {"fingerprint": ids, "tools": tools, "host_sanitize": SANITIZE,
                       "kit_commit": manifest["kit"]["commit"], "exp_digest_sha256": reference},
        "ranges": [{
            "chunk_lo": 0, "chunk_hi": 4096, "word_lo": 0, "word_hi": WORDS,
            "words_checked": WORDS, "mismatches": 0, "sanitizer_errors": 0,
            "complete": True, "range_complete": True, "quick": False,
            "provenance": "reused", "report": TRIAL + "/exhaustive-exp.stdout",
            "checker_exit": 0, "seconds": report["seconds"],
        }],
        "words_checked": WORDS, "mismatches": 0, "sanitizer_errors": 0,
        "gaps": [], "failures": [], "commands": commands, "artifacts": artifacts,
    }


def main():
    try:
        expected = audit()
        strict_equal(json.loads((HERE / "coverage.json").read_bytes()), expected, "coverage differs from audited evidence")
        result = {"status": "pass", "coverage": {
            "path": (HERE / "coverage.json").relative_to(ROOT).as_posix(),
            "sha256": sha((HERE / "coverage.json").read_bytes()),
        }, **expected}
        strict_equal(json.loads((HERE / "result.json").read_bytes()), result, "result differs from audited evidence")
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        print(f"host/exp evidence rejected: {error}", file=sys.stderr)
        return 1
    print("host/exp: verified reused GCC ASan+UBSan coverage of [0,4096), "
          "4294967296 words, zero mismatches and sanitizer errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
