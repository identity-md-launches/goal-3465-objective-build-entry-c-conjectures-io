#!/usr/bin/env python3
"""Regenerates result.json from the retained evidence (stdlib only)."""
import hashlib, json, os, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.."))
D = "eik-work/final-validation/coverage/rv32im-exp"
T = "eik-work/trials/m0-tanh-refine"
def sha(p):
    return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()
files = [T + "/targetcheck-rv32im-exp-all." + e for e in ("json", "stdout", "stderr")]
files += [T + "/entry.c", T + "/packet.json", T + "/fingerprint.json", "entry.c",
          "eik-work/freeze/evidence/objects/guest-rv32im.elf", "eik-work/freeze/evidence/objects/sub-rv32im.o",
          "eik-work/offline-runtime/manifest.json", "eik-work/offline-runtime/result.json",
          D + "/logs/prepare.stdout", D + "/logs/prepare.stderr", D + "/logs/prepare.exit"]
rep = json.load(open(os.path.join(ROOT, T + "/targetcheck-rv32im-exp-all.stdout")))
res = {
 "schema": "rv32im-exp-coverage-1",
 "status": "incomplete",
 "function": "exp", "runtime": "rv32im",
 "source": {"path": "entry.c", "sha256": sha("entry.c"), "trial_copy": T + "/entry.c"},
 "tool_identities": {"fingerprint": rep["fingerprint"], "report_schema": rep["schema"],
   "prior_image_sha256": rep["image_sha256"]},
 "ranges": [{"lo": 0, "hi": 4096, "half_open": True, "words": rep["words_checked"],
   "mismatches": rep["mismatches"], "provenance": "reused-unbound", "report": T + "/targetcheck-rv32im-exp-all.stdout"}],
 "claimed_pass_ranges": [],
 "measured_facts": {"prior_report_verdict": rep["verdict"], "prior_report_complete": rep["complete"],
   "prior_report_range_complete": rep["range_complete"], "prior_words_checked": rep["words_checked"],
   "prior_mismatches": rep["mismatches"], "prior_exit_code": 0, "prior_seconds": 298.325},
 "commands": [
  {"cmd": "python3 eik-work/toolkit/run.py test/scratch/m0-tanh-refine rv32im-complete targetcheck-rv32im-exp-all targetcheck eik-work/trials/m0-tanh-refine/entry.c --function exp --target rv32im --jobs 1", "exit": 0, "origin": "prior run (recorded in packet.json)"},
  {"cmd": "python3 eik-work/offline-runtime/prepare.py $TMPDIR/deps2", "exit": 1, "origin": "this run", "stderr": D + "/logs/prepare.stderr"}],
 "gaps": [
  "Prior report's image_sha256 (4c46aa4f...) is not bound to any retained linked image: the repo keeps no guest image with that hash; freeze guest-rv32im.elf has a different hash (81d8958e...) and belongs to the freeze build, so section/load-address/relocation equivalence cannot be shown.",
  "Prior run's runtime ($REPO/test/scratch/m0-tanh-refine/runtime) is not retained; runtime identity is unproven.",
  "Rerun impossible: offline-runtime/prepare.py exits 1 because Zig wheel, Unicorn wheel and QEMU source archive are absent from the reduced export.",
  "Hence no chunk range [0,4096) is established as exhaustively covered by a compatible, identity-bound run; the prior report is kept as unbound evidence only."],
 "artifacts": {p: sha(p) for p in files},
}
json.dump(res, open(os.path.join(ROOT, D, "result.json"), "w"), indent=1, sort_keys=True)
