#!/usr/bin/env python3
"""Audit the recorded host/sigmoid evidence without executing any artifact."""
import hashlib
import json
import math
from pathlib import Path
import re
import shlex
import struct
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ITEM = HERE.relative_to(ROOT).as_posix()
RAW = ITEM + "/raw/"
KIT = "eik-work/toolkit/"
BUNDLE = "eik-work/offline-runtime/"
OLD = "eik-work/trials/m0-tanh-refine/"
WORK = "test/scratch/host-sigmoid"
CASE = WORK + "/work/cases/exhaustive"
SOURCE = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
REFERENCE = "a62545e4b3067576aa72b26eca71d60f20f8db9774f58fadb45dd0c5a4d69e95"
RESULT_SHA256 = "bd36959eee19114bec9658ba9bdfde054153c1d89ef3679839a700bb2f9abc32"
FINGERPRINT = {
    "measurement": "2c8fd1f3a6711f0639685319fb25262b02bfecf4c6589c52cb58928270a46322",
    "verifier": "ebbf9d5cac596a718532b34798dc452e4050d6940594005c44f9a729c699c5a8",
    "sandbox": "none",
}
FLAGS = ["-fsanitize=undefined,address", "-fno-sanitize-recover=all"]
SANITIZER_ENV = {
    "ASAN_OPTIONS": "exitcode=66:detect_leaks=0:abort_on_error=0:handle_abort=1:symbolize=1",
    "UBSAN_OPTIONS": "halt_on_error=1:exitcode=67:print_stacktrace=1",
}
PINS = {
    "entry.c": SOURCE,
    OLD + "entry.c": SOURCE,
    OLD + "packet.json": "f87f8792533bf56d0a145248527f356dc5653147c3ad378e7d029591da390f8c",
    KIT + "files.json": "dfde917987ab51e848f8705cfe46d9c8dbbb1c7035db2b1130d1077d59d064f9",
    BUNDLE + "manifest.json": "fe7340f53675006f4d258a6ef4fa20910a56dc4eb7fda0f1d9078586403fd950",
    BUNDLE + "prepare.py": "0142541f00c6bf3304eaec1481da27b7b95e4a282f7ebe23aef4753f9745f35b",
}
OLD_LOGS = {OLD + name + ext for name in ("exhaustive-sigmoid", "fingerprint")
            for ext in (".json", ".stdout", ".stderr")}
NEW_LOGS = {RAW + name + ext for name in ("exhaustive-sigmoid", "fingerprint", "native")
            for ext in (".json", ".stdout", ".stderr")}
SUPPORT = {RAW + name for name in ("runtime.json", "check-host", "sub-host-san.o", "install.log",
                                  "prepare.stdout", "prepare.stderr", "prepare.json")}
FACTS = {"chunk_lo": 0, "chunk_hi": 4096, "words_checked": 4294967296,
         "complete": True, "range_complete": True, "mismatches": 0, "examples": []}
RERUN_ARGS = ["fullcheck", "entry.c", "--function", "sigmoid", "--chunks", "0:4096", "--threads", "2"]
RERUN = ["python3", KIT + "run.py", "--dependencies", WORK + "/deps", WORK + "/work",
         "exhaustive"]
PREPARE = ["python3", WORK + "/bundle/offline-runtime/prepare.py"]
GAP = "The prior checker, candidate object, and loaded sanitizer libraries have no recorded byte identities."


def expect(condition, message):
    if not condition:
        raise ValueError(message)


def read(name):
    path = ROOT / name
    expect(path.is_file() and path.resolve() == path and path.is_relative_to(ROOT),
           f"missing or non-ordinary evidence: {name}")
    return path.read_bytes()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_hash(path, value):
    expect(digest(read(path)) == value, f"SHA-256 mismatch: {path}")


def load(path):
    def unique_keys(pairs):
        obj = dict(pairs)
        expect(len(obj) == len(pairs), f"{path}: duplicate JSON key")
        return obj

    return json.loads(read(path), object_pairs_hook=unique_keys)


def fields(obj, expected, label):
    for key, value in expected.items():
        expect(key in obj and json.dumps(obj[key], sort_keys=True) == json.dumps(value, sort_keys=True),
               f"{label}: invalid {key}")


def command(base, argv, source):
    record = load(base + ".json")
    fields(record, {"argv": argv, "exit_code": 0, "source_sha256": source}, base)
    check_hash(base + ".stdout", record["stdout_sha256"])
    check_hash(base + ".stderr", record["stderr_sha256"])
    expect(read(base + ".stderr") == b"", f"{base}: unexpected stderr")
    return load(base + ".stdout")


def validate_fingerprint(doc):
    fields(doc, dict(FINGERPRINT, kind="fingerprint", schema="eik-report-1",
                     competition="exact-integer-kernels"), "fingerprint")
    details = doc["details"]
    for key in ("verifier", "measurement"):
        spec = details[key]
        expect(digest(json.dumps(spec, sort_keys=True).encode()) == FINGERPRINT[key],
               f"{key} fingerprint payload differs")
        for name, value in spec["files"].items():
            check_hash(KIT + "kit/" + name, value)
    expect(details["verifier"]["files"]["reference/sigmoid.digest"] == REFERENCE,
           "unexpected sigmoid reference")
    expect(len(read(KIT + "kit/reference/sigmoid.digest")) == 4096 * 32,
           "reference lacks a digest for each chunk")
    expect(details["verifier"]["constants"]["host_sanitize"] == FLAGS, "wrong sanitizer flags")
    expect(details["tools"] == load(KIT + "dependencies.json")["host_tool_versions"],
           "tool versions differ from pinned runtime")


def fullcheck(report):
    fields(report, dict(FACTS, schema="eik-report-1", competition="exact-integer-kernels",
                        kind="fullcheck", function="sigmoid", quick=False, sha256=SOURCE,
                        fingerprint=FINGERPRINT, exit=0, verdict="passed", stage=None, reasons=[]),
           "fullcheck")
    expect("sanitizer" not in report, "sanitizer diagnostics present")
    elapsed(report)


def elapsed(report):
    seconds = report["seconds"]
    expect(type(seconds) in (int, float) and math.isfinite(seconds) and seconds > 0,
           "invalid checker duration")
    return seconds


def old_evidence():
    packet = load(OLD + "packet.json")
    fields(packet["source"], {"path": OLD + "entry.c", "sha256": SOURCE}, "prior source")
    work = "test/scratch/m0-tanh-refine"
    prefix = ["$REPO/" + work + "/runtime/bin/python", "-m", "eik"]
    for name, case, args in (
        ("exhaustive-sigmoid", "exhaustive", ["fullcheck", OLD + "entry.c", "--function", "sigmoid"]),
        ("fingerprint", "trial", ["fingerprint", "--details"]),
    ):
        indexed = packet["runs"][name]
        fields(indexed, {"exit_code": 0}, name)
        expect(shlex.split(indexed["command"]) == ["python3", KIT + "run.py", work, case, name, *args],
               f"{name}: packet command differs")
        expect(set(indexed["files"]) == {name + ext for ext in (".json", ".stdout", ".stderr")},
               f"{name}: packet evidence inventory differs")
        for path, value in indexed["files"].items():
            check_hash(OLD + path, value)
    report = command(OLD + "exhaustive-sigmoid", prefix + ["fullcheck", "$REPO/" + OLD + "entry.c",
                                                         "--function", "sigmoid"], SOURCE)
    fullcheck(report)
    validate_fingerprint(command(OLD + "fingerprint", prefix + ["fingerprint", "--details"], None))


def elf_tables(path, types, kind):
    data = read(path)
    expect(data[:7] == b"\x7fELF\x02\x01\x01", f"{path}: expected ELF64 little endian")
    header = struct.unpack_from("<HHIQQQIHHHHHH", data, 16)
    expect(header[0] in kind and header[1] == 62 and header[10] == 64,
           f"{path}: wrong ELF kind, machine or section width")
    sections = [struct.unpack_from("<IIQQQQIIQQ", data, header[5] + i * 64)
                for i in range(header[11])]
    for section in sections:
        if section[1] not in types:
            continue
        start, size, link = section[4:7]
        strings = sections[link]
        names = data[strings[4]:strings[4] + strings[5]]
        yield data[start:start + size], names


def name_at(names, offset):
    end = names.index(b"\0", offset)
    return names[offset:end].decode("ascii")


def validate_objects(libraries):
    needed = set()
    for table, names in elf_tables(RAW + "check-host", {6}, {2, 3}):
        needed.update(name_at(names, offset) for tag, offset in struct.iter_unpack("<qQ", table) if tag == 1)
    expect({"libasan.so.8", "libubsan.so.1", "libc.so.6"} <= needed <= libraries.keys(),
           "checker lacks required sanitizer dependencies or runtime identity")
    symbols = {}
    for table, names in elf_tables(RAW + "sub-host-san.o", {2}, {1}):
        for offset, _, _, section, _, _ in struct.iter_unpack("<IBBHQQ", table):
            symbols[name_at(names, offset)] = section
    expect(symbols.get("eik_sigmoid", 0) != 0 and symbols.get("__asan_init") == 0
           and any(name.startswith("__asan_report_") and section == 0 for name, section in symbols.items())
           and any(name.startswith("__ubsan_handle_") and name.endswith("_abort") and section == 0
                   for name, section in symbols.items()), "missing sanitizer instrumentation in candidate object")


def validate_rerun():
    prefix = ["$REPO/" + WORK + "/work/runtime/bin/python", "-m", "eik"]
    fp = command(RAW + "fingerprint", prefix + ["fingerprint", "--details"], None)
    validate_fingerprint(fp)
    report = command(RAW + "exhaustive-sigmoid",
                     prefix + [arg if arg != "entry.c" else "$REPO/entry.c" for arg in RERUN_ARGS],
                     SOURCE)
    fullcheck(report)
    runtime = load(RAW + "runtime.json")
    fields(runtime, {"platform": ["Linux", "x86_64"], "gcc": fp["details"]["tools"]["host_cc"],
                     "python": fp["details"]["tools"]["python"], "reference_sha256": REFERENCE,
                     "sanitizer_env": SANITIZER_ENV}, "runtime")
    libraries = runtime["linked_libraries"]
    expect("ld-linux-x86-64.so.2" in libraries, "missing runtime loader identity")
    for value in [runtime[key] for key in ("gcc_sha256", "cc1_sha256", "python_sha256")] + list(libraries.values()):
        expect(re.fullmatch(r"[0-9a-f]{64}", value), "invalid tool/runtime digest")
    check_hash(RAW + "check-host", runtime["checker_sha256"])
    check_hash(RAW + "sub-host-san.o", runtime["object_sha256"])
    validate_objects(libraries)

    native = load(RAW + "native.json")
    fields(native, {"exit_code": 0, "checker_sha256": runtime["checker_sha256"],
                    "reference_sha256": REFERENCE}, "native run")
    expect(len(native["argv"]) == 8
           and re.fullmatch(re.escape(CASE) + r"/build/593e2420f5363dcb-[0-9a-f]{12}/check-host", native["argv"][0])
           and native["argv"][1:] == ["sigmoid", CASE + "/kit/reference/sigmoid.digest", "2", "0", "1", "0", "4096"],
           "native run does not bind the checker, reference or range")
    for stream in ("stdout", "stderr"):
        check_hash(RAW + "native." + stream, native[stream + "_sha256"])
    expect(read(RAW + "native.stderr") == b"", "native checker emitted diagnostics")
    native_report = load(RAW + "native.stdout")
    fields(native_report, dict(FACTS, fn="sigmoid"), "native result")

    prepare = load(RAW + "prepare.json")
    bundle = load(BUNDLE + "manifest.json")
    fields(prepare, {"argv": PREPARE + [WORK + "/deps"], "exit_code": 0,
                     "logged_argv": PREPARE + [WORK + "/deps-audit"], "logged_exit_code": 0,
                     "restored": {name: bundle["files"][name]["sha256"]
                                                  for name in bundle["omitted"]}}, "prepare")
    expect(read(RAW + "prepare.stderr") == b""
           and read(RAW + "prepare.stdout").decode() ==
           f"Prepared {len(bundle['files'])} pinned files and verified their on-disk hashes\n",
           "pin restoration did not complete cleanly")
    install_log = read(RAW + "install.log").decode()
    for wheel in load(KIT + "dependencies.json")["wheels"]:
        expect(re.search(r"^installed " + re.escape(wheel["name"] + "==" + wheel["version"]) +
                         r" .* sha256=" + wheel["sha256"] + r" \(", install_log, re.M),
               f"unbound wheel: {wheel['name']}")
    expect("import probe -> 0\n" in install_log, "runtime import probe failed")
    return runtime, elapsed(report), elapsed(native_report)


def main():
    for path, value in PINS.items():
        check_hash(path, value)
    toolkit_files = load(KIT + "files.json")
    for name, value in toolkit_files.items():
        if name.startswith("kit/") or name in ("dependencies.json", "provision.py", "run.py"):
            check_hash(KIT + name, value)
    pinned_inputs = dict(PINS)
    for name in ("dependencies.json", "provision.py", "run.py", "kit/reference/sigmoid.digest"):
        pinned_inputs[KIT + name] = toolkit_files[name]

    result = load(ITEM + "/result.json")
    paths = OLD_LOGS | NEW_LOGS | SUPPORT | {ITEM + "/coverage.json"}
    expect(set(result["artifacts"]) == paths, "wrong evidence inventory")
    for path, value in result["artifacts"].items():
        check_hash(path, value)
    old_evidence()
    runtime, fullcheck_seconds, native_seconds = validate_rerun()

    coverage = load(ITEM + "/coverage.json")
    fields(coverage, {"status": "pass", "function": "sigmoid", "runtime": "host",
                      "source_sha256": SOURCE, "fingerprint": FINGERPRINT, "identity": runtime,
                      "sanitizer_flags": FLAGS,
                      "failures": [], "gaps": [], "words_checked": FACTS["words_checked"],
                      "mismatches": 0, "sanitizer_errors": 0,
                      "prior": {"selected": False, "binding_gap": GAP,
                                "reported_ranges": [[0, 4096]], "reported_words": FACTS["words_checked"],
                                "artifacts": {path: result["artifacts"][path] for path in sorted(OLD_LOGS)}},
                      "ranges": [{"chunk_lo": 0, "chunk_hi": 4096, "words_checked": FACTS["words_checked"],
                                  "provenance": "rerun",
                                  "artifacts": {path: result["artifacts"][path] for path in sorted(NEW_LOGS)}}]},
           "coverage")
    fields(result, {"status": "pass", "function": "sigmoid", "runtime": "host", "gaps": [],
                    "source_sha256": SOURCE, "fingerprint": FINGERPRINT, "tool_identity": runtime,
                    "pinned_inputs": pinned_inputs, "sanitizer_flags": FLAGS,
                    "measured": dict(FACTS, sanitizer_errors=0, threads=2, quick=False,
                                     fullcheck_seconds=fullcheck_seconds, native_seconds=native_seconds),
                    "commands": [
                        {"argv": PREPARE + [WORK + "/deps"], "exit_code": 0},
                        {"argv": PREPARE + [WORK + "/deps-audit"], "exit_code": 0},
                        {"argv": RERUN + ["fingerprint", "fingerprint", "--details"], "exit_code": 0},
                        {"argv": RERUN + ["exhaustive-sigmoid", *RERUN_ARGS], "exit_code": 0},
                        {"argv": load(RAW + "native.json")["argv"], "exit_code": 0},
                    ]}, "result")
    check_hash(ITEM + "/result.json", RESULT_SHA256)
    print("PASS host/sigmoid: [0,4096), 4294967296 words, zero mismatches and sanitizer diagnostics")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, AttributeError, IndexError, struct.error) as exc:
        print(f"Host sigmoid evidence rejected: {exc}", file=sys.stderr)
        sys.exit(1)
