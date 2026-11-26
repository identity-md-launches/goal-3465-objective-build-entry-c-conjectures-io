#!/usr/bin/env python3
"""Offline verifier for the exhaustive thumbv6m/exp coverage packet.

Standard library only. Run from anywhere: paths are resolved from this file.

It rejects: missing or tampered evidence (every artifact hash), a report whose
stdout/stderr bytes do not match its run record, a run record not bound to the
frozen source and the exact targetcheck command, a report whose fields do not say
"every chunk of [0,4096) matched the pinned reference with zero mismatches", an
image_sha256 that is not the SHA-256 of the retained linked image, an image whose
entry symbol / entry points / allocated sections differ from what the packet
recorded, an entry object whose allocated sections differ from the frozen build,
pinned identities (fingerprint, QEMU, toolkit files) that disagree with the
repository's independent records, gaps or overlaps in the selected chunk ranges,
a prior report counted without image binding, and a "pass" status that the
evidence does not support.  Exit 0 means every check passed.
"""
import json
import re
import struct
import sys
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCOPE = HERE.relative_to(ROOT).as_posix()

SOURCE_SHA = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
FUNCTION = "exp"
TARGET = "thumbv6m"
CHUNKS = 4096
CHUNK_WORDS = 1 << 20
DOMAIN_WORDS = CHUNKS * CHUNK_WORDS  # 4294967296
ENTRY_POINTS = ("eik_sigmoid", "eik_tanh", "eik_exp")
PRIOR_DIR = "eik-work/trials/m0-tanh-refine"
HEX64 = re.compile(r"^[0-9a-f]{64}$")

TARGETCHECK_ARGV_TAIL = ["targetcheck", "$REPO/entry.c", "--function", FUNCTION, "--target", TARGET,
                         "--chunks", f"0:{CHUNKS}", "--jobs", "2"]


class Fail(Exception):
    pass


def require(condition, message):
    if not condition:
        raise Fail(message)


def sha(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    path = Path(path)
    require(path.is_file(), f"missing file: {path}")
    return json.loads(path.read_bytes())


# ------------------------------------------------------------------ ELF32 (LE)
def elf(path):
    """Header, all section headers, allocated-section hashes, writable allocated
    sections and GLOBAL symbols of a little-endian ELF32 file."""
    b = Path(path).read_bytes()
    require(b[:4] == b"\x7fELF" and b[4] == 1 and b[5] == 1, f"{path}: not a little-endian ELF32 file")
    e_type, e_machine = struct.unpack_from("<HH", b, 16)
    e_entry, = struct.unpack_from("<I", b, 0x18)
    shoff, = struct.unpack_from("<I", b, 0x20)
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 0x2E)
    require(shentsize == 40 and shnum and shstrndx < shnum, f"{path}: bad section header table")
    hs = [struct.unpack_from("<IIIIIIIIII", b, shoff + i * shentsize) for i in range(shnum)]
    st = hs[shstrndx]
    names = b[st[4]:st[4] + st[5]]

    def name_at(table, off):
        return table[off:table.index(b"\0", off)].decode()

    sections = [{"name": name_at(names, h[0]), "type": h[1], "flags": h[2], "addr": h[3],
                 "offset": h[4], "size": h[5], "link": h[6]} for h in hs]
    alloc, writable = {}, []
    for s in sections:
        if s["flags"] & 2 and s["type"] != 8:  # SHF_ALLOC and not SHT_NOBITS
            require(s["offset"] + s["size"] <= len(b), f"{path}: section {s['name']} past end of file")
            alloc[s["name"]] = {"size": s["size"],
                                "sha256": sha256(b[s["offset"]:s["offset"] + s["size"]]).hexdigest()}
        if s["flags"] & 1 and s["flags"] & 2 and s["size"]:  # writable allocated (incl. NOBITS)
            writable.append(s["name"])
    symbols = {}
    for s in sections:
        if s["type"] == 2:  # SHT_SYMTAB
            strtab = sections[s["link"]]
            table = b[strtab["offset"]:strtab["offset"] + strtab["size"]]
            for i in range(s["size"] // 16):
                st_name, st_value, st_size, st_info, _other, st_shndx = struct.unpack_from(
                    "<IIIBBH", b, s["offset"] + i * 16)
                name = name_at(table, st_name) if st_name else ""
                if name and (st_info >> 4) == 1:  # STB_GLOBAL
                    symbols[name] = {"value": st_value, "size": st_size, "type": st_info & 0xF,
                                     "shndx": st_shndx}
    return {"type": e_type, "machine": e_machine, "entry": e_entry, "sections": sections,
            "alloc": alloc, "writable": writable, "symbols": symbols}


def section(info, name):
    for s in info["sections"]:
        if s["name"] == name:
            return s
    raise Fail(f"section {name} absent")


# ------------------------------------------------------------- report checks
def check_record(record_path, stdout_path, stderr_path, argv_tail, source_sha):
    rec = load(record_path)
    require(rec["exit_code"] == 0, f"{record_path}: exit code {rec['exit_code']}")
    require(sha(stdout_path) == rec["stdout_sha256"], f"{stdout_path}: bytes differ from the run record")
    require(sha(stderr_path) == rec["stderr_sha256"], f"{stderr_path}: bytes differ from the run record")
    require(rec["source_sha256"] == source_sha, f"{record_path}: source hash not bound")
    argv = rec["argv"]
    require(argv[0].endswith("/runtime/bin/python") and argv[1:3] == ["-m", "eik"],
            f"{record_path}: argv is not the pinned runtime running the kit")
    require(argv[3:] == argv_tail, f"{record_path}: argv {argv[3:]} is not {argv_tail}")
    return rec


def check_report(rep, lo, hi, fingerprint, where):
    require(rep.get("schema") == "eik-report-1" and rep.get("kind") == "targetcheck"
            and rep.get("competition") == "exact-integer-kernels", f"{where}: not a targetcheck report")
    require(rep["function"] == FUNCTION and rep["target"] == TARGET, f"{where}: wrong function/target")
    require(rep["sha256"] == SOURCE_SHA, f"{where}: report source hash is not the frozen source")
    require(rep["fingerprint"] == fingerprint, f"{where}: fingerprint differs from the pinned identity")
    require(rep["chunk_lo"] == lo and rep["chunk_hi"] == hi and 0 <= lo < hi <= CHUNKS,
            f"{where}: chunk range is not [{lo},{hi})")
    require(rep["verdict"] == "passed" and rep["mismatches"] == 0 and rep["stage"] is None
            and rep["reasons"] == [], f"{where}: verdict/mismatches/stage/reasons do not say passed")
    require(rep["range_complete"] is True, f"{where}: range_complete is not true")
    require(rep["complete"] is ((lo, hi) == (0, CHUNKS)), f"{where}: complete flag inconsistent with range")
    require(rep["words_checked"] == (hi - lo) * CHUNK_WORDS, f"{where}: words_checked != (hi-lo)<<20")
    require(HEX64.match(rep["image_sha256"]), f"{where}: image_sha256 malformed")
    require(isinstance(rep["jobs"], int) and rep["jobs"] >= 1, f"{where}: jobs malformed")


def covered(ranges):
    """Half-open chunk ranges must tile [0, CHUNKS) exactly once."""
    require(ranges, "no ranges selected")
    ordered = sorted((r["chunk_lo"], r["chunk_hi"]) for r in ranges)
    position = 0
    for lo, hi in ordered:
        require(lo == position, f"gap or overlap at chunk {position}: next range starts at {lo}")
        require(hi > lo, f"empty range [{lo},{hi})")
        position = hi
    require(position == CHUNKS, f"ranges end at chunk {position}, not {CHUNKS}")
    require(sum(r["words"] for r in ranges) == DOMAIN_WORDS, "words do not sum to 2^32")
    require(sum(r["mismatches"] for r in ranges) == 0, "nonzero mismatches in a claimed pass")


# -------------------------------------------------------------------- main
def verify():
    result = load(HERE / "result.json")
    require(result["status"] in {"pass", "fail", "incomplete"}, "result.json status malformed")
    require(result["function"] == FUNCTION and result["target"] == TARGET, "result.json function/target")

    # 1. every artifact exists with its recorded hash (paths are repository-relative)
    artifacts = result["artifacts"]
    require(f"{SCOPE}/coverage.json" in artifacts, "coverage.json is not listed as an artifact")
    for rel, digest in artifacts.items():
        p = ROOT / rel
        require(p.is_file() and not p.is_symlink(), f"artifact missing or not a regular file: {rel}")
        require(sha(p) == digest, f"artifact tampered or stale: {rel}")
    cov = load(HERE / "coverage.json")
    require(cov["schema"] == "eik-coverage-packet-1", "coverage.json schema")
    require(cov["function"] == FUNCTION and cov["target"] == TARGET, "coverage.json function/target")
    require(cov["status"] == result["status"], "coverage.json and result.json disagree on status")
    require(cov["domain"] == {"chunks": CHUNKS, "chunk_words": CHUNK_WORDS, "words": DOMAIN_WORDS},
            "domain description")

    # 2. frozen source
    require(cov["source"] == {"path": "entry.c", "sha256": SOURCE_SHA}, "coverage.json source pin")
    require(sha(ROOT / "entry.c") == SOURCE_SHA, "root entry.c is not the frozen source")
    require(sha(ROOT / PRIOR_DIR / "entry.c") == SOURCE_SHA, "trial entry.c is not the frozen source")

    # 3. pinned identities cross-checked against independent repository records
    pins = cov["pinned"]
    fingerprint = pins["fingerprint"]
    freeze = load(ROOT / "eik-work/freeze/manifest.json")
    require(freeze["evaluator"] == fingerprint, "pinned fingerprint differs from eik-work/freeze/manifest.json")
    require(freeze["entry"]["sha256"] == SOURCE_SHA, "freeze manifest source differs")
    deps = load(ROOT / "eik-work/toolkit/dependencies.json")
    qemu = deps["qemu"]["executables"]["qemu-arm"]
    require(pins["qemu_arm"] == {"sha256": qemu["sha256"], "version": qemu["version"]},
            "pinned qemu-arm differs from toolkit/dependencies.json")
    require(pins["kit_commit"] == freeze["kit"]["commit"], "kit commit pin differs from freeze manifest")
    for rel, digest in pins["toolkit_identity"].items():
        require(sha(ROOT / rel) == digest, f"toolkit identity file changed: {rel}")
    for name in ("eik-work/toolkit/run.py", "eik-work/toolkit/provision.py", "eik-work/toolkit/dependencies.json",
                 "eik-work/toolkit/kit/reference/exp.digest", "eik-work/toolkit/kit/harness/target_check.c",
                 "eik-work/toolkit/kit/eik/stages.py", "eik-work/toolkit/kit/eik/toolchain.py",
                 "eik-work/toolkit/kit/eik/config.py", "eik-work/offline-runtime/prepare.py"):
        require(name in pins["toolkit_identity"], f"toolkit identity does not pin {name}")
    require(sha(ROOT / "eik-work/toolkit/kit/reference/exp.digest") == pins["reference_exp_digest_sha256"],
            "reference exp.digest pin")
    require((ROOT / "eik-work/toolkit/kit/reference/exp.digest").stat().st_size == CHUNKS * 32,
            "reference exp.digest is not 4096 chunk digests")

    # 4. the new (rerun) set: run record, report, image, object
    new = cov["sets"]["new"]
    require(new["provenance"] == "rerun", "new set provenance")
    files = {k: HERE / v["path"] for k, v in new["files"].items()}
    for k, v in new["files"].items():
        require(f"{SCOPE}/{v['path']}" in artifacts and artifacts[f"{SCOPE}/{v['path']}"] == v["sha256"],
                f"new set file not an artifact or hash mismatch: {k}")
    rec = check_record(files["record"], files["report"], files["stderr"], TARGETCHECK_ARGV_TAIL, SOURCE_SHA)
    require(new["exit_code"] == rec["exit_code"] == 0, "new set exit code")
    require(new["command"].split()[:3] == ["python3", "eik-work/toolkit/run.py", "--dependencies"]
            and new["command"].split()[-10:] == ["targetcheck", "entry.c", "--function", FUNCTION, "--target",
                                                 TARGET, "--chunks", f"0:{CHUNKS}", "--jobs", "2"],
            "new set command is not the required targetcheck command")
    rep = json.loads(files["report"].read_bytes())
    check_report(rep, 0, CHUNKS, fingerprint, "new report")
    require(rep["jobs"] == 2, "new report jobs != 2")
    require(new["ranges"] == [{"chunk_lo": 0, "chunk_hi": CHUNKS, "words": DOMAIN_WORDS, "mismatches": 0,
                               "report": new["files"]["report"]["path"]}], "new set ranges do not match the report")
    require(new["report_facts"] == {k: rep[k] for k in ("complete", "range_complete", "chunk_lo", "chunk_hi",
                                                          "words_checked", "mismatches", "verdict", "jobs",
                                                          "seconds", "budget_seconds", "image_sha256")},
            "new set report_facts differ from the report")

    # image binding: the retained linked image IS the hashed image
    img_rec = new["image"]
    img_path = HERE / img_rec["path"]
    require(sha(img_path) == rep["image_sha256"] == img_rec["sha256"],
            "image_sha256 is not the SHA-256 of the retained target-check-thumbv6m.elf")
    image = elf(img_path)
    require(image["type"] == 2 and image["machine"] == 40, "image is not an ARM ELF executable")
    require(image["alloc"] == img_rec["sections"], "image allocated sections differ from the recorded hashes")
    text = section(image, ".text")
    require(text["addr"] <= image["entry"] < text["addr"] + text["size"], "entry point outside .text")
    start = image["symbols"].get("_start")
    require(start and start["value"] == image["entry"] == img_rec["entry_address"], "entry symbol is not _start")
    require(img_rec["entry_symbol"] == "_start", "recorded entry symbol")
    for ep in ENTRY_POINTS:
        s = image["symbols"].get(ep)
        require(s and s["type"] == 2 and text["addr"] <= s["value"] < text["addr"] + text["size"],
                f"{ep} is not a global function inside the image .text")
        require(img_rec["entry_points"][ep] == {"address": s["value"], "size": s["size"]},
                f"recorded entry point {ep} differs")
    require(image["writable"] == [".bss"], f"image writable allocated sections {image['writable']} != ['.bss']")
    require(section(image, ".bss")["size"] == 4 * CHUNK_WORDS, ".bss is not the 4 MiB harness chunk buffer")

    obj_rec = new["object"]
    obj_path = HERE / obj_rec["path"]
    require(sha(obj_path) == obj_rec["sha256"], "entry object hash")
    obj = elf(obj_path)
    require(obj["type"] == 1 and obj["machine"] == 40, "entry object is not an ARM relocatable")
    require(obj["alloc"] == obj_rec["sections"], "object allocated sections differ from the recorded hashes")
    require(obj["writable"] == [], "entry object has writable allocated data")
    for ep in ENTRY_POINTS:
        require(obj["symbols"][ep]["size"] == image["symbols"][ep]["size"],
                f"{ep} has a different size in object and image")
    globals_defined = {n for n, s in obj["symbols"].items() if s["shndx"] != 0}
    require(globals_defined == set(ENTRY_POINTS), f"object exports {sorted(globals_defined)}")

    # equivalence of executable sections with the frozen build (independent record)
    eq = new["object_equivalence_to_freeze"]
    fz = freeze["objects"][TARGET]["object"]
    require(eq["freeze_object"] == fz["path"] and eq["freeze_sha256"] == fz["sha256"], "freeze object reference")
    require(sha(ROOT / fz["path"]) == fz["sha256"], "frozen object bytes changed")
    frozen = elf(ROOT / fz["path"])
    require(frozen["alloc"] == fz["sections"], "freeze manifest section record does not match the frozen object")
    require(frozen["alloc"] == obj["alloc"], "allocated sections of the rebuilt object differ from the frozen build")
    require(eq["sections_equal"] is True and eq["file_bytes_equal"] is (sha(obj_path) == fz["sha256"]),
            "object equivalence flags inconsistent")

    # fingerprint run of the same runtime
    fp_files = {k: HERE / v["path"] for k, v in new["fingerprint_run"]["files"].items()}
    check_record(fp_files["record"], fp_files["report"], fp_files["stderr"], ["fingerprint"], None)
    fp_rep = json.loads(fp_files["report"].read_bytes())
    require({k: fp_rep[k] for k in ("measurement", "verifier", "sandbox")} == fingerprint,
            "fingerprint run disagrees with the pinned identity")
    rec_dir = Path(rec["argv"][0]).parent.parent
    require(Path(load(fp_files["record"])["argv"][0]).parent.parent == rec_dir,
            "fingerprint and targetcheck ran in different runtimes")

    # runtime preparation evidence
    prep = (HERE / new["runtime"]["prepare_stdout"]).read_text()
    require("Prepared 33 pinned files and verified their on-disk hashes" in prep, "prepare.py did not succeed")
    install = (HERE / new["runtime"]["install_log"]).read_text()
    for wheel in deps["wheels"]:
        require(f"sha256={wheel['sha256']}" in install and "every member checked against RECORD" in install,
                f"install log does not show the pinned wheel {wheel['path']}")
    require("import probe -> 0" in install, "runtime import probe did not pass")
    for name, digest in new["runtime"]["restored_payloads"].items():
        require(deps_pin(deps, name) == digest, f"restored payload {name} is not the pinned hash")

    # 5. prior set: internally consistent, indexed, but not bound and not counted
    prior = cov["sets"]["prior"]
    require(prior["provenance"] == "reused-candidate" and prior["counted"] is False, "prior set must not be counted")
    packet = load(ROOT / prior["indexed_by"])
    run = packet["runs"][prior["run_key"]]
    require(run["exit_code"] == 0, "prior run exit code")
    require(set(run["files"]) == set(prior["files"]), "prior file list differs from packet index")
    for name, digest in run["files"].items():
        p = ROOT / PRIOR_DIR / name
        require(sha(p) == digest == prior["files"][name], f"prior raw file hash mismatch: {name}")
        require(f"{PRIOR_DIR}/{name}" in artifacts, f"prior raw file not listed as artifact: {name}")
    prec = load(ROOT / PRIOR_DIR / (prior["run_key"] + ".json"))
    require(prec["source_sha256"] == SOURCE_SHA and prec["argv"][3:5] == ["targetcheck", f"$REPO/{PRIOR_DIR}/entry.c"]
            and prec["argv"][5:] == ["--function", FUNCTION, "--target", TARGET, "--jobs", "1"],
            "prior run record binding")
    require(sha(ROOT / PRIOR_DIR / (prior["run_key"] + ".stdout")) == prec["stdout_sha256"], "prior stdout binding")
    prep_rep = json.loads((ROOT / PRIOR_DIR / (prior["run_key"] + ".stdout")).read_bytes())
    check_report(prep_rep, 0, CHUNKS, fingerprint, "prior report")
    binding = prior["binding"]
    require(binding["image_sha256"] == prep_rep["image_sha256"] and binding["bound"] is False, "prior binding")
    candidates = list((HERE / "objects").iterdir()) + list((ROOT / "eik-work/freeze/evidence/objects").iterdir())
    for p in candidates:
        require(sha(p) != binding["image_sha256"], f"{p} matches the prior image hash; binding claim is wrong")
    require(binding["image_sha256"] != rep["image_sha256"], "prior and new images unexpectedly identical")

    # 6. coverage from the selected set only
    require(cov["selected_set"] == "new", "selected set must be the bound rerun")
    covered(cov["sets"][cov["selected_set"]]["ranges"])
    require(cov["coverage"] == {"words_checked": DOMAIN_WORDS, "chunks_checked": CHUNKS, "mismatches": 0,
                                "ranges": [[0, CHUNKS]]}, "coverage summary")

    # 7. commands and status
    names = [c["name"] for c in result["commands"]]
    require(names == ["prepare", "fingerprint", "targetcheck"], f"commands {names}")
    require(all(c["exit_code"] == 0 for c in result["commands"]), "a recorded command failed")
    require(result["commands"][2]["command"] == new["command"], "result/coverage command mismatch")
    require(cov["failures"] == [] and cov["gaps"] == [] and result["gaps"] == [], "failures or gaps recorded")
    require(result["measured_facts"]["words_checked"] == DOMAIN_WORDS
            and result["measured_facts"]["mismatches"] == 0
            and result["measured_facts"]["image_sha256"] == rep["image_sha256"], "measured facts")
    require(result["status"] == "pass", "evidence supports a pass but status is not pass")


def deps_pin(deps, name):
    for item in [*deps["wheels"], *deps["qemu"]["source_archives"]]:
        if item["path"] == name:
            return item["sha256"]
    raise Fail(f"{name} is not a pinned dependency")


def main():
    try:
        verify()
    except Fail as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    except (OSError, KeyError, ValueError, TypeError, IndexError) as exc:
        print(f"FAIL: evidence unreadable: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"OK: {TARGET}/{FUNCTION} exhaustive coverage packet verified: {DOMAIN_WORDS} words, "
          f"chunks [0,{CHUNKS}), 0 mismatches, image bound to retained target-check-{TARGET}.elf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
