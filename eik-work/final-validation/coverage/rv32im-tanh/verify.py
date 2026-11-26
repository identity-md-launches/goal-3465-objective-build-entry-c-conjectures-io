#!/usr/bin/env python3
"""Offline verifier for the rv32im/tanh exhaustive target-coverage packet (standard library only).

Run from the repository root: python3 eik-work/final-validation/coverage/rv32im-tanh/verify.py
Exit 0 only when result.json and coverage.json agree with the retained raw evidence: every
artifact digest, the frozen source, the command/source binding of each raw record, fingerprints
against the pinned toolkit manifest and prior run, the linked image hash against the retained
image bytes, executable equivalence of the probe builds, and a claimed pass covering exactly
the half-open chunk range [0, 4096) (4294967296 words) without gaps, overlaps, incompatible
identities or failures. Missing or altered files, and success claims the evidence does not
support, are rejected. A recorded "fail"/"incomplete" outcome is accepted only when consistent.
"""
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REL = HERE.relative_to(REPO).as_posix()
sys.path.insert(0, str(HERE))

PIN = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
VERIFIER = "ebbf9d5cac596a718532b34798dc452e4050d6940594005c44f9a729c699c5a8"
MEASUREMENT = "2c8fd1f3a6711f0639685319fb25262b02bfecf4c6589c52cb58928270a46322"
CHUNKS, WORDS_PER_CHUNK = 4096, 1 << 20
EMPTY = sha256(b"").hexdigest()
PRIOR = {"targetcheck-rv32im-tanh-all.json": "90db00182499b1acb3a208cf19a7b807236b59dcc7d9d5a5d367ff27919c17a0",
         "targetcheck-rv32im-tanh-all.stdout": "d3c878c8ce90a623758239dc4456936f1a8d8b73c5cf073be9d8dd6a223dc921",
         "targetcheck-rv32im-tanh-all.stderr": EMPTY}
PRIOR_IMAGE = "4c46aa4fafce593279c77bd8dc73332682101f13fefd7b61f9ced7a6a939b0bd"
SELF = {"verify.py", "result.json"}


class Reject(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise Reject(msg)


def path(relpath):
    p = (REPO / relpath).resolve()
    need(p.is_relative_to(REPO), f"path escapes repository: {relpath}")
    need(p.is_file(), f"missing evidence file: {relpath}")
    return p


def digest(relpath):
    return sha256(path(relpath).read_bytes()).hexdigest()


def load(relpath):
    try:
        return json.loads(path(relpath).read_text())
    except json.JSONDecodeError as exc:
        raise Reject(f"invalid JSON in {relpath}: {exc}") from exc


def check_record(label, expect_args, expect_exit, source):
    """A toolkit/run.py record bound to its stdout/stderr and the exact evaluator argv."""
    base = f"{REL}/rerun/logs/{label}"
    rec = load(f"{base}.json")
    need(rec.get("exit_code") == expect_exit, f"{label}: exit {rec.get('exit_code')} != {expect_exit}")
    need(rec.get("stdout_sha256") == digest(f"{base}.stdout"), f"{label}: stdout digest mismatch")
    need(rec.get("stderr_sha256") == digest(f"{base}.stderr"), f"{label}: stderr digest mismatch")
    need(rec.get("source_sha256") == source, f"{label}: source digest binding mismatch")
    argv = rec.get("argv", [])
    need(len(argv) >= 3 and argv[0].endswith("/runtime/bin/python") and argv[0].startswith("$REPO/test/scratch/")
         and argv[1:3] == ["-m", "eik"], f"{label}: not the toolkit runtime interpreter")
    need(argv[3:] == expect_args, f"{label}: argv {argv[3:]} != {expect_args}")
    return rec


def check_report(rep, lo, hi, image_bytes):
    need(rep.get("schema") == "eik-report-1" and rep.get("kind") == "targetcheck", "not a targetcheck report")
    need(rep.get("competition") == "exact-integer-kernels", "wrong competition")
    need(rep.get("function") == "tanh" and rep.get("target") == "rv32im", "wrong function/target")
    need(rep.get("sha256") == PIN, "report source digest is not the frozen entry")
    need(rep.get("fingerprint") == {"measurement": MEASUREMENT, "sandbox": "none", "verifier": VERIFIER},
         f"incompatible fingerprint {rep.get('fingerprint')}")
    need((rep.get("chunk_lo"), rep.get("chunk_hi")) == (lo, hi), "report range differs from claim")
    need(rep.get("verdict") == "passed" and rep.get("mismatches") == 0 and rep.get("reasons") == []
         and rep.get("stage") is None, "report is not a clean pass")
    # range_complete: every chunk of [lo, hi) was compared; complete: the range is the whole domain.
    need(rep.get("range_complete") is True, "report range not complete")
    need(rep.get("complete") is ((lo, hi) == (0, CHUNKS)), "report complete flag inconsistent with range")
    need(rep.get("words_checked") == (hi - lo) * WORDS_PER_CHUNK, "words_checked does not match range")
    need(rep.get("image_sha256") == sha256(image_bytes).hexdigest(), "image_sha256 not bound to retained image")


def main():
    import elfcheck as E

    result = load(f"{REL}/result.json")
    cov = load(f"{REL}/coverage.json")
    need(result.get("status") in {"pass", "fail", "incomplete"}, "result.status invalid")
    need(cov.get("status") == result["status"], "coverage/result status disagree")
    need(cov.get("function") == "tanh" and cov.get("target") == "rv32im", "coverage scope is not rv32im/tanh")

    # Every artifact listed by result.json, and every file present in the packet, is hashed.
    arts = result.get("artifacts")
    need(isinstance(arts, dict) and arts, "result.artifacts missing")
    for rel, value in arts.items():
        need(digest(rel) == value, f"artifact digest mismatch: {rel}")
    present = {p.relative_to(REPO).as_posix() for p in HERE.rglob("*")
               if p.is_file() and "__pycache__" not in p.parts}
    unlisted = sorted(p for p in present - set(arts) if Path(p).name not in SELF or Path(p).parent != Path(REL))
    need(not unlisted, f"unlisted files in packet: {unlisted}")
    need(f"{REL}/coverage.json" in arts and f"{REL}/elfcheck.py" in arts, "core artifacts not listed")

    # Frozen source.
    need(digest("entry.c") == PIN, "root entry.c is not the frozen source")
    need(cov["source"]["sha256"] == PIN and cov["source"]["pinned_sha256"] == PIN, "coverage source digest")
    need(digest("eik-work/trials/m0-tanh-refine/entry.c") == PIN, "trials copy differs from frozen source")

    # Runtime identity: fingerprint log equals the toolkit manifest and the prior report's identity.
    fp_rec = check_record("fingerprint", ["fingerprint", "--details"], 0, None)
    fp = load(f"{REL}/rerun/logs/fingerprint.stdout")
    manifest = load("eik-work/toolkit/manifest.json")["fingerprint"]
    need(fp.get("verifier") == VERIFIER == manifest.get("verifier"), "verifier identity differs from manifest")
    need(fp.get("measurement") == MEASUREMENT == manifest.get("measurement"), "measurement identity differs")
    need(fp.get("details") == manifest.get("details"), "fingerprint details differ from pinned manifest")
    deps = load("eik-work/toolkit/dependencies.json")["host_tool_versions"]
    tools = fp["details"]["tools"]
    need(tools.get("host_cc") == deps["host_cc"] and tools.get("clang") == deps["clang"]
         and tools.get("packages") == deps["packages"], "tool versions differ from pinned dependencies")
    need(cov["runtime"]["fingerprint"]["verifier"] == VERIFIER
         and cov["runtime"]["fingerprint"]["measurement"] == MEASUREMENT, "coverage runtime identity")
    del fp_rec

    # Retained image and objects.
    image_rel = f"{REL}/rerun/objects/target-check-rv32im.elf"
    image = path(image_rel).read_bytes()
    summary = E.summary(image)
    view = E.executable_view(summary)
    need(summary["machine"] == E.EM_RISCV and summary["e_type"] == 2, "image is not an RV32 executable")
    need(summary["symbols"].get("_start", {}).get("value") == summary["entry"], "entry point is not _start")
    need("eik_tanh" in summary["symbols"], "image lacks eik_tanh")
    need(not summary["dynamic"] and not summary["interp"] and not view["relocation_sections"],
         "image is not a static, fully relocated executable")
    ident = cov["image_identity"]
    need(ident["sha256"] == sha256(image).hexdigest() == ident["reported_image_sha256"], "image identity")
    need(ident["summary"] == json.loads(json.dumps(view)), "recorded image summary differs from retained image")
    obj = path(f"{REL}/rerun/objects/sub-rv32im.o").read_bytes()
    osum = E.summary(obj)
    need(osum["machine"] == E.EM_RISCV and osum["e_type"] == 1, "sub-rv32im.o is not an RV32 relocatable")
    need(ident["object"]["summary"] == json.loads(json.dumps(E.executable_view(osum))), "object summary differs")
    text_obj = [s for s in osum["alloc_sections"] if s["name"] == ".text"]
    text_img = [s for s in summary["alloc_sections"] if s["name"] == ".text"]
    need(text_obj and text_img, "missing .text")
    for name in ("entry.o", "guest.o", "target_check.o"):
        rel = f"{REL}/rerun/objects/zig-cache/{name}"
        need(ident["zig_cache_objects"][name]["sha256"] == digest(rel), f"zig object {name} digest")
        need(E.summary(path(rel).read_bytes())["machine"] == E.EM_RISCV, f"{name} not RV32")

    # Probe builds in other case directories: executable equivalence, path-only metadata differences.
    allowed_meta = {".debug_info", ".debug_line", ".debug_str", ".debug_abbrev", ".debug_rnglists",
                    ".debug_loclists", ".debug_frame", ".rela.debug_line", ".rela.debug_info", ".symtab",
                    ".strtab", ".comment"}
    for case, label, src_rel in (("repro-root", "probe-root", "$REPO/entry.c"),
                                 ("repro-trials", "probe-trials", "$REPO/eik-work/trials/m0-tanh-refine/entry.c")):
        check_record(label, ["targetcheck", src_rel, "--function", "tanh", "--target", "rv32im",
                             "--chunks", "0:1", "--jobs", "1"], 0, PIN)
        img = gzip.decompress(path(f"{REL}/rerun/probes/{case}/target-check-rv32im.elf.gz").read_bytes())
        pobj = gzip.decompress(path(f"{REL}/rerun/probes/{case}/sub-rv32im.o.gz").read_bytes())
        check_report(load(f"{REL}/rerun/logs/{label}.stdout"), 0, 1, img)
        si, so = E.summary(img), E.summary(pobj)
        need(E.executable_view(si) == view, f"{case}: image not executably equivalent")
        need(E.executable_view(so) == E.executable_view(osum), f"{case}: object not equivalent")
        meta = set(E.metadata_differences(summary, si)) | set(E.metadata_differences(osum, so))
        need(all(m in allowed_meta or m.startswith("ELF header") for m in meta), f"{case}: unexpected diff {meta}")
        rec = ident["reproduction_probes"][case]
        need(rec["image_sha256"] == sha256(img).hexdigest() and rec["counts_toward_coverage"] is False,
             f"{case}: probe record")

    # Prior evidence audit: raw hashes against the packet index; not reused.
    prior = cov["prior"]
    packet = load("eik-work/trials/m0-tanh-refine/packet.json")["runs"]["targetcheck-rv32im-tanh-all"]
    need(packet["files"] == PRIOR and packet["exit_code"] == 0, "prior packet index changed")
    for name, value in PRIOR.items():
        need(digest(f"eik-work/trials/m0-tanh-refine/{name}") == value, f"prior raw file tampered: {name}")
    prior_rep = load("eik-work/trials/m0-tanh-refine/targetcheck-rv32im-tanh-all.stdout")
    need(prior_rep["image_sha256"] == PRIOR_IMAGE and prior_rep["fingerprint"]["verifier"] == VERIFIER,
         "prior report identity changed")
    need(prior["status"] == "audited-not-reused", "prior coverage may not be claimed without a bound image")

    # Claimed coverage.
    ranges = cov.get("ranges", [])
    selected = [r for r in ranges if r.get("provenance") == "rerun"]
    need(cov.get("selected_set") == "rerun" and len(selected) == len(ranges), "mixed or unknown coverage sets")
    covered, words, mism = [], 0, 0
    for r in sorted(ranges, key=lambda r: r["chunk_lo"]):
        lo, hi = r["chunk_lo"], r["chunk_hi"]
        need(isinstance(lo, int) and isinstance(hi, int) and 0 <= lo < hi <= CHUNKS, "bad range")
        need(not covered or covered[-1][1] <= lo, f"overlapping range at {lo}")
        need(r["report_sha256"] == digest(r["report"]) and r["record_sha256"] == digest(r["record"]),
             "range report/record digest")
        need(r["image_sha256"] == digest(r["image"]), "range image digest")
        rep = load(r["report"])
        check_report(rep, lo, hi, path(r["image"]).read_bytes())
        need(r["record"] == f"{REL}/rerun/logs/targetcheck-rv32im-tanh-all.json", "unexpected record")
        check_record("targetcheck-rv32im-tanh-all", ["targetcheck", "$REPO/entry.c", "--function", "tanh",
                                                     "--target", "rv32im", "--chunks", f"{lo}:{hi}",
                                                     "--jobs", "2"], 0, PIN)
        need(r["words"] == rep["words_checked"] and r["mismatches"] == rep["mismatches"], "range facts")
        covered.append((lo, hi))
        words += rep["words_checked"]
        mism += rep["mismatches"]
    gaps, cursor = [], 0
    for lo, hi in covered:
        if lo > cursor:
            gaps.append([cursor, lo])
        cursor = hi
    if cursor < CHUNKS:
        gaps.append([cursor, CHUNKS])
    tot = cov["totals"]
    if result["status"] == "pass":
        need(not gaps and words == 1 << 32 and mism == 0, f"pass claimed with gaps {gaps} or mismatches {mism}")
        need(tot == {"chunks": CHUNKS, "words": 1 << 32, "mismatches": 0, "gaps": [], "overlaps": []}, "totals")
        need(cov.get("gaps") == [] and result.get("gaps") == [], "pass claimed with recorded gaps")
        need(all(f["step"] != "targetcheck" for f in cov.get("failures", [])), "pass claimed with failed check")
    else:
        need(gaps or mism or result.get("gaps"), "negative status without an evidenced gap or failure")
    need(result.get("source", {}).get("sha256") == PIN, "result source identity")
    need(result.get("runtime", {}).get("verifier") == VERIFIER, "result runtime identity")
    print(f"rv32im/tanh coverage verified: status={result['status']} chunks=[0,{CHUNKS}) words={words} "
          f"mismatches={mism} image={ident['sha256']}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Reject, KeyError, TypeError, ValueError, OSError, gzip.BadGzipFile) as exc:
        print(f"REJECTED: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
