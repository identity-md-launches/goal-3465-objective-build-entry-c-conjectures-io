#!/usr/bin/env python3
"""Offline verifier for the rv32im/sigmoid exhaustive target coverage packet.

Standard library only. Run from the repository root:
    python3 eik-work/final-validation/coverage/rv32im-sigmoid/verify.py

Exits 0 only when the evidence is present, untampered and supports the
status claimed in result.json. A claimed "pass" additionally needs complete,
gap-free, overlap-free coverage of chunks [0,4096) with zero mismatches, a
report bound to the retained linked image, and identities that match the
pinned toolkit. A non-pass status is accepted when its evidence is intact.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REL = "eik-work/final-validation/coverage/rv32im-sigmoid"
ENTRY_SHA = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
FUNCTION, TARGET = "sigmoid", "rv32im"
CHUNKS = 4096
WORDS_PER_CHUNK = 1 << 20
DOMAIN = 1 << 32
EMPTY = hashlib.sha256(b"").hexdigest()
PRIOR = "eik-work/trials/m0-tanh-refine"
PRIOR_STEM = "targetcheck-rv32im-sigmoid-all"


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
    except (OSError, ValueError) as exc:
        raise Fail(f"cannot read JSON {path}: {exc}")


def repo_path(rel):
    p = (REPO / rel).resolve()
    need(str(p).startswith(str(REPO) + "/"), f"path escapes repository: {rel}")
    need(p.is_file(), f"missing file: {rel}")
    return p


def elf32(path):
    """Minimal ELF32 little-endian parser: header, LOAD segments, allocated sections, symbols."""
    b = Path(path).read_bytes()
    need(len(b) > 52 and b[:4] == b"\x7fELF" and b[4] == 1 and b[5] == 1, f"not an ELF32 LE file: {path}")
    (e_type, e_machine, _, e_entry, e_phoff, e_shoff, _, ehsize, phentsz, phnum,
     shentsz, shnum, shstrndx) = struct.unpack_from("<HHIIIIIHHHHHH", b, 16)
    segs = []
    for i in range(phnum):
        p_type, off, va, _, fsz, msz, flg, _ = struct.unpack_from("<8I", b, e_phoff + i * phentsz)
        if p_type == 1:
            body = b[off:off + fsz]
            # bytes after the ELF file header and program headers when the segment starts at offset 0
            skip = (e_phoff + phnum * phentsz) if off == 0 else 0
            segs.append({"vaddr": va, "offset": off, "filesz": fsz, "memsz": msz, "flags": flg,
                         "sha256": hashlib.sha256(body).hexdigest(),
                         "sha256_after_headers": hashlib.sha256(body[skip:]).hexdigest()})
    shs = [struct.unpack_from("<10I", b, e_shoff + i * shentsz) for i in range(shnum)]
    stroff = shs[shstrndx][4]

    def name_at(base, o):
        return b[base + o:b.index(b"\0", base + o)].decode()

    secs, syms, rel = [], {}, 0
    for s in shs:
        n, typ, flg, addr, off, size = s[:6]
        if typ in (4, 9):
            rel += 1
        if flg & 2:
            secs.append({"name": name_at(stroff, n), "addr": addr, "size": size, "flags": flg,
                         "sha256": None if typ == 8 else hashlib.sha256(b[off:off + size]).hexdigest()})
        if typ == 2:
            st = shs[s[6]][4]
            for j in range(size // 16):
                stn, val, sz, _, _, _ = struct.unpack_from("<IIIBBH", b, off + j * 16)
                nm = name_at(st, stn)
                if nm in ("_start", "eik_sigmoid", "eik_tanh", "eik_exp"):
                    syms[nm] = {"value": val, "size": sz}
    return {"e_type": e_type, "e_machine": e_machine, "entry": e_entry, "load_segments": segs,
            "alloc_sections": secs, "symbols": dict(sorted(syms.items())), "relocation_sections": rel}


def check_report(rep, lo, hi, label):
    need(rep.get("schema") == "eik-report-1", f"{label}: schema")
    need(rep.get("kind") == "targetcheck", f"{label}: kind")
    need(rep.get("competition") == "exact-integer-kernels", f"{label}: competition")
    need(rep.get("function") == FUNCTION and rep.get("target") == TARGET, f"{label}: function/target")
    need(rep.get("sha256") == ENTRY_SHA, f"{label}: source sha256")
    need((rep.get("chunk_lo"), rep.get("chunk_hi")) == (lo, hi), f"{label}: chunk range")
    need(rep.get("verdict") == "passed", f"{label}: verdict {rep.get('verdict')!r}")
    need(rep.get("complete") is True and rep.get("range_complete") is True, f"{label}: complete flags")
    need(rep.get("mismatches") == 0, f"{label}: mismatches {rep.get('mismatches')!r}")
    need(rep.get("reasons") == [], f"{label}: reasons {rep.get('reasons')!r}")
    need(rep.get("words_checked") == (hi - lo) * WORDS_PER_CHUNK, f"{label}: words_checked")


def main():
    result = load(HERE / "result.json")
    cov = load(HERE / "coverage.json")
    status = result.get("status")
    need(status in ("pass", "fail", "incomplete"), f"bad status {status!r}")
    need(cov.get("status") == status, "coverage.json and result.json disagree on status")
    need(cov.get("function") == FUNCTION and cov.get("target") == TARGET, "coverage function/target")

    # 1. every listed artifact exists with its recorded hash; required ones are listed
    arts = result.get("artifacts")
    need(isinstance(arts, dict) and arts, "artifacts missing")
    for rel, digest in arts.items():
        need(rel.startswith(REL + "/"), f"artifact outside packet: {rel}")
        need(sha(repo_path(rel)) == digest, f"artifact hash mismatch: {rel}")
    need(arts.get(f"{REL}/coverage.json") == sha(HERE / "coverage.json"), "coverage.json not bound")
    actual = {f"{REL}/{p.relative_to(HERE)}" for p in HERE.rglob("*") if p.is_file()}
    extra = actual - set(arts) - {f"{REL}/result.json", f"{REL}/verify.py"}
    need(not {p for p in extra if "__pycache__" not in p}, f"unlisted files in packet: {sorted(extra)}")

    # 2. source and toolkit identities (current repository bytes)
    ids = result.get("identities", {})
    need(sha(repo_path("entry.c")) == ENTRY_SHA, "root entry.c is not the frozen source")
    need(ids.get("source", {}).get("sha256") == ENTRY_SHA, "recorded source identity")
    for rel, digest in ids.get("toolkit_files", {}).items():
        need(sha(repo_path(rel)) == digest, f"toolkit identity changed: {rel}")
    for rel in ("eik-work/toolkit/run.py", "eik-work/toolkit/manifest.json",
                "eik-work/toolkit/kit/requirements.txt", "eik-work/toolkit/kit/RULES.md"):
        need(rel in ids.get("toolkit_files", {}), f"toolkit identity not recorded: {rel}")
    manifest = load(repo_path("eik-work/toolkit/manifest.json"))
    pinned = None
    stack = [manifest]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            if x.get("kind") == "fingerprint" and "measurement" in x and "verifier" in x:
                pinned = {"measurement": x["measurement"], "verifier": x["verifier"]}
                break
            stack.extend(x.values())
        elif isinstance(x, list):
            stack.extend(x)
    need(pinned is not None, "pinned fingerprint not found in toolkit manifest")
    need(ids.get("fingerprint", {}).get("measurement") == pinned["measurement"]
         and ids.get("fingerprint", {}).get("verifier") == pinned["verifier"], "recorded fingerprint != pinned")

    # 3. prior evidence audit (recomputed; it must not be claimed as reused without an image)
    packet = load(repo_path(f"{PRIOR}/packet.json"))
    run = packet["runs"][PRIOR_STEM]
    for name, digest in run["files"].items():
        need(sha(repo_path(f"{PRIOR}/{name}")) == digest, f"prior raw hash mismatch: {name}")
    prior_rep = load(repo_path(f"{PRIOR}/{PRIOR_STEM}.stdout"))
    prior_cmd = load(repo_path(f"{PRIOR}/{PRIOR_STEM}.json"))
    need(prior_cmd["stdout_sha256"] == sha(repo_path(f"{PRIOR}/{PRIOR_STEM}.stdout")), "prior stdout binding")
    audit = cov.get("prior_audit", {})
    need(audit.get("image_sha256") == prior_rep.get("image_sha256"), "prior image hash misrecorded")
    need(audit.get("exit_code") == prior_cmd.get("exit_code") == run.get("exit_code"), "prior exit misrecorded")
    if audit.get("reused"):
        img = audit.get("image_path")
        need(img and sha(repo_path(img)) == prior_rep.get("image_sha256"), "prior reuse claimed without bound image")

    # 4. coverage ranges
    ranges = cov.get("ranges")
    need(isinstance(ranges, list) and ranges, "no ranges")
    ranges = sorted(ranges, key=lambda r: r["chunk_lo"])
    total = 0
    prev_hi = 0
    gaps = []
    for r in ranges:
        lo, hi = r["chunk_lo"], r["chunk_hi"]
        need(isinstance(lo, int) and isinstance(hi, int) and 0 <= lo < hi <= CHUNKS, f"bad range {lo}:{hi}")
        need(lo >= prev_hi, f"overlapping ranges at {lo}")
        if lo > prev_hi:
            gaps.append([prev_hi, lo])
        prev_hi = hi
        label = f"range {lo}:{hi}"
        need(r.get("provenance") in ("rerun", "reused"), f"{label}: provenance")
        if r["provenance"] == "reused":
            need(audit.get("reused") is True, f"{label}: reuse without accepted prior audit")
        rep_path = repo_path(r["report"]["path"])
        need(sha(rep_path) == r["report"]["sha256"], f"{label}: report hash")
        rep = load(rep_path)
        check_report(rep, lo, hi, label)
        need(r.get("words") == rep["words_checked"] and r.get("mismatches") == 0, f"{label}: counts")
        need(rep["fingerprint"].get("measurement") == pinned["measurement"]
             and rep["fingerprint"].get("verifier") == pinned["verifier"], f"{label}: fingerprint")
        # command binding
        log = load(repo_path(r["command_log"]["path"]))
        need(sha(repo_path(r["command_log"]["path"])) == r["command_log"]["sha256"], f"{label}: log hash")
        need(log.get("exit_code") == 0 and r.get("exit_code") == 0, f"{label}: exit code")
        need(log.get("source_sha256") == ENTRY_SHA, f"{label}: command source")
        argv = log.get("argv", [])
        expect = ["-m", "eik", "targetcheck", "$REPO/entry.c", "--function", FUNCTION, "--target", TARGET,
                  "--chunks", f"{lo}:{hi}"]
        need(argv[1:1 + len(expect)] == expect, f"{label}: argv {argv}")
        for stream in ("stdout", "stderr"):
            sp = repo_path(r["command_log"][stream])
            need(sha(sp) == log.get(f"{stream}_sha256"), f"{label}: {stream} binding")
        # image binding
        img = repo_path(r["image"]["path"])
        need(sha(img) == rep["image_sha256"] == r["image"]["sha256"], f"{label}: image_sha256 not the retained image")
        info = elf32(img)
        need(info["e_machine"] == 243 and info["e_type"] == 2, f"{label}: image is not a RISC-V executable")
        need("eik_sigmoid" in info["symbols"] and info["symbols"].get("_start", {}).get("value") == info["entry"],
             f"{label}: entry symbols")
        need(info == r["image"]["elf"], f"{label}: recorded ELF identity differs from image")
        for obj in r.get("objects", []):
            need(sha(repo_path(obj["path"])) == obj["sha256"], f"{label}: object hash {obj['path']}")
        total += rep["words_checked"]
    if prev_hi < CHUNKS:
        gaps.append([prev_hi, CHUNKS])
    need(cov.get("gaps") == gaps, f"recorded gaps {cov.get('gaps')} != computed {gaps}")
    need(cov.get("words_checked") == total, "recorded word total")
    failures = cov.get("failures")
    need(isinstance(failures, list), "failures list missing")

    # 5. path-only reproduction evidence (optional but checked when present)
    rp = cov.get("path_reproduction")
    if rp:
        a = elf32(repo_path(ranges[0]["image"]["path"]))
        b = elf32(repo_path(rp["image"]["path"]))
        need(sha(repo_path(rp["image"]["path"])) == rp["image"]["sha256"], "reproduction image hash")
        need(a["entry"] == b["entry"] and a["symbols"] == b["symbols"] and a["alloc_sections"] == b["alloc_sections"]
             and a["relocation_sections"] == b["relocation_sections"], "reproduction differs in executable content")
        for x, y in zip(a["load_segments"], b["load_segments"]):
            need({k: v for k, v in x.items() if k != "sha256"} == {k: v for k, v in y.items() if k != "sha256"},
                 "reproduction load segment differs beyond ELF headers")

    if status == "pass":
        need(gaps == [] and total == DOMAIN and failures == [], "pass claimed without complete coverage")
        need(all(r["provenance"] == "rerun" or audit.get("reused") for r in ranges), "unsupported provenance")
    else:
        need(gaps or failures, f"status {status} recorded without a gap or failure")
    print(f"rv32im/sigmoid coverage packet verified: status={status}, words={total}, gaps={gaps}, "
          f"failures={len(failures)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fail as exc:
        print(f"verify.py: REJECTED: {exc}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        print(f"verify.py: REJECTED: malformed evidence: {exc!r}", file=sys.stderr)
        sys.exit(1)
