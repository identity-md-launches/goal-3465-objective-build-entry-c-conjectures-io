#!/usr/bin/env python3
"""Verify payload bytes and retained offline replay evidence using only Python."""
from hashlib import sha256
from lzma import LZMAError
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True

from prepare import HERE, TOOLKIT, bundle_manifest, digest, ordinary, read_json, reconstruct, require
from replay import REPO, CHECKERS, commands

ENTRY = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
EVIDENCE = HERE / "evidence"
UPLOAD_LIMIT = 8 * 1024 * 1024
IDENTITY_FILES = ("README.md", "manifest.json", "prepare.py", "replay.py", "verify.py")


def text(path):
    return ordinary(path).read_text()


def identity(value):
    return sha256(json.dumps(value, sort_keys=True, default=list).encode()).hexdigest()


def check_inventory(result):
    evidence = {p.relative_to(HERE).as_posix() for p in EVIDENCE.rglob("*")
                if not p.is_dir() or p.is_symlink()}
    require(set(result["artifact_sha256"]) == evidence | set(IDENTITY_FILES),
            "evidence inventory differs from result")
    for name, expected in result["artifact_sha256"].items():
        require(digest(HERE / name) == expected, f"artifact hash mismatch: {name}")


def check_commands(result, evidence=EVIDENCE):
    scratch = Path(result["scratch"])
    require(scratch.is_relative_to("test/scratch") and ".." not in scratch.parts,
            "recorded scratch is outside test/scratch")
    expected = commands(scratch)
    records = read_json(evidence / "commands.json")
    require(records == result["commands"] and records, "missing or inconsistent command records")
    require([r["name"] for r in records] == list(expected)[:len(records)], "commands missing or reordered")
    for item in records:
        name = item["name"]
        require(item["argv"] == expected[name] and type(item["exit_code"]) is int,
                f"invalid command record: {name}")
        for kind in ("stdout", "stderr"):
            ordinary(evidence / f"{name}.{kind}")
    return {r["name"]: r["exit_code"] for r in records}


def check_kit_log(name, source, scratch):
    logs = EVIDENCE / "kit-logs"
    record = read_json(logs / f"{name}.json")
    args = commands(Path(scratch))[name][7:]
    if source is not None:
        args[1] = "$REPO/entry.c"
    if "--out" in args:
        args[-1] = f"$REPO/{args[-1]}"
    expected = [f"$REPO/{scratch}/work/runtime/bin/python", "-m", "eik", *args]
    require(record["exit_code"] == 0 and record["source_sha256"] == source
            and record["argv"] == expected, f"invalid toolkit log: {name}")
    for stream in ("stdout", "stderr"):
        log = logs / f"{name}.{stream}"
        require(digest(log) == record[f"{stream}_sha256"]
                and digest(log) == digest(EVIDENCE / f"{name}.{stream}"),
                f"inconsistent {stream}: {name}")
    return record


def checked_facts(result, pins, my_manifest):
    checker_names = {"setup", "fingerprint", "check", *CHECKERS}
    for name in checker_names:
        check_kit_log(name, None if name in {"setup", "fingerprint"} else ENTRY, result["scratch"])
    require("incumbent registered as champion" in text(EVIDENCE / "setup.stdout"),
            "missing setup success")
    require("bootstrap passed: offline setup, pinned fingerprints" in text(EVIDENCE / "bootstrap.stdout"),
            "missing cold bootstrap success")
    require(text(EVIDENCE / "prepare.stdout").strip()
            == f"Prepared {len(my_manifest['files'])} pinned files and verified their on-disk hashes",
            "missing reconstruction success")
    install = text(EVIDENCE / "install.log")
    for wheel in pins["wheels"]:
        require(re.search(rf"installed {re.escape(wheel['name'])}=={re.escape(wheel['version'])} "
                          rf"from .* sha256={wheel['sha256']} ", install), "missing wheel installation proof")
    require("import probe -> 0" in install and "--without-pip" in install, "missing offline install proof")

    pinned = read_json(TOOLKIT / "manifest.json")["fingerprint"]
    fingerprint = read_json(EVIDENCE / "fingerprint.stdout")
    tools = pins["host_tool_versions"]
    require(fingerprint["details"]["tools"] == tools and not fingerprint["production_problems"]
            and text(EVIDENCE / "python.stdout").strip() == f"Python {tools['python']}"
            and text(EVIDENCE / "gcc.stdout").splitlines()[0] == tools["host_cc"], "unexpected tool identities")
    for part in ("verifier", "measurement"):
        require(fingerprint[part] == identity(fingerprint["details"][part]) == pinned[part],
                f"invalid {part} fingerprint")
    require(result["tool_identities"]["fingerprint"] == {k: pinned[k] for k in ("verifier", "measurement")},
            "incorrect result fingerprint")
    check_output = text(EVIDENCE / "check.stdout")
    require(check_output.startswith("PASS "), "static check failed")
    facts = {"static_check": json.loads(check_output.removeprefix("PASS ")), "one_chunk": {}}
    targets = set(CHECKERS) - {"host"}
    require(set(facts["static_check"]["bytes"]) == set(facts["static_check"]["stack_bound"]) == targets,
            "static check missing target")
    for target in CHECKERS:
        report = read_json(EVIDENCE / f"{target}.report.json")
        expected = {"schema": "eik-report-1", "competition": "exact-integer-kernels",
                    "function": "exp", "sha256": ENTRY, "chunk_lo": 1016, "chunk_hi": 1017,
                    "words_checked": 1048576, "mismatches": 0, "range_complete": True,
                    "complete": False, "verdict": "passed", "reasons": []}
        if target == "host":
            expected.update(kind="fullcheck", quick=False, exit=0, examples=[])
        else:
            expected.update(kind="targetcheck", target=target, jobs=1)
            require(re.fullmatch(r"[0-9a-f]{64}", report["image_sha256"]),
                    f"missing image hash: {target}")
        require(all(report[k] == v for k, v in expected.items()), f"invalid one-chunk report: {target}")
        require(all(report["fingerprint"][k] == pinned[k] for k in ("verifier", "measurement")),
                f"report fingerprint differs: {target}")
        facts["one_chunk"][target] = {key: report[key] for key in
                                      ("words_checked", "mismatches", "seconds", "verdict")}
    require(result["measured_facts"] == facts, "measured facts differ from the check outputs")


def check_isolation(evidence):
    isolation = read_json(evidence / "isolation.json")
    interfaces = [line.split(":")[0].strip() for line in
                  text(evidence / "network-interfaces.stdout").splitlines()[2:]]
    require(isolation["system"] == "Linux" and isolation["machine"] == "x86_64"
            and isolation["new_scratch"] is True, "missing cold replay isolation record")
    require(all(re.fullmatch(r"net:\[\d+\]", isolation[key]) for key in ("parent_net", "child_net"))
            and isolation["parent_net"] != isolation["child_net"]
            and isolation["interfaces"] == interfaces == ["lo"], "replay was not isolated from the network")


def check_reduced_export(result, manifest, omitted):
    require(result["status"] == "incomplete", "missing payloads rule out offline replay success")
    files = manifest["files"]
    payload_bytes = sum(ordinary(p).stat().st_size for p in (HERE / "payload").rglob("*")
                        if not p.is_dir())
    omitted_bytes = sum(files[name]["bytes"] for name in omitted)
    observed = read_json(EVIDENCE / "upload-rejection.json")
    require(observed["name"] == "bundle_size" and observed["exit_code"] == 1
            and observed["limit_bytes"] == UPLOAD_LIMIT
            and observed["reported_bytes"] > UPLOAD_LIMIT and observed["max_pieces"] == 12,
            "missing upload rejection evidence")
    require(result["distribution"] == {
        "retained_payload_bytes": payload_bytes,
        "omitted_payload_bytes": omitted_bytes,
        "omitted_payloads": omitted,
        "upload_rejection": observed,
    }, "invalid distribution facts")
    require(omitted_bytes > UPLOAD_LIMIT and sum(p.stat().st_size for p in HERE.rglob("*")
            if p.is_file()) <= UPLOAD_LIMIT, "export sizes disagree with the upload limitation")
    require(result["gaps"] == [
        f"Required payload excluded by upload cap: {name}" for name in omitted
    ], "incorrect replay gaps")
    evidence = EVIDENCE / "reduced-export"
    check_isolation(evidence)
    exits = check_commands(result["reduced_export_replay"], evidence)
    require(exits == {"network-interfaces": 0, "python": 0, "gcc": 0, "prepare": 1},
            "unexpected reduced-export command outcome")
    require(text(evidence / "prepare.stdout") == "" and text(evidence / "prepare.stderr").strip()
            == "preparation failed: required payloads absent from export: " + ", ".join(omitted),
            "missing offline preparation failure")


def verify():
    manifest = bundle_manifest()
    omitted = manifest.get("omitted", [])
    require(isinstance(omitted, list) and omitted == sorted(set(omitted))
            and set(omitted) <= manifest["files"].keys(), "invalid omission inventory")
    reconstruct(manifest, omitted=omitted)
    result = read_json(HERE / "result.json")
    require(result["schema"] == 1 and result["status"] in {"pass", "fail", "incomplete"},
            "invalid result status")
    toolkit = read_json(TOOLKIT / "manifest.json")
    pins = read_json(TOOLKIT / "dependencies.json")
    for name, expected in read_json(TOOLKIT / "files.json").items():
        require(digest(TOOLKIT / name) == expected, f"toolkit file differs: {name}")
    require(digest(REPO / "entry.c") == ENTRY and result["source_identities"] == {
        "entry_sha256": ENTRY, "kit_commit": toolkit["kit"]["commit"],
        "reference_digest_list_sha256": toolkit["kit"]["reference_digest_list_sha256"],
    }, "source identities differ")
    require(result["tool_identities"]["host_and_target"] == pins["host_tool_versions"]
            and result["tool_identities"]["qemu"] == pins["qemu"]["executables"],
            "result tool pins differ")
    check_inventory(result)
    exits = check_commands(result)
    check_isolation(EVIDENCE)
    require(set(exits) == set(commands(Path(result["scratch"]))) and not any(exits.values()),
            "incomplete historical replay evidence")
    checked_facts(result, pins, manifest)
    if omitted:
        check_reduced_export(result, manifest, omitted)
    else:
        require(result["status"] == "pass" and result["gaps"] == [], "unsupported offline success")
    return result["status"]


if __name__ == "__main__":
    try:
        status = verify()
    except (ValueError, TypeError, OSError, KeyError, IndexError, AttributeError, LZMAError, EOFError) as exc:
        print(f"offline bundle verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Retained payloads and replay evidence verified. Export replay status: {status}.")
