#!/usr/bin/env python3
"""Offline verifier for the host/tanh exhaustive coverage packet (standard library only).

Run from the repository root: python3 eik-work/final-validation/coverage/host-tanh/verify.py
Exits 0 only when every hashed artifact is present and untampered, the identities bind the
frozen root entry.c to the pinned toolkit/kit, and the claimed status is supported by the raw
reports: a "pass" needs one selected set of gap-free, non-overlapping, non-quick GCC ASan+UBSan
fullcheck reports over [0,4096) with zero mismatches and zero sanitizer errors.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REL = "eik-work/final-validation/coverage/host-tanh"
ENTRY_SHA = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
HOST_CC = "gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0"
CHUNK_WORDS = 1 << 20
DOMAIN = (0, 4096)
STATUSES = ("pass", "fail", "incomplete")
errors = []


def fail(msg):
    errors.append(msg)


def require(cond, msg):
    if not cond:
        fail(msg)
    return bool(cond)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(rel):
    if not isinstance(rel, str) or rel.startswith("/") or ".." in Path(rel).parts:
        raise ValueError(f"bad artifact path {rel!r}")
    return REPO / rel


def load(rel):
    return json.loads(resolve(rel).read_text())


def check_refs(node, where):
    """Every {"path","sha256"} object must name an existing file with that digest."""
    if isinstance(node, dict):
        if set(node) >= {"path", "sha256"} and isinstance(node.get("path"), str):
            try:
                p = resolve(node["path"])
            except ValueError as exc:
                fail(f"{where}: {exc}")
                return
            if require(p.is_file(), f"{where}: missing artifact {node['path']}"):
                require(sha(p) == node["sha256"], f"{where}: hash mismatch for {node['path']}")
        for k, v in node.items():
            check_refs(v, f"{where}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            check_refs(v, f"{where}[{i}]")


def clean_stderr(rel, where):
    text = resolve(rel).read_text(errors="replace")
    require("runtime error" not in text and "AddressSanitizer" not in text and "LeakSanitizer" not in text,
            f"{where}: sanitizer output in stderr")


def check_run(run, where, *, expect_exit=0):
    rec = load(run["record"]["path"])
    require(rec.get("exit_code") == expect_exit == run.get("exit_code"), f"{where}: exit code is not {expect_exit}")
    require(rec.get("argv") == run.get("argv"), f"{where}: argv differs from record")
    require(rec.get("stdout_sha256") == run["stdout"]["sha256"], f"{where}: record does not bind stdout")
    require(rec.get("stderr_sha256") == run["stderr"]["sha256"], f"{where}: record does not bind stderr")
    return rec


def check_range(r, ident, where, selected):
    lo, hi = r["chunk_lo"], r["chunk_hi"]
    require(isinstance(lo, int) and isinstance(hi, int) and 0 <= lo < hi <= 4096, f"{where}: bad range")
    require(r["words"] == (hi - lo) * CHUNK_WORDS, f"{where}: word count does not match range")
    run = r["run"]
    rec = check_run(run, where)
    argv = rec.get("argv", [])
    require(argv[1:4] == ["-m", "eik", "fullcheck"], f"{where}: not an eik fullcheck command")
    require("--function" in argv and argv[argv.index("--function") + 1] == "tanh",
            f"{where}: function is not tanh")
    require("--quick" not in argv, f"{where}: --quick run cannot support exhaustive coverage")
    if "--chunks" in argv:
        require(argv[argv.index("--chunks") + 1] == f"{lo}:{hi}", f"{where}: --chunks differs from claimed range")
    else:
        require((lo, hi) == DOMAIN, f"{where}: no --chunks but range is not whole domain")
    require(any(a.endswith("/entry.c") or a == "entry.c" for a in argv), f"{where}: argv names no entry.c")
    require(rec.get("source_sha256") == ENTRY_SHA, f"{where}: source is not the frozen root entry.c")
    clean_stderr(run["stderr"]["path"], where)
    rep = load(r["report"]["path"])
    if "--out" in argv and resolve(run["stdout"]["path"]).read_bytes() == b"":
        # --out shards: the record binds empty stdout, not the report file, so such a set is
        # corroborating only and can never be the selected set.
        require(not selected, f"{where}: selected range report is not bound by its run record")
        require(Path(argv[argv.index("--out") + 1]).name.startswith(f"host-tanh-{lo}-{hi}"), f"{where}: --out name mismatch")
    else:
        require(rep == load(run["stdout"]["path"]), f"{where}: report differs from the recorded stdout report")
    expect = {"schema": "eik-report-1", "kind": "fullcheck", "function": "tanh", "competition": "exact-integer-kernels",
              "sha256": ENTRY_SHA, "verdict": "passed", "exit": 0, "quick": False, "range_complete": True,
              "mismatches": 0, "examples": [], "reasons": [], "stage": None, "chunk_lo": lo, "chunk_hi": hi,
              "words_checked": (hi - lo) * CHUNK_WORDS, "complete": (lo, hi) == DOMAIN}
    for k, v in expect.items():
        require(rep.get(k) == v, f"{where}: report {k}={rep.get(k)!r}, need {v!r}")
    require("sanitizer" not in rep, f"{where}: report carries sanitizer output")
    fpr = rep.get("fingerprint", {})
    require(fpr.get("verifier") == ident["verifier_fingerprint"] and fpr.get("measurement") == ident["measurement_fingerprint"],
            f"{where}: report fingerprint differs from the pinned identity")
    for k, v in r["measured"].items():
        require(rep.get(k) == v, f"{where}: summary {k} does not match the raw report")
    return lo, hi


def check_set(name, s, ident):
    spans = sorted(check_range(r, ident, f"sets.{name}.ranges[{i}]", bool(s.get("selected"))) for i, r in enumerate(s["ranges"]))
    gaps, overlaps, pos = [], [], DOMAIN[0]
    for lo, hi in spans:
        if lo > pos:
            gaps.append((pos, lo))
        elif lo < pos:
            overlaps.append((lo, min(pos, hi)))
        pos = max(pos, hi)
    if pos < DOMAIN[1]:
        gaps.append((pos, DOMAIN[1]))
    require(not overlaps, f"sets.{name}: overlapping ranges {overlaps}")
    return gaps, sum((hi - lo) * CHUNK_WORDS for lo, hi in spans)


def main():
    cov_rel, res_rel = f"{REL}/coverage.json", f"{REL}/result.json"
    try:
        cov, res = load(cov_rel), load(res_rel)
    except (OSError, ValueError) as exc:
        print(f"FAIL: cannot read packet: {exc}")
        return 1
    check_refs(cov, "coverage")
    check_refs({k: v for k, v in res.items() if k != "verifier_script"}, "result")
    require(res["coverage"]["path"] == cov_rel, "result.json does not bind coverage.json")
    status = cov.get("status")
    require(status in STATUSES and res.get("status") == status, "status missing, unknown or inconsistent")
    require(cov.get("function") == "tanh" and res.get("function") == "tanh", "function is not tanh")

    # Frozen source and pinned toolkit/kit identities.
    require(sha(REPO / "entry.c") == ENTRY_SHA, "root entry.c is not the frozen source")
    require(cov["source"] == {"path": "entry.c", "sha256": ENTRY_SHA} == res["source"], "source identity mismatch")
    ident = cov["identities"]
    files = json.loads((REPO / "eik-work/toolkit/files.json").read_text())
    for name, digest in ident["toolkit_pins"].items():
        require(files.get(name) == digest, f"toolkit pin for {name} differs from files.json")
        require(sha(REPO / "eik-work/toolkit" / name) == digest, f"toolkit file {name} was changed")
    require(set(ident["toolkit_pins"]) >= {"run.py", "kit/eik/config.py", "kit/eik/stages.py"}, "toolkit pins incomplete")
    config = (REPO / "eik-work/toolkit/kit/eik/config.py").read_text()
    require('HOST_SANITIZE = ["-fsanitize=undefined,address", "-fno-sanitize-recover=all"]' in config,
            "pinned kit does not build the full check with ASan and UBSan")
    manifest = (REPO / "eik-work/toolkit/manifest.json").read_text()
    for key in ("verifier_fingerprint", "measurement_fingerprint"):
        require(f'"{ident[key]}"' in manifest, f"{key} is not pinned in the toolkit manifest")
    require(ident["host_cc"] == HOST_CC and f'"host_cc": "{HOST_CC}"' in manifest, "host compiler is not the pinned GCC")
    fp = load(ident["fingerprint_log"]["path"])
    require(fp.get("verifier") == ident["verifier_fingerprint"] and fp.get("measurement") == ident["measurement_fingerprint"],
            "fingerprint log differs from claimed identity")
    require(HOST_CC in json.dumps(fp), "fingerprint log does not record the pinned GCC")
    install = resolve(ident["runtime_install_log"]["path"]).read_text()
    for pkg in ("capstone==5.0.9", "pyelftools==0.33", "unicorn==2.1.4", "ziglang==0.17.1"):
        require(f"installed {pkg}" in install, f"runtime install log lacks {pkg}")
    for k in ("setup", "fingerprint", "check"):
        check_run(cov["setup_runs"][k], f"setup_runs.{k}")
    require(resolve(cov["setup_runs"]["check"]["stdout"]["path"]).read_text().startswith("PASS"), "static check did not pass")
    t = res["tools"]
    require(t["verifier_fingerprint"] == ident["verifier_fingerprint"] and t["host_cc"] == HOST_CC
            and t["run_py_sha256"] == files["run.py"], "result.json tool identities differ")

    # Negative controls prove the pipeline reports sanitizer errors.
    for n in ("neg-ubsan", "neg-asan"):
        nc = cov["negative_controls"][n]
        check_run(nc["run"], f"negative_controls.{n}", expect_exit=1)
        rep = load(nc["run"]["stdout"]["path"])
        require(rep.get("verdict") == "rejected" and rep.get("stage") == "fullcheck:sanitizer" and rep.get("exit") in (66, 67)
                and "runtime error" in rep.get("sanitizer", ""), f"negative control {n} was not rejected by a sanitizer")
        require(rep.get("sha256") != ENTRY_SHA, f"negative control {n} used the unmodified entry")
        require(resolve(nc["diff"]["path"]).read_text().count("\n+    {") == 1, f"negative control {n} diff missing")

    # Selected coverage set.
    sets = cov["sets"]
    selected = [k for k, s in sets.items() if s.get("selected")]
    require(selected == [cov.get("selected_set")], "exactly one compatible set must be selected")
    for name, s in sets.items():
        if name.startswith("prior"):
            for f in s["files"].values():
                require(f["sha256"] == f["packet_sha256"], f"prior {f['path']} differs from its packet")
            continue
        gaps, words = check_set(name, s, ident)
        if s.get("selected"):
            claimed = [tuple(g) for g in cov.get("gaps", [])]
            require(sorted(claimed) == gaps, f"selected set gaps {gaps} not reported exactly")
            if status == "pass":
                require(not gaps and words == 1 << 32, "pass claimed without whole-domain coverage")
                require(cov.get("failures") == [] and res.get("failures") == [] and res.get("gaps") == [],
                        "pass claimed with recorded failures or gaps")
                sel = s["ranges"]
                m = res["measured"]
                require(m["words_checked"] == sum(load(r["report"]["path"])["words_checked"] for r in sel) == 1 << 32
                        and m["mismatches"] == 0 and m["sanitizer_errors"] == 0 and m["quick"] is False
                        and m["verdict"] == "passed", "result.json measured facts unsupported")
                obj = s["objects"]
                require(resolve(obj["check_host"]["path"]).read_bytes()[:4] == b"\x7fELF", "check binary is not ELF")
                ldd = resolve(obj["ldd"]["path"]).read_text()
                require("libasan.so" in ldd and "libubsan.so" in ldd, "check binary is not linked with ASan and UBSan")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print(f"OK host/tanh coverage status={status}: selected {cov['selected_set']}, "
          f"{res['measured']['words_checked']} words, {res['measured']['mismatches']} mismatches, 0 sanitizer errors")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyError, TypeError, ValueError, IndexError, OSError) as exc:
        print(f"FAIL: malformed or missing evidence: {exc!r}")
        sys.exit(1)
