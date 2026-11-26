#!/usr/bin/env python3
"""Offline verifier for the thumbv7em/tanh exhaustive target-coverage packet.

Standard library only. Run from anywhere:
    python3 eik-work/final-validation/coverage/thumbv7em-tanh/verify.py
Exits 0 only if every artifact is present and untampered, the claimed status is
supported by the evidence, and a claimed pass covers [0, 4096) chunks exactly once
with zero mismatches under the pinned fingerprint and frozen source.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCE = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
EMPTY = hashlib.sha256(b"").hexdigest()
DOMAIN = 1 << 32
CHUNKS = 4096
PRIOR_INDEX = {
    "targetcheck-thumbv7em-all.json": "207f70777a28ae806c35adf15b8d1de37f7e3a6be9ab4c0e42b6b4f2d4594408",
    "targetcheck-thumbv7em-all.stderr": EMPTY,
    "targetcheck-thumbv7em-all.stdout": "7c3baa949ce7aacecd328a5cd32958032bd7d79665edc4880d3d6a58e1b90c27",
}
PINNED_PAYLOADS = {
    "qemu/source/qemu_7.2+dfsg.orig.tar.xz": "91aca71520040edc40b8d437aa3004dae614f58e286cf653ee8996c07af2962f",
    "wheels/unicorn-2.1.4-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl":
        "9d6e6dea140560de4ebd8446661f7ef84a357d428c14a3ef09dacd306ec8c239",
    "wheels/ziglang-0.17.1-py3-none-manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64.whl":
        "ea6cc5d87b033cf0aedfbc8f9549a908cae6c50ac31f1698188fa48a74524b54",
}
errors = []


def need(cond, msg):
    if not cond:
        errors.append(msg)
    return bool(cond)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(rel):
    p = (HERE / rel).resolve()
    if not p.is_relative_to(HERE) or not p.is_file() or p.is_symlink():
        raise ValueError(f"missing or unsafe artifact: {rel}")
    return p


def load(rel):
    return json.loads(safe(rel).read_bytes())


def find_fingerprint(node):
    if isinstance(node, dict):
        if node.get("kind") == "fingerprint" and "measurement" in node and "verifier" in node:
            return node["measurement"], node["verifier"]
        for v in node.values():
            r = find_fingerprint(v)
            if r:
                return r
    elif isinstance(node, list):
        for v in node:
            r = find_fingerprint(v)
            if r:
                return r
    return None


def check_report(rep, lo, hi, image=None):
    """Return True if a targetcheck report supports a clean pass over chunks [lo, hi)."""
    ok = True
    ok &= need(rep.get("schema") == "eik-report-1" and rep.get("kind") == "targetcheck", "report kind/schema")
    ok &= need(rep.get("competition") == "exact-integer-kernels", "report competition")
    ok &= need(rep.get("function") == "tanh" and rep.get("target") == "thumbv7em", "report function/target")
    ok &= need(rep.get("sha256") == SOURCE, "report source hash is not the frozen entry.c")
    ok &= need((rep.get("chunk_lo"), rep.get("chunk_hi")) == (lo, hi), "report chunk range")
    ok &= need(rep.get("complete") is True and rep.get("range_complete") is True, "report not complete")
    ok &= need(rep.get("verdict") == "passed" and rep.get("reasons") == [], "report verdict")
    ok &= need(rep.get("mismatches") == 0, "report has mismatches")
    ok &= need(rep.get("words_checked") == (hi - lo) << 20, "report word count")
    if image is not None:
        ok &= need(rep.get("image_sha256") == image, "report image_sha256 is not the retained linked image")
    return ok


def elf_arm32(path):
    b = path.read_bytes()[:20]
    return b[:4] == b"\x7fELF" and b[4] == 1 and b[5] == 1 and int.from_bytes(b[18:20], "little") == 40


def main():
    cov = load("coverage.json")
    res = load("result.json")
    status = res.get("status")
    need(status in ("pass", "fail", "incomplete"), "result status must be pass/fail/incomplete")
    need(res.get("coverage", {}).get("sha256") == sha(safe("coverage.json")), "coverage.json hash differs from result.json")
    need(res.get("function") == cov.get("function") == "tanh", "function")
    need(res.get("target") == cov.get("target") == "thumbv7em", "target")

    # Every evidence file listed, present and untampered; nothing unlisted under new/ or prior/.
    arts = cov.get("artifacts", {})
    need(arts == res.get("artifacts"), "artifact lists differ between coverage.json and result.json")
    on_disk = {p.relative_to(HERE).as_posix() for d in ("new", "prior") if (HERE / d).is_dir()
               for p in (HERE / d).rglob("*") if p.is_file() or p.is_symlink()}
    need(on_disk == set(arts), f"artifact inventory differs: {sorted(on_disk ^ set(arts))}")
    for rel, digest in arts.items():
        try:
            need(sha(safe(rel)) == digest, f"tampered artifact: {rel}")
        except ValueError as exc:
            errors.append(str(exc))

    # Frozen source identity.
    need(cov.get("source", {}).get("sha256") == SOURCE, "coverage source identity")
    root = REPO / "entry.c"
    need(root.is_file() and sha(root) == SOURCE, "root entry.c is not at the frozen SHA-256")

    # Pinned toolkit identity (when present in the checkout) and fingerprint.
    ids = cov.get("identities", {})
    need(ids == res.get("identities"), "identities differ between coverage.json and result.json")
    for name, digest in ids.get("toolkit", {}).items():
        p = REPO / "eik-work/toolkit" / name
        if p.is_file():
            need(sha(p) == digest, f"toolkit identity differs: {name}")
    om_path = REPO / "eik-work/offline-runtime/manifest.json"
    for name, digest in ids.get("offline_runtime", {}).items():
        p = REPO / "eik-work/offline-runtime" / name
        if p.is_file():
            need(sha(p) == digest, f"offline-runtime identity differs: {name}")
    fp = load("new/logs/fingerprint.stdout")
    pin = None
    tm = REPO / "eik-work/toolkit/manifest.json"
    if tm.is_file():
        pin = find_fingerprint(json.loads(tm.read_bytes()))
        need(pin is not None, "toolkit manifest has no fingerprint pin")
    pin = pin or (ids.get("fingerprint", {}).get("measurement"), ids.get("fingerprint", {}).get("verifier"))
    need((fp.get("measurement"), fp.get("verifier")) == pin, "fresh fingerprint differs from the pin")
    need((ids.get("fingerprint", {}).get("measurement"), ids.get("fingerprint", {}).get("verifier")) == pin,
         "recorded fingerprint identity differs from the pin")

    # Restored payloads must equal the offline-runtime pins.
    restored = cov.get("runtime", {}).get("restored_payloads", [])
    need({r.get("path"): r.get("sha256") for r in restored} == PINNED_PAYLOADS, "restored payload set/hashes")
    if om_path.is_file():
        om = json.loads(om_path.read_bytes())
        for r in restored:
            need(om["files"].get(r["path"], {}).get("sha256") == r["sha256"], f"payload pin differs: {r['path']}")
    install = safe("new/logs/install.log").read_text()
    for name, digest in PINNED_PAYLOADS.items():
        if name.startswith("wheels/"):
            need(f"sha256={digest}" in install, f"install.log lacks pinned wheel {name}")
    need("import probe -> 0" in install, "install.log lacks a passing import probe")

    # Commands and exits recorded in result.json must agree with the run records.
    cmds = {c.get("step"): c for c in res.get("commands", [])}
    need(set(cmds) >= {"prepare", "bootstrap", "setup", "fingerprint", "targetcheck"}, "missing command records")
    for step in ("setup", "fingerprint", "targetcheck"):
        c = cmds.get(step, {})
        r = load(c.get("record", "missing"))
        base = c["record"].removesuffix(".json")
        need(r.get("exit_code") == c.get("exit_code"), f"{step}: exit differs from record")
        need(r.get("stdout_sha256") == sha(safe(base + ".stdout")), f"{step}: stdout hash binding")
        need(r.get("stderr_sha256") == sha(safe(base + ".stderr")), f"{step}: stderr hash binding")
    need(safe("new/logs/prepare.stdout").read_text().startswith("Prepared "), "prepare log")
    need(safe("new/logs/bootstrap.stdout").read_text().startswith("bootstrap passed"), "bootstrap log")

    # Selected set: rerun reports, bound to sources, commands and retained images.
    claimed_ok = True
    spans = []
    for sel in cov.get("selected", []):
        lo, hi = sel["chunks"]
        spans.append((lo, hi))
        rep = load(sel["report"])
        img = safe(sel["image"])
        claimed_ok &= need(elf_arm32(img), "selected image is not a 32-bit ARM ELF")
        claimed_ok &= need(sha(img) == sel["image_sha256"], "selected image hash")
        claimed_ok &= need(elf_arm32(safe(sel["object"])) and sha(safe(sel["object"])) == sel["object_sha256"],
                           "selected object")
        claimed_ok &= check_report(rep, lo, hi, sha(img))
        claimed_ok &= need(sel["words"] == (hi - lo) << 20 and sel["mismatches"] == rep["mismatches"], "selected counts")
        claimed_ok &= need(sel.get("provenance") == "rerun", "only rerun coverage is bound in this packet")
        rec = load(sel["record"])
        argv = rec.get("argv", [])
        claimed_ok &= need(rec.get("exit_code") == 0, "targetcheck exit code")
        claimed_ok &= need(rec.get("source_sha256") == SOURCE, "record source hash")
        claimed_ok &= need(argv[1:4] == ["-m", "eik", "targetcheck"] and argv[4] == "$REPO/entry.c",
                           "record argv is not a targetcheck of root entry.c")
        tail = argv[5:]
        claimed_ok &= need(tail[:8] == ["--function", "tanh", "--target", "thumbv7em", "--chunks", f"{lo}:{hi}",
                                        "--jobs", "2"] and tail[8] == "--out"
                           and tail[9].endswith("/" + Path(sel["report"]).name), "record argv arguments")
    spans.sort()
    pos, gaps, overlaps = 0, [], []
    for lo, hi in spans:
        need(0 <= lo < hi <= CHUNKS, f"bad span {lo}:{hi}")
        if lo > pos:
            gaps.append([pos, lo])
        if lo < pos:
            overlaps.append([lo, min(pos, hi)])
        pos = max(pos, hi)
    if pos < CHUNKS:
        gaps.append([pos, CHUNKS])
    words = sum((hi - lo) << 20 for lo, hi in spans)

    # Prior evidence audit (history only, never credited here).
    prior = cov.get("prior", {})
    for name, digest in PRIOR_INDEX.items():
        need(sha(safe("prior/" + name)) == digest, f"prior file differs from packet index: {name}")
    idx = load("prior/packet.json")
    need(idx.get("logs", idx).get("targetcheck-thumbv7em-all", {}).get("files") == PRIOR_INDEX
         or json.dumps(PRIOR_INDEX, sort_keys=True)[1:-1] in json.dumps(idx, sort_keys=True),
         "prior packet does not index the prior report")
    prec = load("prior/targetcheck-thumbv7em-all.json")
    need(prec.get("stdout_sha256") == PRIOR_INDEX["targetcheck-thumbv7em-all.stdout"], "prior record stdout binding")
    need(prec.get("exit_code") == 0 and prec.get("source_sha256") == SOURCE, "prior record exit/source")
    prep = load("prior/targetcheck-thumbv7em-all.stdout")
    check_report(prep, 0, CHUNKS)
    need(prior.get("credited") is False, "prior coverage must not be credited without a bound image")

    # Status must be supported.
    supported = (claimed_ok and not gaps and not overlaps and words == DOMAIN
                 and cov.get("words_covered") == DOMAIN and cov.get("mismatches") == 0
                 and cov.get("gaps") == gaps and cov.get("overlaps") == overlaps and cov.get("failures") == []
                 and res.get("gaps") == [] and res.get("failures") == [])
    m = res.get("measured", {})
    if status == "pass":
        need(supported, f"pass claimed without support (gaps={gaps}, overlaps={overlaps}, words={words})")
        need(m.get("words_checked") == DOMAIN and m.get("mismatches") == 0 and m.get("verdict") == "passed",
             "measured facts do not support pass")
    else:
        need(res.get("gaps") or res.get("failures"), "non-pass status must state its gaps or failures")

    if errors:
        for e in errors:
            print("FAIL:", e, file=sys.stderr)
        return 1
    print(f"verified thumbv7em/tanh coverage: status={status}, {len(spans)} range(s), {words} words, "
          f"0 gaps, 0 overlaps, {len(arts)} hashed artifacts")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError, TypeError, IndexError, AttributeError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
