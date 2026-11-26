#!/usr/bin/env python3
"""Assemble scores.json, scores.md, current-references.json and result.json from the retained raw reports.

Run from the repository root after drive.py has produced raw/. verify.py recomputes everything this
writes from the raw data with its own code; this script is only the assembler.
"""
import hashlib, json, math
from pathlib import Path

ROOT = Path.cwd()
REL = "eik-work/final-validation/scores/heldout-1"
H = ROOT / REL
SEED = 849230117
BOARDS = ("rv32im", "thumbv6m", "overall")
TARGETS = ("rv32im", "thumbv6m", "thumbv7em")
FUNCTIONS = ("sigmoid", "tanh", "exp")
CAND, ID50 = "entry.c", "eik-work/baselines/former-50/entry.c"
SNAP = "eik-work/final-validation/boards/snapshot.json"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
dump = lambda p, v: Path(p).write_text(json.dumps(v, indent=1, sort_keys=True) + "\n")

ev_c = load(H / "raw/cand/evaluate-849230117.stdout")
ev_i = load(H / "raw/id50/evaluate-849230117.stdout")
cmp_ = load(H / "raw/cand/historical-compare-id50.stdout")
ms_i = load(H / "raw/id50/measure-849230117.stdout")
fp = load(H / "raw/cand/fingerprint.stdout")
ident = {k: fp[k] for k in ("verifier", "measurement", "sandbox")}
cm = cmp_["measure"]

def entry(rep, path, report, repeats):
    t = rep["targets"]
    return {"path": path, "sha256": rep["sha256"], "source_bytes": (ROOT / path).stat().st_size,
            "bytes": rep["bytes"], "images": rep["images"],
            "S": {**{x: rep["scores"][x]["S"] for x in TARGETS}, "overall": rep["scores"]["overall"]["S"]},
            "parts": {x: {"functions": rep["scores"][x]["functions"], "size_factor": rep["scores"][x]["size_factor"]} for x in TARGETS},
            "classes": {x: t[x]["functions"] for x in TARGETS},
            "tail_p999_hard": {x: {fn: t[x]["functions"][fn]["hard"]["p999"] for fn in FUNCTIONS} for x in TARGETS},
            "wrong_outputs": {x: len(t[x]["wrong"]) for x in TARGETS},
            "sample": {x: {"words": t[x]["sample"]["words"], "mismatches": t[x]["sample"]["mismatches"]} for x in TARGETS},
            "stack": {x: t[x]["stack"] for x in TARGETS},
            "report": report, "repeat_reports": repeats}

cand = entry(cm, CAND, "raw/cand/historical-compare-id50.stdout#/measure", ["raw/cand/evaluate-849230117.stdout"])
id50 = entry(ms_i, ID50, "raw/id50/measure-849230117.stdout",
             ["raw/id50/evaluate-849230117.stdout", "raw/cand/historical-compare-id50.stdout#/champions/" + ms_i["sha256"]])

hp = dict(cm["hard_pool"]); hp["files"] = {}
for fn in FUNCTIONS:
    f = next((H / "raw/cand/hard").glob(f"hardscan-*-{SEED}-{fn}.txt"))
    hp["files"][fn] = {"path": f"raw/cand/hard/{f.name}", "copy": f"raw/id50/hard/{f.name}", "sha256": sha(f),
                       "lines": len([l for l in f.read_text().splitlines() if l.strip()])}

snap = load(ROOT / SNAP)
refs = {"snapshot_path": SNAP, "snapshot_file_sha256": sha(ROOT / SNAP), "snapshot_utc": snap["snapshot_utc"],
        "snapshot_sha256": snap["snapshot_sha256"],
        "note": "extract of the landed board snapshot: per-board current champion and whether reference bytes exist",
        "boards": {b: {k: snap["per_board"][b][k] for k in ("champion_submission", "current_promotion_id", "declared_source_sha256",
                   "reference_path", "reference_sha256", "source_status", "source_reason_code", "published_absolute_S",
                   "champion_over_public_reference", "measurement_identity")} for b in BOARDS}}
dump(H / "current-references.json", refs)

id50_cmp, current = {}, {}
for b in BOARDS:
    r = cand["S"][b] / id50["S"][b]
    id50_cmp[b] = {"candidate_S": cand["S"][b], "id50_S": id50["S"][b], "ratio": r, "le_0970": r <= 0.97,
                   "denominator": "S of id50 on this board" if b != "overall" else "sqrt(rv32im S * thumbv6m S) of id50, the same source",
                   "kit_decision_ratio": cmp_["decision"]["boards"][b]["ratio"], "kit_decision_beats": cmp_["decision"]["boards"][b]["beats"],
                   "conditional_on": "exhaustive correctness (not established by this item)"}
    p = refs["boards"][b]
    current[b] = {"submission": p["champion_submission"], "declared_source_sha256": p["declared_source_sha256"],
                  "reference_available": False, "reason": p["source_reason_code"], "current_S": None, "ratio": None,
                  "le_0970": None, "eligibility": "undetermined",
                  "indicative_only_published_champion_over_id50": p["champion_over_public_reference"]}

cmds = {c: load(H / f"raw/{c}/commands.json") for c in ("cand", "id50")}
secs = {c: {x["label"]: x["seconds"] for x in cmds[c]} for c in cmds}
scores = {"kind": "paired-score-comparison", "seed": SEED, "inputs_sha256": cm["inputs_sha256"], "fingerprint": ident,
          "mode": fp["mode"], "takeover_ratio": 0.97, "hard_pool": hp,
          "populations": fp["details"]["measurement"]["constants"]["set_sizes"],
          "target_sample_words_per_function": fp["details"]["measurement"]["constants"]["target_sample"],
          "entries": {"candidate": cand, "id50": id50},
          "id50_comparison": id50_cmp, "current_reference": current,
          "kit_incumbent": {"label": "the kit's local incumbent (examples/incumbent.c), the default opponent of eik evaluate; "
                                     "not a board champion, and its ratio is not a takeover",
                            "S": {b: ev_c["comparison"][b]["champion_S"] for b in BOARDS},
                            "candidate_ratio": {b: ev_c["comparison"][b]["ratio"] for b in BOARDS},
                            "id50_ratio": {b: ev_i["comparison"][b]["ratio"] for b in BOARDS}},
          "evaluate": {n: {"status": r["status"], "seconds": r["seconds"], "timed_out": False, "cap_seconds": 600,
                           "candidate_boards_vs_kit_incumbent": r["candidate_boards"], "host_check": r["host_check"]}
                       for n, r in (("candidate", ev_c), ("id50", ev_i))},
          "seconds": secs}
dump(H / "scores.json", scores)

f = lambda x: f"{x:.12f}"
md = [f"# Held-out paired score comparison, seed {SEED}", "",
      f"- inputs_sha256 `{cm['inputs_sha256']}`; measurement identity `{ident['measurement']}`; verifier identity `{ident['verifier']}`",
      f"- candidate: `entry.c` sha256 `{cand['sha256']}`; id50: `{ID50}` sha256 `{id50['sha256']}`",
      f"- full populations per function: typical 2000, wide 1000, hard 300, uniform 1000; fresh hard pools "
      f"(sigmoid {hp['sizes']['sigmoid']}, tanh {hp['sizes']['tanh']}, exp {hp['sizes']['exp']}); target sample 98304 words per target, 0 wrong",
      "- status: **incomplete**. No current-board reference source is public, so no current S, ratio or eligibility exists.", "",
      "## Candidate vs former champion 50 (historical comparison, not a current board)", "",
      "| board | candidate S | id50 S | ratio | <= 0.970 |", "|---|---|---|---|---|"]
for b in BOARDS:
    r = id50_cmp[b]
    md.append(f"| {b} | {f(r['candidate_S'])} | {f(r['id50_S'])} | {f(r['ratio'])} | {'yes' if r['le_0970'] else 'no'} |")
md += ["", "The overall denominator is sqrt(rv32im S x thumbv6m S) of id50 itself. thumbv7em (reported only): candidate "
       f"{f(cand['S']['thumbv7em'])}, id50 {f(id50['S']['thumbv7em'])}.", "",
       "## Candidate vs current board references", "",
       "| board | current champion | reference bytes | current S | ratio | eligibility |", "|---|---|---|---|---|---|"]
for b in BOARDS:
    c = current[b]
    md.append(f"| {b} | submission {c['submission']} (`{c['declared_source_sha256'][:12]}`) | none ({c['reason']}) | null | null | undetermined |")
md += ["", "## Per-class mean instructions per call (typical / wide / hard / uniform), code bytes, hard p99.9", "",
       "| entry | target | function | typical | wide | hard | uniform | hard p99.9 | bytes |", "|---|---|---|---|---|---|---|---|---|"]
for n, e in (("candidate", cand), ("id50", id50)):
    for t in TARGETS:
        for fn in FUNCTIONS:
            c = e["classes"][t][fn]
            md.append(f"| {n} | {t} | {fn} | {c['typical']['mean']:.4f} | {c['wide']['mean']:.4f} | {c['hard']['mean']:.4f} | "
                      f"{c['uniform']['mean']:.4f} | {c['hard']['p999']} | {e['bytes'][t]} |")
md += ["", "## eik evaluate --quick --json (opponent: the kit's local incumbent, not a board champion)", "",
       "| entry | status | seconds | timed out | quick host check (3 functions x 134217728 words) |", "|---|---|---|---|---|"]
for n, r in (("candidate", ev_c), ("id50", ev_i)):
    md.append(f"| {n} | {r['status']} | {r['seconds']} | no (cap 600 s) | 0 wrong, complete=false |")
md += ["", "The evaluate status only says the entry is far below the kit's ~140k-instruction incumbent; the incumbent state "
       "was left as setup made it. It is not a takeover of any live board.", ""]
(H / "scores.md").write_text("\n".join(md))

setup = []
for label, argv in (("provision", ["python3", "eik-work/toolkit/provision.py", "--fetch"]),
                    ("bootstrap", ["python3", "eik-work/toolkit/verify.py", "bootstrap", "--offline"])):
    setup.append({"label": label, "argv": argv, "exit_code": int((H / f"raw/{label}.exit").read_text()),
                  "stdout": f"raw/{label}.stdout", "stdout_sha256": sha(H / f"raw/{label}.stdout"),
                  "stderr": f"raw/{label}.stderr", "stderr_sha256": sha(H / f"raw/{label}.stderr"),
                  "note": "re-run after the measurements to retain its log; the first run before them printed the same result"})
dump(H / "raw/setup-commands.json", setup)

gaps = [
    "No current-board reference is available: the sources of submissions 52 (rv32im), 53 (thumbv6m) and 56 (overall) are withheld "
    "(HTTP 403 SOURCE_WITHHELD in the landed board snapshot), so current S, ratios and <=0.970 eligibility are null/undetermined on every board.",
    "eik compare --champion BOARD=FILE was therefore run only against former champion 50 (labelled historical); no compare against a current reference exists.",
    "Against id50 the candidate does not reach 0.970 on any board (ratios 1.000000, 1.000318, 1.000159); the published takeover ratios put the current "
    "thumbv6m and overall champions about 3.2% below id50, which is indicative only and not a same-seed measurement.",
    "Exhaustive correctness is not established here: evaluate ran the quick 3% host check only (0 wrong); the full host and target coverage belongs to the coverage targets.",
    "The reduced offline-runtime export cannot bootstrap; the pinned Zig/Unicorn wheels and QEMU assets were restored with the unchanged toolkit/provision.py --fetch "
    "(every asset verified against the manifest) into scratch, and the evaluator then ran offline through toolkit/run.py.",
    "The runtime, guest images and build cache lived in test/scratch and are not retained; image sha256s are recorded in the measure reports.",
    "The evaluate status 'would-take-over-after-full-check' refers to the kit's local incumbent state created by eik setup, not to any live board.",
]
result = {
    "kind": "heldout-score-comparison", "item": "heldout-1", "status": "incomplete",
    "status_reason": "measurements completed and verified, but every current-board reference is missing, so eligibility is undetermined",
    "seed": SEED, "inputs_sha256": cm["inputs_sha256"],
    "sources": {"candidate": {"path": CAND, "sha256": cand["sha256"]}, "id50": {"path": ID50, "sha256": id50["sha256"]},
                "current_references": {b: {"submission": current[b]["submission"], "declared_source_sha256": current[b]["declared_source_sha256"],
                                           "available": False} for b in BOARDS}},
    "tools": {"fingerprint": ident, "versions": fp["details"]["tools"], "mode": fp["mode"],
              "runner": {"path": "eik-work/toolkit/run.py", "sha256": sha(ROOT / "eik-work/toolkit/run.py")},
              "toolkit_manifest_sha256": sha(ROOT / "eik-work/toolkit/manifest.json"),
              "toolkit_files_sha256": sha(ROOT / "eik-work/toolkit/files.json")},
    "measured": {"candidate_S": cand["S"], "id50_S": id50["S"], "id50_ratio": {b: id50_cmp[b]["ratio"] for b in BOARDS},
                 "id50_le_0970": {b: id50_cmp[b]["le_0970"] for b in BOARDS}, "id50_any_le_0970": any(id50_cmp[b]["le_0970"] for b in BOARDS),
                 "current_S": {b: None for b in BOARDS}, "current_ratio": {b: None for b in BOARDS},
                 "eligibility": {b: "undetermined" for b in BOARDS},
                 "wrong_outputs": 0, "target_sample_mismatches": 0, "quick_host_check_mismatches": 0,
                 "evaluate_status": {"candidate": ev_c["status"], "id50": ev_i["status"]}, "evaluate_timed_out": False,
                 "hard_pool_sizes": hp["sizes"], "code_bytes": {"candidate": cand["bytes"], "id50": id50["bytes"]}},
    "boards_candidate_would_take": [],
    "deviations": ["none from eik evaluate --quick --json --seed 849230117: both evaluations completed inside the 600 s cap, so the measure + quick fullcheck fallback was not used"],
    "gaps": gaps,
    "commands": cmds["cand"] + cmds["id50"] + setup,
    "verify": "python3 eik-work/final-validation/scores/heldout-1/verify.py",
}
arts = {f"{REL}/{p.relative_to(H).as_posix()}": sha(p) for p in sorted(H.rglob("*"))
        if p.is_file() and p.name != "result.json" and "__pycache__" not in p.parts}
arts.update({CAND: sha(ROOT / CAND), ID50: sha(ROOT / ID50)})
result["artifacts"] = arts
dump(H / "result.json", result)
print("built", len(arts), "artifacts")
