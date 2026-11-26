#!/usr/bin/env python3
"""Validate the thumbv7em/sigmoid evidence without running the target or using the network."""
import hashlib
import json
import lzma
from pathlib import Path
import struct
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCOPE = HERE.relative_to(ROOT).as_posix()
WORK = "test/scratch/thumbv7em-sigmoid"
KIT = "eik-work/toolkit"
OFFLINE = "eik-work/offline-runtime"
FREEZE = "eik-work/freeze"
TRIAL = "eik-work/trials/m0-tanh-refine"
PRIOR = "targetcheck-thumbv7em-sigmoid-all"
SOURCE = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
FINGERPRINT = {
    "measurement": "2c8fd1f3a6711f0639685319fb25262b02bfecf4c6589c52cb58928270a46322",
    "verifier": "ebbf9d5cac596a718532b34798dc452e4050d6940594005c44f9a729c699c5a8",
    "sandbox": "none",
}
PINS = {
    "entry.c": SOURCE,
    f"{TRIAL}/entry.c": SOURCE,
    f"{TRIAL}/packet.json": "f87f8792533bf56d0a145248527f356dc5653147c3ad378e7d029591da390f8c",
    f"{FREEZE}/manifest.json": "7ed07bccda548cfc10ad76ed9bd22a836e1d6984f3d1c208a912fec86d7f990f",
    f"{FREEZE}/evidence/logs/fingerprint.stdout": "6d00a662caaa7c24064216f5b91b6ad4a9f07e61708e5d3436451c50b82bba5d",
    f"{KIT}/files.json": "dfde917987ab51e848f8705cfe46d9c8dbbb1c7035db2b1130d1077d59d064f9",
    f"{KIT}/run.py": "3ed70ea2276af80905800a24462d78d3c72f8a5604000da732744b6b61580fbf",
    f"{KIT}/dependencies.json": "ea29b3e0e7ea1c14df66e20a6f1a733111f427a52f3fbf9a00849fa77f6f9015",
    f"{OFFLINE}/prepare.py": "0142541f00c6bf3304eaec1481da27b7b95e4a282f7ebe23aef4753f9745f35b",
    f"{OFFLINE}/manifest.json": "fe7340f53675006f4d258a6ef4fa20910a56dc4eb7fda0f1d9078586403fd950",
}
EXTENSIONS = ("json", "stdout", "stderr")
OBJECT = "sub-thumbv7em.o"
GUEST = "guest-thumbv7em.elf"
CHECKER = "target-check-thumbv7em.elf"
FROZEN_OBJECTS = f"{FREEZE}/evidence/objects"
PREPARE = ["python3", f"{OFFLINE}/prepare.py", f"{WORK}/dependencies"]
RUNNER = ["python3", f"{KIT}/run.py", "--dependencies", f"{WORK}/dependencies", f"{WORK}/run"]
TARGET_ARGS = ["--function", "sigmoid", "--target", "thumbv7em"]
TARGET = ["targetcheck", "entry.c", *TARGET_ARGS, "--chunks", "0:4096", "--jobs", "2"]
GUEST_ARGS = [f"{WORK}/run/runtime/bin/python", f"{SCOPE}/build_guest.py",
              f"{WORK}/run/cases/exhaustive", "entry.c"]
GUEST_ENV = {
    "PATH": f"$REPO/{WORK}/dependencies/qemu/bin:/usr/bin:/bin",
    "LANG": "C.UTF-8", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "EIK_THREADS": "2",
    **{key: f"$REPO/{WORK}/run/cases/exhaustive/{value}" for key, value in {
        "TMPDIR": "tmp", "HOME": "home", "EIK_BUILD_DIR": "build",
        "ZIG_GLOBAL_CACHE_DIR": "build/zig-cache", "ZIG_LOCAL_CACHE_DIR": "build/zig-cache",
    }.items()},
}
COMMANDS = {
    "prepare_export": {"argv": PREPARE, "exit_code": 1},
    "restore": {"argv": ["python3", f"{WORK}/restore.py"], "exit_code": 0},
    "prepare_restored": {"argv": ["python3", f"{WORK}/offline-runtime/prepare.py", f"{WORK}/dependencies"],
                         "exit_code": 0},
    "setup": {"argv": RUNNER + ["exhaustive", "sigmoid", "setup"], "exit_code": 0},
    "targetcheck": {"argv": RUNNER + ["exhaustive", "exhaustive"] + TARGET, "exit_code": 0},
    "fingerprint": {"argv": RUNNER + ["fingerprint", "fingerprint", "fingerprint", "--details"],
                    "exit_code": 0},
    "build_guest": {"argv": GUEST_ARGS, "environment": GUEST_ENV, "exit_code": 0},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(name):
    path = ROOT / name
    require(path.is_file() and path.resolve() == path and path.is_relative_to(ROOT),
            f"missing or unsafe artifact: {name}")
    return path.read_bytes()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(name):
    return digest(read(name))


def load(name):
    return json.loads(read(name))


def local(name):
    return f"{SCOPE}/{name}"


def checked_hashes():
    for path, expected in PINS.items():
        require(sha(path) == expected, f"pin differs: {path}")
    for path, expected in load(f"{KIT}/files.json").items():
        if path.startswith(("kit/", "wheels/")) or path == "provision.py":
            require(sha(f"{KIT}/{path}") == expected, f"kit input differs: {path}")


def elf(name, elf_type):
    """Return runtime-relevant ELF data plus section and symbol information."""
    data = read(name)
    require(data[:7] == b"\x7fELF\x01\x01\x01", f"{name}: expected little-endian ELF32")
    kind, machine, version, entry, phoff, shoff, flags, ehsize, phsize, phnum, shsize, shnum, shstr = (
        struct.unpack_from("<HHIIIIIHHHHHH", data, 16))
    require((kind, machine, version, ehsize, shsize) == (elf_type, 40, 1, 52, 40)
            and (phnum == 0 or phsize == 32), f"{name}: wrong ARM ELF format")
    require(shnum > 0 and shstr < shnum, f"{name}: no section names")
    headers = [struct.unpack_from("<10I", data, shoff + i * shsize) for i in range(shnum)]

    def contents(header):
        offset, size = header[4:6]
        if header[1] == 8:  # SHT_NOBITS
            return b""
        require(offset + size <= len(data), f"{name}: truncated section")
        return data[offset:offset + size]

    def string(strings, start):
        return strings[start:strings.index(b"\0", start)].decode("ascii")

    strings = contents(headers[shstr])
    sections = {}
    symbols = {}
    for header in headers:
        label = string(strings, header[0])
        require(label not in sections, f"{name}: duplicate ELF section")
        sections[label] = (header[1:4], header[5:], contents(header))
        if header[1] == 2:  # SHT_SYMTAB
            symbol_strings = contents(headers[header[6]])
            for offset, value, size, info, other, index in struct.iter_unpack("<IIIBBH", contents(header)):
                label = string(symbol_strings, offset)
                if label and info & 15 == 2 and index:
                    symbols[label] = (value, size, info, other, index)

    segments = []
    for i in range(phnum):
        program = struct.unpack_from("<8I", data, phoff + i * phsize)
        ptype, offset, va, pa, filesz, memsz, permissions, align = program
        require(offset + filesz <= len(data), f"{name}: truncated segment")
        payload = data[offset:offset + filesz]
        if ptype == 1 and offset == 0 and filesz >= ehsize:
            # e_shoff is the position of the section table, which moves with DWARF size.
            payload = payload[:32] + b"\0" * 4 + payload[36:]
        segments.append((program, digest(payload)))
    return entry, flags, segments, sections, symbols


def debug_strings(data):
    """Canonicalize the workspace-dependent compilation paths emitted by Zig."""
    paths = {
        b"/entry.c": b"$REPO/entry.c",
        b"/kit": b"$CASE/kit",
        b"/kit/harness/guest.c": b"$CASE/kit/harness/guest.c",
    }
    strings = data.split(b"\0")
    return [
        next((name for suffix, name in paths.items() if value.endswith(suffix)), value)
        if value.startswith(b"/") else value
        for value in strings
    ]


def check_objects():
    freeze = load(f"{FREEZE}/manifest.json")
    differences = {}
    for frozen_key, filename, kind in (("object", OBJECT, 1), ("guest_image", GUEST, 2)):
        frozen = f"{FROZEN_OBJECTS}/{filename}"
        expected = freeze["objects"]["thumbv7em"][frozen_key]
        require(expected["path"] == frozen and sha(frozen) == expected["sha256"],
                f"frozen object hash differs: {filename}")
        old = elf(frozen, kind)
        new = elf(local(f"objects/{filename}"), kind)
        require(old[:3] == new[:3] and old[4] == new[4], f"runtime layout or symbols differ: {filename}")
        require(old[3].keys() == new[3].keys(), f"sections differ: {filename}")
        changed = sorted(n for n in old[3] if old[3][n] != new[3][n])
        allowed = {".debug_info", ".debug_str", ".debug_line"}
        if kind == 1:
            allowed.add(".rel.debug_line")
        require(set(changed) == allowed and all(not (new[3][n][0][1] & 2) for n in changed),
                f"unexpected ELF section changes: {filename}")
        require(debug_strings(old[3][".debug_str"][2]) == debug_strings(new[3][".debug_str"][2]),
                f"DWARF strings differ beyond compilation paths: {filename}")
        differences[filename] = changed

    facts = {}
    for filename, symbol in ((GUEST, "eik_batch"), (CHECKER, "_start")):
        entry, _, segments, sections, symbols = elf(local(f"objects/{filename}"), 2)
        require(symbols[symbol][0] == entry and entry & 1, f"{filename}: Thumb entry symbol differs")
        sigmoid, size, *_ = symbols["eik_sigmoid"]
        require(sigmoid & 1 and size > 0 and any(
            p[0] == 1 and p[6] & 1 and p[2] <= (sigmoid & ~1) < (sigmoid & ~1) + size <= p[2] + p[4]
            and p[2] <= (entry & ~1) < p[2] + p[4] for p, _ in segments),
            f"{filename}: entry points outside executable load")
        require(not any(section[0][0] in (4, 9) for section in sections.values()),
                f"{filename}: unexpected linked relocations")
        facts[filename] = {"entry_symbol": symbol, "entry": entry,
                           "sigmoid_address": sigmoid, "sigmoid_bytes": size}
    require(facts[CHECKER]["sigmoid_bytes"] == facts[GUEST]["sigmoid_bytes"],
            "checker and guest sigmoid symbol sizes differ")
    return {"freeze_nonallocated_section_differences": differences, "linked_symbols": facts}


def runner_record(prefix, argv, source):
    record = load(f"{prefix}.json")
    require(record["argv"] == argv and type(record["exit_code"]) is int
            and record["exit_code"] == 0 and record["source_sha256"] == source,
            f"unexpected command, exit, or source: {prefix}")
    for stream in ("stdout", "stderr"):
        require(record[f"{stream}_sha256"] == sha(f"{prefix}.{stream}"),
                f"runner {stream} hash differs: {prefix}")
    require(read(f"{prefix}.stderr") == b"", f"unexpected diagnostics: {prefix}")
    return record


def full_report(path, jobs):
    report = load(path)
    expected = {
        "schema": "eik-report-1", "kind": "targetcheck", "competition": "exact-integer-kernels",
        "function": "sigmoid", "target": "thumbv7em", "sha256": SOURCE, "fingerprint": FINGERPRINT,
        "verdict": "passed", "stage": None, "reasons": [], "range_complete": True, "complete": True,
        "chunk_lo": 0, "chunk_hi": 4096, "words_checked": 1 << 32, "mismatches": 0, "jobs": jobs,
    }
    for key, value in expected.items():
        require(type(report[key]) is type(value) and report[key] == value,
                f"{path}: targetcheck {key} differs")
    return report


def historical():
    packet = load(f"{TRIAL}/packet.json")
    prior = packet["runs"][PRIOR]
    command = ["python3", f"{KIT}/run.py", "test/scratch/m0-tanh-refine", "thumbv7em-complete",
               PRIOR, "targetcheck", f"{TRIAL}/entry.c", *TARGET_ARGS, "--jobs", "1"]
    require(prior["command"].split() == command and prior["exit_code"] == 0
            and packet["source"] == {"path": f"{TRIAL}/entry.c", "sha256": SOURCE},
            "historical packet command, exit, or source differs")
    require(prior["files"] == {f"{PRIOR}.{ext}": sha(f"{TRIAL}/{PRIOR}.{ext}") for ext in EXTENSIONS},
            "historical raw hashes differ from trial packet")
    runner_record(f"{TRIAL}/{PRIOR}", ["$REPO/test/scratch/m0-tanh-refine/runtime/bin/python", "-m",
                  "eik", "targetcheck", f"$REPO/{TRIAL}/entry.c", *TARGET_ARGS, "--jobs", "1"], SOURCE)
    return full_report(f"{TRIAL}/{PRIOR}.stdout", 1)


def runtime():
    pins = load(f"{KIT}/dependencies.json")
    tools = pins["host_tool_versions"]
    qemu = pins["qemu"]["executables"]["qemu-arm"]
    packed = f"{OFFLINE}/payload/{qemu['path']}.xz"
    require(digest(lzma.decompress(read(packed))) == qemu["sha256"], "offline QEMU payload differs")
    lines = read(local("logs/runtime.stdout")).decode().splitlines()
    require(lines[:4] == ["Linux x86_64", f"Python {tools['python']}", tools["host_cc"].split()[-1],
                          qemu["version"]], "runtime version evidence differs")
    assets = [qemu, *pins["wheels"], *pins["qemu"]["source_archives"]]
    observed = {name: checksum for checksum, name in (line.split("  ") for line in lines[5:])}
    require(observed == {asset["path"]: asset["sha256"] for asset in assets}, "staged asset hashes differ")
    install = read(local("logs/install.log")).decode()
    for wheel in pins["wheels"]:
        require(f"installed {wheel['name']}=={wheel['version']} " in install
                and f"sha256={wheel['sha256']} " in install, f"installation evidence missing: {wheel['name']}")
    require("import probe -> 0\n" in install and json.loads(install.splitlines()[-1]) == tools["packages"],
            "runtime import probe failed")
    runner_record(local("logs/fingerprint"), [f"$REPO/{WORK}/run/runtime/bin/python", "-m", "eik",
                  "fingerprint", "--details"], None)
    fingerprint = load(local("logs/fingerprint.stdout"))
    require(read(local("logs/fingerprint.stdout")) == read(f"{FREEZE}/evidence/logs/fingerprint.stdout"),
            "run fingerprint differs from freeze")
    require(fingerprint["details"]["tools"] == tools, "fingerprint tool versions differ")
    for key in ("measurement", "verifier"):
        detail = fingerprint["details"][key]
        require(digest(json.dumps(detail, sort_keys=True).encode()) == FINGERPRINT[key],
                f"computed fingerprint differs: {key}")
        for path, expected in detail["files"].items():
            require(sha(f"{KIT}/kit/{path}") == expected, f"fingerprint input differs: {path}")
    require({key: fingerprint[key] for key in FINGERPRINT} == FINGERPRINT, "fingerprint header differs")
    bundle = load(f"{OFFLINE}/manifest.json")
    omitted = {name: bundle["files"][name]["sha256"] for name in bundle["omitted"]}
    recovered = {name: checksum for name, checksum in
                 (line.split() for line in read(local("logs/restore.stdout")).decode().splitlines())}
    require(recovered == omitted, "restoration hash evidence differs")
    require(read(local("logs/prepare.exit")) == b"1\n"
            and all(name.encode() in read(local("logs/prepare.stderr")) for name in omitted),
            "missing original prepare failure evidence")
    require(read(local("logs/restored-prepare.stdout")) ==
            f"Prepared {len(bundle['files'])} pinned files and verified their on-disk hashes\n".encode(),
            "restored prepare did not verify the bundle")
    return {"fingerprint": FINGERPRINT, "tools": tools, "qemu": qemu, "assets": observed,
            "qemu_arguments": ["-cpu", "max"], "mode": fingerprint["mode"],
            "sigmoid_reference_sha256": sha(f"{KIT}/kit/reference/sigmoid.digest")}


def raw_paths(prefix):
    return {ext: {"path": f"{prefix}.{ext}", "sha256": sha(f"{prefix}.{ext}")} for ext in EXTENSIONS}


def artifact_paths():
    return set(PINS) | {
        f"{TRIAL}/{PRIOR}.{ext}" for ext in EXTENSIONS
    } | {f"{FROZEN_OBJECTS}/{name}" for name in (OBJECT, GUEST)} | {
        f"{OFFLINE}/payload/qemu/bin/qemu-arm.xz",
    } | {
        local(f"objects/{name}") for name in (OBJECT, GUEST, CHECKER)
    } | {
        local(f"logs/{label}.{ext}") for label in ("sigmoid", "fingerprint", "exhaustive") for ext in EXTENSIONS
    } | {
        local(name) for name in ("coverage.json", "README.md", "restore.py", "build_guest.py", "verify.py")
    } | {
        local(f"logs/{name}") for name in (
            "runtime.stdout", "install.log", "prepare.exit", "prepare.stdout", "prepare.stderr",
            "restore.stdout", "restore.stderr", "restored-prepare.stdout", "restored-prepare.stderr",
            "build-guest.stdout", "build-guest.stderr",
        )
    }


def verify():
    checked_hashes()
    result = load(local("result.json"))
    manifest = result["artifact_sha256"]
    require(manifest.keys() == artifact_paths(), "artifact inventory differs")
    for path, expected in manifest.items():
        require(sha(path) == expected, f"artifact hash differs: {path}")

    old = historical()
    identity = runtime()
    inner = [f"$REPO/{WORK}/run/runtime/bin/python", "-m", "eik"]
    runner_record(local("logs/sigmoid"), inner + ["setup"], None)
    runner_record(local("logs/exhaustive"), inner + [TARGET[0], "$REPO/entry.c"] + TARGET[2:], SOURCE)
    require(read(local("logs/sigmoid.stdout")) ==
            b"incumbent registered as champion of rv32im, thumbv6m, overall\n", "setup did not complete")
    for label in ("restore", "restored-prepare", "build-guest"):
        require(read(local(f"logs/{label}.stderr")) == b"", f"unexpected {label} diagnostics")
    report = full_report(local("logs/exhaustive.stdout"), 2)
    image = sha(local(f"objects/{CHECKER}"))
    require(report["image_sha256"] == image and old["image_sha256"] != image,
            "QEMU checker image binding differs")
    require(read(local("logs/build-guest.stdout")).decode().split() ==
            [GUEST, sha(local(f"objects/{GUEST}"))], "guest build hash differs")
    bindings = check_objects()

    coverage = load(local("coverage.json"))
    expected_range = {
        "chunks": [0, 4096], "input_words": [0, 1 << 32], "words_checked": report["words_checked"],
        "mismatches": 0, "provenance": "rerun", "image_sha256": image, "fingerprint": FINGERPRINT,
        "raw": raw_paths(local("logs/exhaustive")),
    }
    require(coverage["ranges"] == [expected_range], "coverage differs, overlaps, has gaps or uses incompatible evidence")
    require(coverage == {
        "status": "pass", "function": "sigmoid", "target": "thumbv7em", "source_sha256": SOURCE,
        "runtime": identity, "ranges": [expected_range], "failures": [], "gaps": [],
        "history": {"selected": False, "reason": "original checker ELF and runtime unavailable",
                    "image_sha256": old["image_sha256"], "words_reported": old["words_checked"],
                    "mismatches_reported": old["mismatches"], "raw": raw_paths(f"{TRIAL}/{PRIOR}")},
    }, "coverage summary differs from evidence")
    require(result == {
        "status": "pass", "source_sha256": SOURCE, "runtime": identity, "commands": COMMANDS,
        "artifact_sha256": manifest, "measurements": {"chunks": [0, 4096], "words_checked": 1 << 32,
                                                     "mismatches": 0, "seconds": report["seconds"]},
        "image_binding": bindings, "failures": [], "gaps": [],
    }, "result summary differs from evidence")
    print("PASS thumbv7em/sigmoid: chunks [0,4096), 4294967296 words, 0 mismatches, bound to retained QEMU checker ELF")


if __name__ == "__main__":
    try:
        verify()
    except (ValueError, OSError, KeyError, IndexError, TypeError, AttributeError, struct.error, lzma.LZMAError) as exc:
        sys.exit(f"FAIL: {exc}")
