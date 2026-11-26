#!/usr/bin/env python3
"""Audit the retained thumbv6m/tanh packet offline with the Python standard library."""
from hashlib import file_digest, sha256
import json
import lzma
from pathlib import Path
import struct
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REL = HERE.relative_to(ROOT).as_posix()
TOOLKIT = "eik-work/toolkit"
FREEZE = "eik-work/freeze"
TRIAL = "eik-work/trials/m0-tanh-refine"
OFFLINE = "eik-work/offline-runtime"
SCRATCH = "test/scratch/thumbv6m-tanh"
SOURCE = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
REFERENCE = "6596c8553a866cac76ac119eb05c832788d10d1e972ee32bbae35f513b21c34a"
FINGERPRINT = {
    "measurement": "2c8fd1f3a6711f0639685319fb25262b02bfecf4c6589c52cb58928270a46322",
    "verifier": "ebbf9d5cac596a718532b34798dc452e4050d6940594005c44f9a729c699c5a8",
    "sandbox": "none",
}
PINS = {
    "entry.c": SOURCE,
    f"{FREEZE}/manifest.json": "7ed07bccda548cfc10ad76ed9bd22a836e1d6984f3d1c208a912fec86d7f990f",
    f"{TRIAL}/packet.json": "f87f8792533bf56d0a145248527f356dc5653147c3ad378e7d029591da390f8c",
    f"{TRIAL}/entry.c": SOURCE,
    f"{TOOLKIT}/manifest.json": "c22729dc9c28b9e54740e639a2cad1bcf58b5665aaf9ba32ccf2abea08b1cb3a",
    f"{TOOLKIT}/files.json": "dfde917987ab51e848f8705cfe46d9c8dbbb1c7035db2b1130d1077d59d064f9",
    f"{OFFLINE}/manifest.json": "fe7340f53675006f4d258a6ef4fa20910a56dc4eb7fda0f1d9078586403fd950",
    f"{OFFLINE}/prepare.py": "0142541f00c6bf3304eaec1481da27b7b95e4a282f7ebe23aef4753f9745f35b",
}
OLD_LABEL = "targetcheck-thumbv6m-all"
OLD = f"{TRIAL}/{OLD_LABEL}"
RAW = f"{REL}/raw"
NEW = f"{RAW}/targetcheck"
CHECKER = f"{RAW}/target-check-thumbv6m.elf"
OBJECT = f"{RAW}/sub-thumbv6m.o"
GUEST = f"{RAW}/guest-thumbv6m.elf"
QEMU = f"{OFFLINE}/payload/qemu/bin/qemu-arm.xz"
TARGET_ARGS = ["--function", "tanh", "--target", "thumbv6m"]
NEW_ARGS = TARGET_ARGS + ["--chunks", "0:4096", "--jobs", "2"]
OLD_ARGS = TARGET_ARGS + ["--jobs", "2"]
WORDS = 1 << 32
END = 4096
RAW_FILES = {
    "fingerprint.json", "fingerprint.stderr", "fingerprint.stdout", "guest-build.exit",
    "guest-build.stderr", "guest-build.stdout", "guest-thumbv6m.elf", "install.log",
    "prepare-first.exit", "prepare-first.stderr", "prepare-first.stdout", "prepare.exit",
    "prepare.stderr", "prepare.stdout", "qemu.sha256", "qemu.version", "restored.json",
    "runner.exit", "runner.stderr", "runner.stdout", "sub-thumbv6m.o",
    "target-check-thumbv6m.elf", "targetcheck.json", "targetcheck.stderr", "targetcheck.stdout",
}


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def ordinary(name):
    path = ROOT / name
    require(path.is_relative_to(ROOT) and path.resolve() == path and path.is_file(),
            f"missing or non-canonical file: {name}")
    return path


def digest(name):
    with ordinary(name).open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def read(name):
    return ordinary(name).read_bytes()


def load(name):
    def unique(pairs):
        obj = dict(pairs)
        require(len(obj) == len(pairs), f"duplicate JSON key in {name}")
        return obj
    return json.loads(read(name), object_pairs_hook=unique)


def files_equal(actual, expected, label):
    require(actual == expected, f"{label} differs from required evidence")


def audit_run(stem, interpreter, args, source):
    record = load(stem + ".json")
    files_equal(record["argv"], [interpreter, "-m", "eik", *args], stem + " command")
    require(type(record["exit_code"]) is int and record["exit_code"] == 0, stem + " failed")
    files_equal(record["source_sha256"], source, stem + " source")
    for stream in ("stdout", "stderr"):
        files_equal(digest(stem + "." + stream), record[stream + "_sha256"], stem + " " + stream)
    require(not read(stem + ".stderr"), stem + " emitted unexpected stderr")
    return record, load(stem + ".stdout")


def audit_full(report):
    expected = {
        "schema": "eik-report-1", "kind": "targetcheck", "competition": "exact-integer-kernels",
        "target": "thumbv6m", "function": "tanh", "sha256": SOURCE, "fingerprint": FINGERPRINT,
        "chunk_lo": 0, "chunk_hi": END, "words_checked": WORDS, "mismatches": 0, "jobs": 2,
        "complete": True, "range_complete": True, "verdict": "passed", "stage": None, "reasons": [],
    }
    for key, value in expected.items():
        require(type(report[key]) is type(value) and report[key] == value,
                f"target report has incompatible {key}")
    image_hash = report["image_sha256"]
    require(len(image_hash) == 64 and bytes.fromhex(image_hash).hex() == image_hash,
            "invalid report image hash")


def elf(name):
    """Read the ELF32 ARM headers and sections needed for an offline equivalence check."""
    data = read(name)
    require(data[:7] == b"\x7fELF\x01\x01\x01", f"not little-endian ELF32: {name}")
    hdr = struct.unpack_from("<16sHHIIIIIHHHHHH", data)
    (_, kind, machine, _, entry, phoff, shoff, flags, _, phsize,
     phnum, shsize, shnum, strings) = hdr
    require(machine == 40 and shsize == 40 and (not phnum or phsize == 32), f"invalid ARM ELF: {name}")
    sections = [struct.unpack_from("<10I", data, shoff + i * shsize) for i in range(shnum)]

    def payload(header):
        _, section_type, _, _, offset, size, *_ = header
        if section_type == 8:  # NOBITS
            return b""
        require(offset + size <= len(data), f"section extends beyond {name}")
        return data[offset:offset + size]

    names = payload(sections[strings])
    by_name = {}
    for header in sections:
        n, section_type, attrs, address, _, size, link, info, alignment, entsize = header
        section = names[n:names.index(b"\0", n)].decode("ascii")
        require(section not in by_name, f"duplicate ELF section {section} in {name}")
        by_name[section] = ((section_type, attrs, address, size, link, info, alignment, entsize),
                            payload(header))
    programs = [struct.unpack_from("<8I", data, phoff + i * phsize) for i in range(phnum)]
    return (kind, flags, entry, programs), by_name


def elf_metadata_delta(left, right, allowed):
    left_header, left_sections = elf(left)
    right_header, right_sections = elf(right)
    files_equal(left_header, right_header, f"{left} ELF type, entry and program headers")
    files_equal(left_sections.keys(), right_sections.keys(), f"{left} section inventory")
    different = sorted(name for name in left_sections if left_sections[name] != right_sections[name])
    require(set(different) <= allowed, f"{left} has non-DWARF section differences: {different}")
    return different


def check_checker():
    (kind, _, entry, programs), sections = elf(CHECKER)
    require(kind == 2 and entry & 1, "checker must be an ARM executable with a Thumb entry")
    require(not any(p[0] in (2, 3) for p in programs), "checker is dynamically linked")
    text = sections[".text"][0]
    require(any(p[0] == 1 and p[6] & 1 and p[2] <= (entry & ~1) < p[2] + p[4] for p in programs),
            "checker entry is outside the executable load segment")
    require(text[1] & 4 and text[2] <= (entry & ~1) < text[2] + text[3], "checker entry is outside .text")
    strings = sections[".strtab"][1]
    symbols = {}
    for offset, value, size, info, _, index in struct.iter_unpack("<IIIBBH", sections[".symtab"][1]):
        if info == 0x12 and index:
            symbols[strings[offset:strings.index(b"\0", offset)].decode("ascii")] = value
    require(symbols.get("_start") == entry and "eik_tanh" in symbols, "checker lacks expected entry symbols")
    tanh = symbols["eik_tanh"]
    require(tanh & 1 and text[2] <= (tanh & ~1) < text[2] + text[3], "checker tanh is outside .text")
    require(not any(section[0][0] in (4, 9) and not name.startswith((".rel.debug", ".rela.debug"))
                    for name, section in sections.items()), "checker has non-DWARF relocations")
    return {"entry": entry, "eik_tanh": tanh, "load_headers": [list(p) for p in programs if p[0] == 1]}


def audit():
    files_equal({p.name for p in (HERE / "raw").iterdir()}, RAW_FILES, "raw artifact inventory")
    files_equal(digest(NEW + ".json"),
                "5d9e9a521f57a4c375c7605d138fb2185f5f81f918abd7e54bf2c6e2d9016b4e",
                "recorded exhaustive run")
    for name, pin in PINS.items():
        files_equal(digest(name), pin, name)
    freeze = load(f"{FREEZE}/manifest.json")
    files_equal(freeze["entry"]["sha256"], SOURCE, "freeze source")
    files_equal(freeze["evaluator"], FINGERPRINT, "freeze fingerprint")
    kit = load(f"{TOOLKIT}/manifest.json")["kit"]
    for name, pin in kit["file_hashes"].items():
        files_equal(digest(f"{TOOLKIT}/{name}"), pin, name)
    manifest = load(f"{OFFLINE}/manifest.json")
    for name, pin in manifest["toolkit_sha256"].items():
        files_equal(digest(f"{TOOLKIT}/{name}"), pin, name)
    reference = f"{TOOLKIT}/kit/reference/tanh.digest"
    files_equal(digest(reference), REFERENCE, "tanh reference")
    require(len(read(reference)) == END * 32, "tanh reference has wrong chunk count")

    deps = load(f"{TOOLKIT}/dependencies.json")
    qemu = deps["qemu"]["executables"]["qemu-arm"]
    with lzma.open(ordinary(QEMU), "rb") as stream:
        files_equal(file_digest(stream, "sha256").hexdigest(), qemu["sha256"], "retained QEMU payload")
    files_equal(read(f"{RAW}/qemu.sha256").decode().strip(), qemu["sha256"], "executed QEMU hash")
    files_equal(read(f"{RAW}/qemu.version").decode().splitlines()[0], qemu["version"], "executed QEMU version")
    install = read(f"{RAW}/install.log").decode()
    for wheel in deps["wheels"]:
        require(f'/{Path(wheel["path"]).name} sha256={wheel["sha256"]} (' in install,
                f'wheel pin missing from install log: {wheel["path"]}')
    restored = load(f"{RAW}/restored.json")
    files_equal(restored, {name: manifest["files"][name]["sha256"] for name in manifest["omitted"]},
                "restored payload pins")

    trial = load(f"{TRIAL}/packet.json")
    files_equal(trial["source"], {"path": f"{TRIAL}/entry.c", "sha256": SOURCE}, "trial source")
    prior_command = (f"python3 {TOOLKIT}/run.py test/scratch/m0-tanh-refine target {OLD_LABEL}"
                     f" targetcheck {TRIAL}/entry.c " + " ".join(OLD_ARGS))
    indexed = [item for item in trial["runs"].values() if item["command"] == prior_command]
    require(len(indexed) == 1, "prior run missing or duplicated in trial index")
    files_equal(indexed[0]["exit_code"], 0, "indexed prior exit")
    suffixes = ("json", "stdout", "stderr")
    files_equal(indexed[0]["files"], {f"{OLD_LABEL}.{ext}": digest(f"{OLD}.{ext}") for ext in suffixes},
                "indexed prior report hashes")
    old_record, old = audit_run(OLD, "$REPO/test/scratch/m0-tanh-refine/runtime/bin/python",
                                ["targetcheck", f"$REPO/{TRIAL}/entry.c", *OLD_ARGS], SOURCE)
    audit_full(old)

    runtime = f"$REPO/{SCRATCH}/work/runtime/bin/python"
    _, fp = audit_run(f"{RAW}/fingerprint", runtime, ["fingerprint", "--details"], None)
    files_equal({key: fp[key] for key in FINGERPRINT}, FINGERPRINT, "rerun fingerprint")
    files_equal(fp["kind"], "fingerprint", "fingerprint report kind")
    for kind in ("measurement", "verifier"):
        detail = fp["details"][kind]
        files_equal(sha256(json.dumps(detail, sort_keys=True).encode()).hexdigest(), FINGERPRINT[kind],
                    f"recomputed {kind} fingerprint")
        for name, pin in detail["files"].items():
            files_equal(digest(f"{TOOLKIT}/kit/{name}"), pin, name)
    tools = fp["details"]["tools"]
    require(tools["python"].startswith("3.12.") and tools["machine"] == "x86_64" and
            tools["host_cc"].startswith("gcc ") and tools["zig"] == "0.17.1", "wrong replay toolchain")

    record, fresh = audit_run(NEW, runtime, ["targetcheck", "$REPO/entry.c", *NEW_ARGS], SOURCE)
    audit_full(fresh)
    files_equal(digest(CHECKER), fresh["image_sha256"], "actually executed checker image")
    files_equal(read(f"{RAW}/runner.stdout"), read(NEW + ".stdout"), "outer runner stdout")
    files_equal(read(f"{RAW}/runner.stderr"), read(NEW + ".stderr"), "outer runner stderr")
    for label, exit_code in (("prepare-first", 1), ("prepare", 0), ("runner", 0), ("guest-build", 0)):
        files_equal(read(f"{RAW}/{label}.exit").strip(), str(exit_code).encode(), label + " exit")
    prep_failure = read(f"{RAW}/prepare-first.stderr").decode()
    require("missing or non-ordinary file:" in prep_failure and
            prep_failure.strip().endswith("/toolkit/dependencies.json"), "unexpected initial preparation failure")
    files_equal(read(f"{RAW}/prepare.stdout").decode().strip(),
                f"Prepared {len(manifest['files'])} pinned files and verified their on-disk hashes",
                "preparation stdout")

    old_images = freeze["objects"]["thumbv6m"]
    for item in old_images.values():
        files_equal(digest(item["path"]), item["sha256"], item["path"])
    object_delta = elf_metadata_delta(OBJECT, old_images["object"]["path"],
                                     {".debug_info", ".debug_str", ".debug_line", ".rel.debug_line"})
    guest_delta = elf_metadata_delta(GUEST, old_images["guest_image"]["path"],
                                    {".debug_info", ".debug_str", ".debug_line"})
    require(old["image_sha256"] != fresh["image_sha256"] and
            old["image_sha256"] != old_images["guest_image"]["sha256"],
            "prior image identity does not match the recorded audit")

    return {
        "identity": {
            "source_sha256": SOURCE, "kit_commit": kit["commit"], "reference_sha256": REFERENCE,
            "fingerprint": FINGERPRINT, "tools": tools, "qemu": qemu,
            "checker_sha256": fresh["image_sha256"], "object_sha256": digest(OBJECT),
            "guest_sha256": digest(GUEST),
        },
        "range": {
            "chunk_lo": 0, "chunk_hi": END, "words_checked": WORDS, "mismatches": 0,
            "complete": True, "range_complete": True, "provenance": "rerun",
            "raw_report": {f"{NEW}.{ext}": digest(f"{NEW}.{ext}") for ext in suffixes},
        },
        "prior": {
            "raw_report": {f"{OLD}.{ext}": digest(f"{OLD}.{ext}") for ext in suffixes},
            "argv": old_record["argv"], "exit_code": old_record["exit_code"],
            "reported_chunks": [0, END], "reported_words": WORDS, "reported_mismatches": 0,
            "reported_image_sha256": old["image_sha256"], "disposition": "excluded",
            "reason": "original linked checker unavailable and rerun checker hash differs",
        },
        "measurements": {
            "seconds": fresh["seconds"], "words_checked": WORDS, "mismatches": 0,
            "checker_elf": check_checker(), "freeze_object_dwarf_differences": object_delta,
            "freeze_guest_dwarf_differences": guest_delta,
        },
        "targetcheck_command": record["argv"],
        "dependencies": restored,
        "artifacts": {
            name: digest(name) for name in sorted({
                *PINS, QEMU, reference, f"{REL}/build-guest.py", *[item["path"] for item in old_images.values()],
                *[f"{OLD}.{ext}" for ext in suffixes],
                *[p.relative_to(ROOT).as_posix() for p in (HERE / "raw").iterdir()],
            })
        },
    }


def commands(audited):
    scratch = SCRATCH
    prefix = ["python3.12", f"{TOOLKIT}/run.py", "--dependencies", f"{scratch}/dependencies", f"{scratch}/work"]
    prepare = ["python3.12", f"{scratch}/offline-runtime/prepare.py", f"{scratch}/dependencies"]
    return [
        {"argv": prepare, "exit_code": 1, "stderr": f"{RAW}/prepare-first.stderr",
         "detail": "prepare.py rejected the symlink to the pinned toolkit"},
        {"argv": prepare, "exit_code": 0, "stdout": f"{RAW}/prepare.stdout",
         "detail": "retried with an ordinary scratch copy of the pinned toolkit"},
        {"argv": [f"{scratch}/dependencies/qemu/bin/qemu-arm", "--version"], "exit_code": 0,
         "stdout": f"{RAW}/qemu.version"},
        {"argv": [*prefix, "exhaustive", "targetcheck", "targetcheck", "entry.c", *NEW_ARGS],
         "exit_code": 0, "record": NEW + ".json"},
        {"argv": audited["targetcheck_command"], "exit_code": 0, "record": NEW + ".json"},
        {"argv": [*prefix, "runtime-identity", "fingerprint", "fingerprint", "--details"],
         "exit_code": 0, "record": f"{RAW}/fingerprint.json"},
        {"argv": [f"{scratch}/work/runtime/bin/python", "-B", f"{scratch}/build-guest.py",
                  f"{scratch}/work/cases/exhaustive"], "exit_code": 0, "stdout": f"{RAW}/guest-build.stdout"},
    ]


def manifests(audited):
    summary = {
        "schema": 1, "status": "pass", "function": "tanh", "runtime": "thumbv6m",
        "chunk_words": 1 << 20, "identities": audited["identity"], "gaps": [], "failures": [],
    }
    coverage = {
        **summary, "ranges": [audited["range"]], "reused_chunks": 0, "rerun_chunks": END,
        "words_checked": WORDS, "prior_audit": audited["prior"],
    }
    result = {
        **summary, "commands": commands(audited), "measurements": audited["measurements"],
        "restored_dependencies": audited["dependencies"],
        "artifacts": {**audited["artifacts"], f"{REL}/coverage.json": digest(f"{REL}/coverage.json")},
    }
    return coverage, result


def verify():
    coverage, result = manifests(audit())
    files_equal(load(f"{REL}/coverage.json"), coverage, "coverage manifest")
    files_equal(load(f"{REL}/result.json"), result, "result manifest")
    print("PASS thumbv6m/tanh: chunks [0,4096), 4294967296 words, zero mismatches; rerun checker hash verified")


if __name__ == "__main__":
    try:
        verify()
    except (ValueError, IndexError, KeyError, TypeError, OSError, EOFError, struct.error) as exc:
        print(f"FAIL thumbv6m/tanh: {exc}", file=sys.stderr)
        sys.exit(1)
