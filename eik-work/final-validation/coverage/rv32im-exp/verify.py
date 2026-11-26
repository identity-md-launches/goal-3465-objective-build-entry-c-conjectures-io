#!/usr/bin/env python3
"""Offline validator (stdlib only) for the rv32im/exp coverage packet."""
import hashlib, json, os, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.."))
D = "eik-work/final-validation/coverage/rv32im-exp"
FROZEN = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
def fail(m):
    print("FAIL:", m); sys.exit(1)
def sha(p):
    try:
        return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()
    except OSError:
        fail("missing evidence " + p)
try:
    r = json.load(open(os.path.join(ROOT, D, "result.json")))
except Exception as e:
    fail("result.json: %s" % e)
for k in ("status", "source", "tool_identities", "artifacts", "commands", "measured_facts", "gaps", "ranges"):
    if k not in r: fail("missing key " + k)
if r["status"] not in ("pass", "fail", "incomplete"): fail("bad status")
for p, h in r["artifacts"].items():
    if sha(p) != h: fail("hash mismatch " + p)
if sha("entry.c") != FROZEN or r["source"]["sha256"] != FROZEN: fail("root entry.c not frozen")
T = "eik-work/trials/m0-tanh-refine/"
rep = json.loads(open(os.path.join(ROOT, T + "targetcheck-rv32im-exp-all.stdout")).read())
meta = json.load(open(os.path.join(ROOT, T + "targetcheck-rv32im-exp-all.json")))
raw_ok = (meta["exit_code"] == 0 and meta["stdout_sha256"] == sha(T + "targetcheck-rv32im-exp-all.stdout")
          and meta["stderr_sha256"] == sha(T + "targetcheck-rv32im-exp-all.stderr")
          and meta["source_sha256"] == FROZEN and sha(T + "entry.c") == FROZEN
          and rep["sha256"] == FROZEN and rep["function"] == "exp" and rep["target"] == "rv32im"
          and rep["verdict"] == "passed" and rep["complete"] is True and rep["range_complete"] is True
          and rep["mismatches"] == 0 and rep["words_checked"] == 2**32
          and (rep["chunk_lo"], rep["chunk_hi"]) == (0, 4096) and rep["reasons"] == []
          and rep["fingerprint"] == r["tool_identities"]["fingerprint"])
if not raw_ok: fail("raw prior report inconsistent")
# range sanity: sorted, disjoint, no gaps, counts match 2^20 words per chunk
rs = sorted(r["ranges"], key=lambda x: x["lo"]); pos = 0
for x in rs:
    if x["lo"] != pos: fail("gap or overlap at chunk %d" % pos)
    if x["words"] != (x["hi"] - x["lo"]) * (1 << 20): fail("count mismatch")
    pos = x["hi"]
covered = pos == 4096
bound = [x for x in r["ranges"] if x["provenance"] in ("reused-bound", "rerun")]
if r["status"] == "pass":
    if not covered or sum(x["mismatches"] for x in r["ranges"]) or len(bound) != len(r["ranges"]):
        fail("unsupported pass claim")
    if r["gaps"] or any(c["exit"] != 0 for c in r["commands"]): fail("pass with gaps/failed commands")
else:
    if not r["gaps"]: fail("non-pass without stated gaps")
    if r["claimed_pass_ranges"]: fail("non-pass claims ranges")
    if r["status"] == "incomplete" and bound and covered: fail("incomplete although fully bound")
if r["status"] == "incomplete" and open(os.path.join(ROOT, D, "logs/prepare.exit")).read().strip() != "1":
    fail("rerun-failure evidence missing")
print("OK: evidence consistent; status=%s (gaps: %d)" % (r["status"], len(r["gaps"])))
