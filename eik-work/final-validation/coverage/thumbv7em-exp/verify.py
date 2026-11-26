#!/usr/bin/env python3
"""Offline verifier for the thumbv7em/exp exhaustive targetcheck coverage packet.

Run from the repository root:  python3 eik-work/final-validation/coverage/thumbv7em-exp/verify.py
Standard library only. Exits 0 only when every listed artifact is present and untampered, the
report is bound to the frozen source, pinned toolkit/reference and fingerprint, the linked image,
and (for status "pass") the claimed ranges cover [0,4096) exactly once with zero failures.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PRIOR = ROOT / "eik-work/trials/m0-tanh-refine"
SRC = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
MEASUREMENT = "2c8fd1f3a6711f0639685319fb25262b02bfecf4c6589c52cb58928270a46322"
VERIFIER = "ebbf9d5cac596a718532b34798dc452e4050d6940594005c44f9a729c699c5a8"
EXP_DIGEST = "9d44e4100c4f0340f9b825393cc64bd64eae6ccdde8ece146df9464bd4a5c0c2"
CHUNK_WORDS = 1 << 20
CHUNKS = 4096
WORDS = 1 << 32
STATUSES = {"pass", "fail", "incomplete"}
errors = []


def fail(msg):
    errors.append(msg)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        fail(f"cannot read JSON {path}: {exc}")
        return None


def check_art(entry, base, label):
    """entry = {path, sha256, bytes}; path relative to base."""
    try:
        p = (base / entry["path"]).resolve()
        if not p.is_file():
            fail(f"{label}: missing {entry['path']}")
            return False
        data = p.read_bytes()
        if hashlib.sha256(data).hexdigest() != entry["sha256"] or len(data) != entry["bytes"]:
            fail(f"{label}: hash/size mismatch for {entry['path']}")
            return False
        return True
    except (KeyError, TypeError) as exc:
        fail(f"{label}: malformed artifact entry ({exc})")
        return False


def check_report(rep, label, lo=None, hi=None):
    if not isinstance(rep, dict):
        fail(f"{label}: report missing")
        return
    want = {"kind": "targetcheck", "schema": "eik-report-1", "function": "exp", "target": "thumbv7em",
            "sha256": SRC, "verdict": "passed", "mismatches": 0, "reasons": [], "range_complete": True}
    for k, v in want.items():
        if rep.get(k) != v:
            fail(f"{label}: {k}={rep.get(k)!r}, expected {v!r}")
    fp = rep.get("fingerprint") or {}
    if fp.get("measurement") != MEASUREMENT or fp.get("verifier") != VERIFIER or fp.get("sandbox") != "none":
        fail(f"{label}: fingerprint differs from the pinned measurement/verifier")
    clo, chi = rep.get("chunk_lo"), rep.get("chunk_hi")
    if not (type(clo) is int and type(chi) is int and 0 <= clo < chi <= CHUNKS):
        fail(f"{label}: bad chunk bounds {clo},{chi}")
        return
    if lo is not None and (clo, chi) != (lo, hi):
        fail(f"{label}: chunk bounds {clo},{chi} differ from claimed {lo},{hi}")
    if rep.get("words_checked") != (chi - clo) * CHUNK_WORDS:
        fail(f"{label}: words_checked {rep.get('words_checked')} != {(chi - clo) * CHUNK_WORDS}")
    if (clo, chi) == (0, CHUNKS) and rep.get("complete") is not True:
        fail(f"{label}: whole-domain report not complete")


def check_record(rec, stdout, stderr, label, argv_tail):
    if not isinstance(rec, dict):
        fail(f"{label}: runner record missing")
        return
    if rec.get("exit_code") != 0:
        fail(f"{label}: exit_code {rec.get('exit_code')}")
    if rec.get("source_sha256") != SRC:
        fail(f"{label}: source_sha256 not frozen source")
    if rec.get("stdout_sha256") != sha(stdout) or rec.get("stderr_sha256") != sha(stderr):
        fail(f"{label}: stdout/stderr hash not bound to record")
    argv = rec.get("argv") or []
    if argv[1:4] != ["-m", "eik", "targetcheck"] or argv[4:] != argv_tail:
        fail(f"{label}: argv {argv[1:]} does not match expected command")


def elf_ok(path, label):
    b = Path(path).read_bytes()[:20]
    if len(b) < 20 or b[:4] != b"\x7fELF" or b[4] != 1 or b[5] != 1 or int.from_bytes(b[18:20], "little") != 40:
        fail(f"{label}: not a 32-bit little-endian ARM ELF")


def main():
    cov = load(HERE / "coverage.json")
    res = load(HERE / "result.json")
    if cov is None or res is None:
        return finish(None)

    # Frozen source.
    if sha(ROOT / "entry.c") != SRC:
        fail("root entry.c is not the frozen source")
    if cov.get("source", {}).get("sha256") != SRC:
        fail("coverage.json source identity wrong")
    status = cov.get("status")
    if status not in STATUSES or res.get("status") != status:
        fail(f"status invalid or inconsistent: coverage={status!r} result={res.get('status')!r}")
    if cov.get("function") != "exp" or cov.get("target") != "thumbv7em":
        fail("coverage.json scope is not exp/thumbv7em")
    if res.get("coverage", {}).get("sha256") != sha(HERE / "coverage.json"):
        fail("result.json does not bind coverage.json hash")

    # Every listed artifact (in this packet) intact; and no unlisted packet files.
    arts = cov.get("artifacts") or {}
    for name, entry in arts.items():
        if entry.get("path") != f"eik-work/final-validation/coverage/thumbv7em-exp/{name}":
            fail(f"artifact path mismatch for {name}")
        check_art(entry, ROOT, "artifact")
    present = {p.relative_to(HERE).as_posix() for p in HERE.rglob("*") if p.is_file()
               and "__pycache__" not in p.parts}
    extra = present - set(arts) - {"coverage.json", "result.json", "verify.py", "README.md"}
    if extra:
        fail(f"unlisted files in packet: {sorted(extra)}")

    # Pinned toolkit / reference identities.
    tk = cov.get("toolkit") or {}
    for name, entry in tk.items():
        check_art(entry, ROOT, "toolkit")
    if tk.get("kit/reference/exp.digest", {}).get("sha256") != EXP_DIGEST:
        fail("exp reference digest identity wrong")
    dig = (ROOT / "eik-work/toolkit/kit/reference/digests.sha256").read_text()
    if f"{EXP_DIGEST}  reference/exp.digest" not in dig:
        fail("pinned digests.sha256 does not pin exp.digest")
    om = load(ROOT / "eik-work/offline-runtime/manifest.json") or {}
    for name, h in (om.get("toolkit_sha256") or {}).items():
        if sha(ROOT / "eik-work/toolkit" / name) != h:
            fail(f"toolkit file {name} differs from offline-runtime pin")
    if not om.get("toolkit_sha256"):
        fail("offline-runtime toolkit pins missing")

    # Fingerprint report identity.
    fp = load(HERE / "reports/rerun/fingerprint.stdout")
    if not fp or fp.get("measurement") != MEASUREMENT or fp.get("verifier") != VERIFIER:
        fail("rerun fingerprint report does not carry the pinned identity")
    fprec = load(HERE / "reports/rerun/fingerprint.json") or {}
    if fprec.get("exit_code") != 0 or fprec.get("stdout_sha256") != sha(HERE / "reports/rerun/fingerprint.stdout"):
        fail("fingerprint record not bound")
    if cov.get("runtime", {}).get("fingerprint_details_identical_to_prior"):
        if fp != load(PRIOR / "fingerprint.stdout"):
            fail("claimed fingerprint identity with prior is false")

    # Ranges: disjoint, gap-free, exact counts, each bound to its report, record and image.
    ranges = cov.get("ranges") or []
    total, failures, spans = 0, 0, []
    for i, r in enumerate(ranges):
        lab = f"range[{i}]"
        lo, hi = r.get("chunk_lo"), r.get("chunk_hi")
        if not (type(lo) is int and type(hi) is int and 0 <= lo < hi <= CHUNKS):
            fail(f"{lab}: bad bounds")
            continue
        spans.append((lo, hi))
        if r.get("words") != (hi - lo) * CHUNK_WORDS:
            fail(f"{lab}: word count mismatch")
        try:
            rp = HERE / r["report"]
            rc = HERE / r["record"]
            rep = load(rp)
            check_report(rep, lab, lo, hi)
            check_record(load(rc), rp, rp.with_suffix(".stderr"), lab,
                         ["$REPO/entry.c", "--function", "exp", "--target", "thumbv7em",
                          "--chunks", f"{lo}:{hi}", "--jobs", "2"])
            if not rep:
                continue
            for k in ("mismatches", "verdict", "complete", "range_complete", "image_sha256"):
                if r.get(k) != rep.get(k):
                    fail(f"{lab}: {k} disagrees with its report")
            img = HERE / r["image"]
            if not img.is_file() or sha(img) != rep.get("image_sha256"):
                fail(f"{lab}: image_sha256 not bound to retained linked image")
            else:
                elf_ok(img, lab)
            if not (HERE / r["object"]).is_file():
                fail(f"{lab}: retained object missing")
            if r.get("provenance") != "rerun":
                fail(f"{lab}: only rerun ranges are bindable in this packet")
            total += rep.get("words_checked") or 0
            failures += rep.get("mismatches") or 0
        except (KeyError, TypeError) as exc:
            fail(f"{lab}: malformed ({exc})")
    spans.sort()
    gaps, overlaps, cur = [], [], 0
    for lo, hi in spans:
        if lo > cur:
            gaps.append([cur, lo])
        if lo < cur:
            overlaps.append([lo, min(cur, hi)])
        cur = max(cur, hi)
    if cur < CHUNKS:
        gaps.append([cur, CHUNKS])
    if cov.get("gaps") != gaps or cov.get("overlaps") != overlaps:
        fail(f"declared gaps/overlaps {cov.get('gaps')}/{cov.get('overlaps')} != computed {gaps}/{overlaps}")
    if cov.get("covered_words") != total or cov.get("failures") != failures:
        fail("declared covered_words/failures disagree with reports")

    # Prior evidence: audited, kept separate, never silently credited.
    pr = cov.get("prior") or {}
    if pr.get("reused") is not False:
        fail("prior coverage may not be credited: its image is not retained")
    for k in ("report", "record", "stderr", "packet", "fingerprint"):
        if k in pr:
            check_art(pr[k], ROOT, f"prior {k}")
        else:
            fail(f"prior {k} missing")
    packet = load(PRIOR / "packet.json") or {}
    run = (packet.get("runs") or {}).get("targetcheck-thumbv7em-exp-all") or {}
    for n, h in (run.get("files") or {}).items():
        if sha(PRIOR / n) != h:
            fail(f"prior raw file {n} differs from packet index")
    if not run.get("files") or run.get("exit_code") != 0:
        fail("prior packet entry missing or nonzero exit")
    if "--function exp --target thumbv7em" not in run.get("command", ""):
        fail("prior command not bound to exp/thumbv7em")
    prep = load(PRIOR / "targetcheck-thumbv7em-exp-all.stdout")
    check_report(prep, "prior", 0, CHUNKS)

    # Status claims.
    if status == "pass":
        if gaps or overlaps or failures or total != WORDS or not ranges:
            fail("status pass claimed without gap-free, overlap-free, zero-failure 2^32 coverage")
        m = res.get("measured") or {}
        if m.get("words_checked") != WORDS or m.get("mismatches") != 0 or res.get("gaps"):
            fail("result.json measured facts do not support pass")
    return finish(status)


def finish(status):
    if errors:
        for e in errors:
            print("verify: FAIL:", e)
        return 1
    print(f"verify: OK: thumbv7em/exp coverage packet status={status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
