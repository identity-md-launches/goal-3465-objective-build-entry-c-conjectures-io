#!/usr/bin/env python3
"""Offline verifier for the dated conjectures.io board snapshot (Python standard library only).

    python3 eik-work/final-validation/boards/verify.py

No network, no evaluator, no credentials: every claim in snapshot.json is re-derived from the raw
response bodies saved beside it, and every saved byte is hashed.

It refuses to pass unless all of the following hold:
  * snapshot_sha256 is the canonical digest of the snapshot it is stored in, and the declared file
    ledger matches the raw/ and references/ directories exactly (no missing, extra or edited file);
  * the request ledger is internally sound: anonymous GETs over https to the competition API only,
    no credential header of any kind, a UTC timestamp with an offset per request, a body hash that
    matches the saved bytes, and exactly the URLs the snapshot's scope implies;
  * the boards and the three leaderboards are consistent: same board set, same configuration hash,
    each reference promotion is that board's current promotion, and the reference hash is the
    referenced submission's declared source hash;
  * every promotion id the public data mentions is re-resolved here from declared source hashes, and
    the recorded resolution (or its documented absence) matches;
  * every source request is re-classified from its own response: 200 plus a hash match -> a retained
    public reference whose bytes are the declared source; 403 SOURCE_WITHHELD -> withheld with the
    raw error body and no reference file; anything else -> documented, not a reference;
  * every recorded S ratio is the decision score of the evaluation it cites, is flagged as a
    takeover ratio, and never claims an absolute S: published_absolute_S is null on every board,
    the derived champion-over-baseline product is re-multiplied from the cited ratios, and no raw
    body carries an absolute per-call score field;
  * the status block's counts match the recomputation, and each board's withheld champion source is
    named in the gaps.

It also proves it can fail: a set of tampered copies of this snapshot (edited ratio, withheld source
promoted to published, flipped reference byte, deleted raw body, absolute S invented, altered
promotion resolution, extra file, dropped board, request status rewritten) must each be rejected.
"""
import copy
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SNAPSHOT = "snapshot.json"
BOARDS = ("rv32im", "thumbv6m", "overall")
FORMER = (37, 42, 46, 48, 50)
API = "https://conjectures.io/v1/competitions/exact-integer-kernels/"
DIGEST = re.compile(r"^[0-9a-f]{64}$")
CREDENTIAL_HEADERS = ("authorization", "proxy-authorization", "cookie", "set-cookie",
                      "x-api-key", "api-key", "x-auth-token")
ABSOLUTE_KEYS = ("absolute_s", "s_absolute", "score_per_call", "instructions_per_call",
                 "absolute_score", "s_per_call")


class Fail(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise Fail(msg)


def digest(b):
    return sha256(b).hexdigest()


def jload(p):
    try:
        return json.loads(Path(p).read_bytes())
    except Exception as e:
        raise Fail(f"{p}: not readable JSON ({e})")


def load(root):
    return jload(Path(root) / SNAPSHOT)


def canonical(snap):
    body = {k: v for k, v in snap.items() if k != "snapshot_sha256"}
    return digest(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def http_body(root, record):
    p = Path(root) / record["path"]
    need(p.is_file(), f"missing response body {record['path']}")
    return p.read_bytes()


def walk_keys(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield path + "/" + str(k), str(k).lower()
            yield from walk_keys(v, path + "/" + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_keys(v, f"{path}/{i}")


# ---------------------------------------------------------------- request ledger
def check_requests(root, snap):
    reqs = snap["requests"]
    need(isinstance(reqs, dict) and reqs, "no request ledger")
    ledger = jload(Path(root) / "raw/requests.json")
    need(ledger == reqs, "raw/requests.json and the recorded ledger disagree")
    seen_urls = set()
    for key, r in reqs.items():
        need(set(r) >= {"url", "method", "started_utc", "finished_utc", "http_status", "headers",
                        "bytes", "sha256", "path", "error"}, f"{key}: incomplete request record")
        need(r["method"] == "GET", f"{key}: not a GET")
        need(r["url"].startswith(API) and r["url"].count("://") == 1, f"{key}: off-API url")
        need(r.get("final_url", r["url"]) == r["url"], f"{key}: redirected elsewhere")
        need(not re.search(r"//[^/]*@", r["url"]), f"{key}: url carries userinfo")
        need(r["url"] not in seen_urls, f"{key}: duplicate request url")
        seen_urls.add(r["url"])
        hdr = {k.lower(): v for k, v in r["headers"].items()}
        for h in CREDENTIAL_HEADERS:
            need(h not in hdr, f"{key}: credential header {h!r} present (snapshot must be anonymous)")
        need(isinstance(r["http_status"], int) and 0 <= r["http_status"] <= 599, f"{key}: bad status")
        for f in ("started_utc", "finished_utc"):
            dt = datetime.fromisoformat(r[f])
            need(dt.utcoffset() is not None and dt.utcoffset().total_seconds() == 0,
                 f"{key}: {f} is not UTC")
        started = datetime.fromisoformat(r["started_utc"])
        finished = datetime.fromisoformat(r["finished_utc"])
        need(started <= finished, f"{key}: finishes before it starts")
        need(datetime.fromisoformat(snap["snapshot_utc"]) >= finished, f"{key}: recorded after the snapshot")
        body = http_body(root, r)
        need(len(body) == r["bytes"], f"{key}: body length differs from the record")
        need(digest(body) == r["sha256"], f"{key}: body hash differs from the record")
        need(r["sha256"] in snap["files"].get(r["path"], {}).get("sha256", ""),
             f"{key}: body hash is not the declared file hash")
    return reqs


def check_files(root, snap):
    declared = snap["files"]
    need(isinstance(declared, dict) and declared, "no file ledger")
    on_disk = set()
    for d in ("raw", "references"):
        probe = Path(root) / d
        need(probe.is_dir(), f"missing directory {d}")
        need(not [p for p in probe.iterdir() if p.is_dir()], f"{d}/ holds a directory")
        on_disk |= {str(p.relative_to(root)) for p in probe.iterdir() if p.is_file()}
    need(on_disk == set(declared), f"file set differs: undeclared {sorted(on_disk - set(declared))}, "
                                   f"missing {sorted(set(declared) - on_disk)}")
    for path, meta in declared.items():
        p = Path(root) / path
        need(len(p.read_bytes()) == meta["bytes"], f"{path}: size differs from the ledger")
        need(digest(p.read_bytes()) == meta["sha256"], f"{path}: hash differs from the ledger")
        need(DIGEST.match(meta["sha256"]) is not None, f"{path}: malformed digest")


# ---------------------------------------------------------------- rebuild from raw
def rebuild(root, snap, reqs):
    """Re-derive promotions, entries and scores from the saved response bodies alone."""
    boards_body = jload(Path(root) / reqs["boards"]["path"])
    boards = {b["id"]: b for b in boards_body["boards"]}
    leaders = {b: jload(Path(root) / reqs[f"leaderboard-{b}"]["path"]) for b in BOARDS}
    ids = set()
    for b in BOARDS:
        ref = leaders[b]["reference"]
        ids.add(ref["submission"])
        for ch in leaders[b].get("challengers") or []:
            ids.add(ch["submission"])
    ids |= set(FORMER)
    metas = {i: jload(Path(root) / reqs[f"submission-{i}"]["path"]) for i in sorted(ids)}
    for i, m in metas.items():
        need(m.get("id") == i, f"submission {i}: response names id {m.get('id')!r}")
    return boards_body, boards, leaders, metas


def expected_promotions(reqs, leaders, metas):
    by_sub = {i: m.get("source_sha256") for i, m in metas.items()}
    hashes, stated = {}, {}
    for b in BOARDS:
        ref = leaders[b]["reference"]
        p = ref["promotion_id"]
        hashes.setdefault(p, {}).setdefault(ref["source_sha256"], []).append(
            f"raw/leaderboard-{b}.json#/reference/source_sha256")
        stated.setdefault(p, {}).setdefault(ref["submission"], []).append(
            f"raw/leaderboard-{b}.json#/reference/submission")
    for i, m in metas.items():
        for j, ev in enumerate(m.get("evaluations") or []):
            p, h = ev.get("reference_promotion_id"), ev.get("reference_hash")
            if p is None or h is None:
                continue
            hashes.setdefault(p, {}).setdefault(h, []).append(
                f"raw/submission-{i}.json#/evaluations/{j}/reference_hash")
    out = {}
    for p in sorted(hashes):
        cands = set()
        for h in hashes[p]:
            cands |= {i for i, dh in by_sub.items() if dh == h}
        st = set(stated.get(p, {}))
        resolved = len(cands) == 1 and (not st or st == cands)
        out[str(p)] = {
            "promotion_id": p,
            "resolved_submission": sorted(cands)[0] if resolved else None,
            "status": "resolved" if resolved else ("ambiguous" if cands else "unresolved"),
            "attributed_hashes": sorted(hashes[p]),
            "hash_provenance": sorted({x for v in hashes[p].values() for x in v}),
            "leaderboard_stated_submission": sorted(st)[0] if len(st) == 1 else None,
            "leaderboard_provenance": sorted({x for v in stated.get(p, {}).values() for x in v}),
            "note": (None if resolved else
                     "declared reference hash matches no submission in this snapshot; "
                     "not attributable to a submission from the public data fetched here"),
        }
    return out


def expected_entries(root, reqs, leaders, metas, promotions):
    roles = {}
    for b in BOARDS:
        ref = leaders[b]["reference"]
        roles.setdefault(ref["submission"], []).append({"board": b, "role": "leaderboard-reference",
                                                        "promotion_id": ref["promotion_id"]})
        for ch in leaders[b].get("challengers") or []:
            roles.setdefault(ch["submission"], []).append({"board": b, "role": "leaderboard-challenger",
                                                           "evaluation_id": ch.get("evaluation_id")})
    for i in FORMER:
        roles.setdefault(i, []).append({"board": None, "role": "former-champion"})
    entries = {}
    for i in sorted(roles):
        m = metas[i]
        declared = m.get("source_sha256")
        rec = reqs[f"source-{i}"]
        body = http_body(root, rec)
        e = {"submission": i, "roles": roles[i], "declared_source_sha256": declared,
             "hash_provenance": f"raw/submission-{i}.json#/source_sha256",
             "source_available_flag": m.get("source_available"), "source_request": f"source-{i}",
             "status": None, "path": None, "downloaded_sha256": digest(body),
             "reason_code": None, "detail": None,
             "promotion_ids": sorted({p["promotion_id"] for p in promotions.values()
                                      if p["resolved_submission"] == i and p["promotion_id"] is not None})}
        if rec["http_status"] == 200 and rec["error"] is None:
            if e["downloaded_sha256"] == declared:
                e["status"], e["path"] = "published", f"references/id{i}.c"
            else:
                e["status"], e["path"] = "hash-mismatch", f"raw/source-{i}.c"
        else:
            e["path"] = f"raw/source-{i}.json"
            try:
                err = json.loads(body)
            except Exception:
                err = {}
            e["reason_code"], e["detail"] = err.get("reason_code"), err.get("detail")
            e["status"] = "withheld" if rec["http_status"] == 403 else "error"
        need(rec["path"] == e["path"], f"source {i}: ledger path {rec['path']} is not {e['path']}")
        entries[i] = e
    return entries


def expected_scores(reqs, boards, leaders, metas, promotions, entries):
    scores = {}
    for b in BOARDS:
        ref = leaders[b]["reference"]
        current = boards[b]["current_promotion_id"]
        records = []
        for i in sorted(metas):
            for j, ev in enumerate(metas[i].get("evaluations") or []):
                if ev.get("board") != b:
                    continue
                d = ev.get("decision") or {}
                rp = ev.get("reference_promotion_id")
                records.append({
                    "submission": i, "evaluation_id": ev["id"], "state": ev.get("state"),
                    "ratio": d.get("score"), "outcome": d.get("outcome"), "reason": d.get("reason"),
                    "ratio_kind": "takeover-ratio: S_submission / S_reference_at_that_time",
                    "reference_promotion_id": rp,
                    "reference_submission": promotions.get(str(rp), {}).get("resolved_submission"),
                    "reference_hash": ev.get("reference_hash"),
                    "measured_against_current_champion": rp == current,
                    "completed_at": ev.get("completed_at"),
                    "provenance": f"raw/submission-{i}.json#/evaluations/{j}",
                    "leaderboard_ratio": next((c.get("ratio") for c in (leaders[b].get("challengers") or [])
                                               if c.get("submission") == i), None)})
        records.sort(key=lambda r: (r["evaluation_id"] or 0))
        scores[b] = {
            "champion_submission": ref["submission"],
            "champion_promotion_id": ref["promotion_id"],
            "champion_declared_source_sha256": ref["source_sha256"],
            "published_absolute_S": None,
            "published_absolute_S_note": ("the public API publishes no absolute S per call for this board; "
                                          "only S ratios recorded at takeover time, which are relative to "
                                          "the champion of that moment and not comparable across the season"),
            "ratio_records": records,
            "ratios_against_current_champion": [r["evaluation_id"] for r in records
                                                if r["measured_against_current_champion"]],
            "champion_takeover": [{"evaluation_id": r["evaluation_id"], "ratio": r["ratio"],
                                   "reference_promotion_id": r["reference_promotion_id"],
                                   "reference_submission": r["reference_submission"],
                                   "provenance": r["provenance"]}
                                  for r in records
                                  if r["submission"] == ref["submission"] and r["outcome"] == "qualifies"],
        }
        steps, base, why = chain(b, ref["submission"], metas, promotions, entries)
        product = 1.0
        for s in steps:
            product *= s["ratio"]
        scores[b]["champion_over_public_reference"] = {
            "derived": True,
            "not_published": ("a product of published takeover ratios, computed here; the API publishes "
                              "no such number and no absolute S"),
            "baseline_submission": base,
            "baseline_status": (None if base is None else entries[base]["status"]),
            "chain": steps,
            "S_champion_over_baseline": (round(product, 15) if base is not None else None),
            "candidate_bar_over_baseline": (round(0.97 * product, 15) if base is not None else None),
            "open_reason": why,
            "caveat": ("indicative only: the validator scored these ratios on its own inputs, while the "
                       "goal's local comparisons run on local seeds, so this product shows how far the "
                       "champion sits above the public reference, it does not replace measuring it"),
        }
    return scores


def chain(b, sub, metas, promotions, entries):
    steps, seen = [], set()
    while sub is not None and sub not in seen and entries.get(sub, {}).get("status") != "published":
        seen.add(sub)
        found = next(((j, e) for j, e in enumerate(metas[sub].get("evaluations") or [])
                      if e.get("board") == b and (e.get("decision") or {}).get("outcome") == "qualifies"), None)
        if found is None:
            return steps, None, "no qualifying evaluation on this board for submission %d" % sub
        j, ev = found
        rp = ev.get("reference_promotion_id")
        nxt = promotions.get(str(rp), {}).get("resolved_submission")
        steps.append({"submission": sub, "evaluation_id": ev["id"], "ratio": ev["decision"]["score"],
                      "reference_promotion_id": rp, "reference_submission": nxt,
                      "provenance": f"raw/submission-{sub}.json#/evaluations/{j}/decision/score"})
        if nxt is None:
            return steps, None, (f"promotion {rp} does not resolve to any submission in this snapshot, "
                                 f"so no published ratio ties this board's champion to a public reference")
        sub = nxt
    if sub in seen:
        return steps, None, "cycle"
    return steps, sub, None


# ---------------------------------------------------------------- semantic checks
def check_semantics(snap, metas):
    for b, s in snap["scores"].items():
        need(s["published_absolute_S"] is None, f"{b}: claims a published absolute S")
        for r in s["ratio_records"]:
            need(isinstance(r["ratio"], float), f"{b}: evaluation {r['evaluation_id']} has no ratio")
            need(r["ratio_kind"].startswith("takeover-ratio"), f"{b}: ratio not labelled a takeover ratio")
            if r["outcome"] == "qualifies":
                need(r["ratio"] <= 0.97, f"{b}: a qualifying entry above the 0.97 bar ({r['ratio']})")
                need(r["reason"] is None, f"{b}: qualifying entry carries an above-bar reason")
            elif r["outcome"] == "above-bar":
                need(r["ratio"] > 0.97, f"{b}: above-bar entry under the bar ({r['ratio']})")
                need(r["reason"] == f"S ratio {r['ratio']:.4f} > 0.97",
                     f"{b}: reason {r['reason']!r} does not report an S ratio")
            need(r["leaderboard_ratio"] in (None, r["ratio"]),
                 f"{b}: leaderboard and submission records disagree for evaluation {r['evaluation_id']}")
            need(r["reference_hash"] is not None or r["reference_promotion_id"] is None,
                 f"{b}: ratio without the reference it was measured against")
        # a ratio is only tied to a hash the API names; the entry it names must exist in the snapshot
        # or be documented as unresolved, never silently resolved to something else
        for step in s["champion_over_public_reference"]["chain"]:
            need(step["reference_submission"] is not None or step["ratio"] is not None,
                 f"{b}: broken chain step")
    for i, m in metas.items():
        for ev in m.get("evaluations") or []:
            need(not (ev.get("decision") or {}).get("suite_scores"),
                 f"submission {i}: unrecorded published suite scores")


def check_no_absolute_fields(root, reqs):
    for key, r in reqs.items():
        if r["http_status"] != 200:
            continue
        try:
            body = json.loads(http_body(root, r))
        except Exception:
            continue                                          # a source body, not JSON
        for path, k in walk_keys(body):
            need(k not in ABSOLUTE_KEYS, f"{key}: raw body carries {path}, an absolute per-call score "
                                         f"the snapshot does not record")


def check_status(root, snap):
    st = snap["status"]
    need(st["snapshot"] == "complete", "snapshot status is not complete")
    entries = snap["entries"]
    summary = st["summary"]
    expect = {
        "boards": len(BOARDS),
        "submissions_requested": len(entries),
        "sources_published": sum(1 for e in entries.values() if e["status"] == "published"),
        "sources_withheld": sum(1 for e in entries.values() if e["status"] == "withheld"),
        "sources_hash_mismatch": sum(1 for e in entries.values() if e["status"] == "hash-mismatch"),
        "sources_error": sum(1 for e in entries.values() if e["status"] == "error"),
        "published_absolute_S": sum(1 for b in BOARDS if snap["scores"][b]["published_absolute_S"] is not None),
    }
    need(summary == expect, f"status summary {summary} does not match the evidence {expect}")
    gaps = " ".join(snap["gaps"])
    for b in BOARDS:
        sub = snap["board_references"][b]["submission"]
        if entries[str(sub)]["status"] != "published":
            need(str(sub) in gaps, f"{b}: withheld source {sub} is not stated in the gaps")
            need(entries[str(sub)]["reason_code"] is not None,
                 f"{b}: withheld source {sub} carries no reason code")
    need("absolute S per call is published" in gaps, "the absence of a published absolute S is not stated")
    need(len(set(snap["gaps"])) == len(snap["gaps"]), "duplicate gap statements")


def check_result(root, snap):
    """The item result must describe this snapshot and only bytes that are on disk."""
    p = Path(root) / "result.json"
    need(p.is_file(), "result.json is missing")
    res = jload(p)
    need(res.get("status") == "pass", "result.json does not claim a passing checked item")
    need(res["item"] == "board-snapshot" and res["batch"] == "e04-evidence-finalisation",
         "result.json names another item")
    need(res["source"]["snapshot_sha256"] == snap["snapshot_sha256"], "result.json cites another snapshot")
    need(res["generated_utc"] == snap["snapshot_utc"], "result.json was generated at another time")
    need(res["gaps"] == snap["gaps"], "result.json states other gaps")
    for c in res["commands"]:
        need(c["exit"] == 0, f"result.json records a failing command: {c['command']}")
    need(res["tool"]["standard_library_only"] is True and res["tool"]["network_during_verify"] is False,
         "result.json does not claim an offline standard-library check")
    declared = {a["path"]: a for a in res["artifacts"]}
    need("snapshot.json" in declared and "verify.py" in declared, "result.json does not hash its evidence")
    for path, a in declared.items():
        f = Path(root) / path
        need(f.is_file(), f"result.json cites a missing file {path}")
        need(len(f.read_bytes()) == a["bytes"] and digest(f.read_bytes()) == a["sha256"],
             f"result.json cites a hash that {path} does not have")
    facts = res["measured_facts"]
    for b in BOARDS:
        ref = snap["board_references"][b]
        need(facts["boards"][b]["submission"] == ref["submission"]
             and facts["boards"][b]["source_sha256"] == ref["source_sha256"], f"result.json misstates {b}")
        c = snap["scores"][b]["champion_over_public_reference"]
        need(facts["champion_over_public_reference"][b]["S_champion_over_baseline"]
             == c["S_champion_over_baseline"], f"result.json misstates the {b} baseline ratio")
        need(facts["published_absolute_S"][b] is None, f"result.json claims a published absolute S for {b}")
    need(facts["withheld_sources"] == sorted(int(i) for i, e in snap["entries"].items()
                                             if e["status"] == "withheld"),
         "result.json misstates which sources are withheld")
    need(facts["public_references"] == sorted(int(i) for i, e in snap["entries"].items()
                                              if e["status"] == "published"),
         "result.json misstates which references are public")


def validate(root="."):
    root = Path(root)
    snap = load(root)
    for k in ("snapshot_utc", "workspace", "api_base", "environment", "configuration", "boards",
              "board_references", "promotions", "entries", "scores", "requests", "files", "gaps", "status"):
        need(k in snap, f"snapshot has no {k}")
    need(snap["snapshot_sha256"] == canonical(snap), "snapshot_sha256 is not the digest of this snapshot")
    dt = datetime.fromisoformat(snap["snapshot_utc"])
    need(dt.utcoffset() is not None and dt.utcoffset().total_seconds() == 0, "snapshot_utc is not UTC")
    need(snap["api_base"] == API, "unexpected API base")
    need(set(snap["boards"]) == set(BOARDS), "the snapshot does not carry exactly the three boards")
    need(set(snap["board_references"]) == set(BOARDS), "the snapshot does not carry three board references")
    need(set(snap["scores"]) == set(BOARDS), "the snapshot does not carry three score records")

    check_files(root, snap)
    reqs = check_requests(root, snap)

    body, boards, leaders, metas = rebuild(root, snap, reqs)

    # -- expected request set -------------------------------------------------------------
    ids = set(FORMER)
    for b in BOARDS:
        ids.add(leaders[b]["reference"]["submission"])
        ids |= {c["submission"] for c in leaders[b].get("challengers") or []}
    expected_urls = {API + "boards"} | {API + f"leaderboard?board={b}" for b in BOARDS} \
        | {API + f"submissions/{i}" for i in ids} | {API + f"submissions/{i}/source" for i in ids}
    need({r["url"] for r in reqs.values()} == expected_urls,
         "request set is not exactly the boards, three leaderboards, and each submission and its source")
    for i in ids:
        need(reqs[f"submission-{i}"]["http_status"] == 200, f"submission {i} did not answer 200")

    # -- boards and leaderboards ----------------------------------------------------------
    need(set(boards) == set(BOARDS), f"board set {sorted(boards)} is not {sorted(BOARDS)}")
    need(snap["configuration"]["configuration_hash"] == body.get("configuration_hash"),
         "configuration hash differs from the boards response")
    need(snap["configuration"]["publication_hash"] == body.get("publication_hash"),
         "publication hash differs from the boards response")
    for b in BOARDS:
        need(snap["boards"][b]["config_hash"] == boards[b].get("config_hash"), f"{b}: config hash differs")
        need(snap["boards"][b]["current_promotion_id"] == boards[b].get("current_promotion_id"),
             f"{b}: current promotion differs")
        need(snap["boards"][b]["measurement_identity"] == [e.get("identity") for e in boards[b].get("environments") or []],
             f"{b}: measurement identity differs")
        lead = leaders[b]
        need(lead["board"] == b, f"{b}: leaderboard names {lead['board']!r}")
        need(lead["config_hash"] == boards[b]["config_hash"], f"{b}: leaderboard config hash differs")
        need(lead["configuration_hash"] == body["configuration_hash"], f"{b}: configuration hash differs")
        need(snap["board_references"][b] == lead["reference"], f"{b}: reference not the published reference")
        ref = lead["reference"]
        need(ref["promotion_id"] == boards[b]["current_promotion_id"],
             f"{b}: reference promotion is not the board's current promotion")
        need(metas[ref["submission"]]["source_sha256"] == ref["source_sha256"],
             f"{b}: reference hash is not submission {ref['submission']}'s declared source hash")

    # -- promotions ------------------------------------------------------------------------
    promotions = expected_promotions(reqs, leaders, metas)
    need(snap["promotions"] == promotions, "promotion resolution differs from a replay over the raw bodies")
    for b in BOARDS:
        ref = snap["board_references"][b]
        row = snap["promotions"][str(ref["promotion_id"])]
        need(row["status"] == "resolved" and row["resolved_submission"] == ref["submission"],
             f"{b}: promotion {ref['promotion_id']} is not resolved to submission {ref['submission']}")

    # -- entries and sources ---------------------------------------------------------------
    entries = expected_entries(root, reqs, leaders, metas, promotions)
    need({str(i): e for i, e in entries.items()} == snap["entries"],
         "entries differ from a replay over the raw bodies")
    for i, e in entries.items():
        if e["source_available_flag"] is False:
            need(e["status"] != "published", f"submission {i}: marked unavailable but kept as a reference")
        if e["status"] == "published":
            p = Path(root) / e["path"]
            need(p.is_file() and digest(p.read_bytes()) == e["declared_source_sha256"],
                 f"submission {i}: retained reference does not match the declared source hash")
        if e["status"] == "withheld":
            need(e["reason_code"] == "SOURCE_WITHHELD", f"submission {i}: withheld without a reason code")
            need(not (Path(root) / f"references/id{i}.c").exists(),
                 f"submission {i}: withheld yet a reference file exists")
        if e["status"] in ("withheld", "error"):
            need(e["path"].startswith("raw/"), f"submission {i}: failure body not kept raw")

    # -- scores ----------------------------------------------------------------------------
    scores = expected_scores(reqs, boards, leaders, metas, promotions, entries)
    need(snap["scores"] == scores, "scores differ from a replay over the raw bodies")
    check_semantics(snap, metas)
    check_no_absolute_fields(root, reqs)
    check_status(root, snap)
    check_result(root, snap)

    # -- local identities (informational: later waves may legitimately change these files) ---
    ws = snap["workspace"]
    for rel, meta in ws["files"].items():
        if meta is None:
            continue
        need(DIGEST.match(meta["sha256"]) is not None, f"workspace {rel}: malformed digest")
        p = REPO / rel
        if p.is_file() and digest(p.read_bytes()) != meta["sha256"]:
            print(f"note: {rel} has changed since the snapshot (recorded {meta['sha256'][:12]}…, "
                  f"now {digest(p.read_bytes())[:12]}…) — recorded hashes are a point-in-time identity")
    need(ws["former_50_local_baseline_matches_published_reference"] ==
         (ws["files"].get("eik-work/baselines/former-50/entry.c") is not None
          and entries[50]["status"] == "published"
          and ws["files"]["eik-work/baselines/former-50/entry.c"]["sha256"] == entries[50]["downloaded_sha256"]),
         "the former-50 cross-check contradicts the recorded hashes")
    return snap


# ---------------------------------------------------------------- negatives
TAMPERS = [
    ("flipped reference byte",
     lambda r: _flip(Path(r) / "references/id50.c")),
    ("edited ratio",
     lambda r: _patch(r, lambda s: s["scores"]["thumbv6m"]["ratio_records"][-1].__setitem__("ratio", 0.5))),
    ("withheld source promoted to published",
     lambda r: _patch(r, lambda s: s["entries"]["52"].update({"status": "published",
                                                             "path": "references/id52.c"}))),
    ("deleted raw body",
     lambda r: (Path(r) / "raw/submission-54.json").unlink()),
    ("absolute S invented",
     lambda r: _patch(r, lambda s: s["scores"]["rv32im"].__setitem__("published_absolute_S", 28.5))),
    ("promotion resolution altered",
     lambda r: _patch(r, lambda s: s["promotions"]["59"].__setitem__("resolved_submission", 53))),
    ("request status rewritten",
     lambda r: _patch(r, lambda s: s["requests"]["source-52"].__setitem__("http_status", 200))),
    ("extra file",
     lambda r: (Path(r) / "raw/extra.json").write_text("{}\n")),
    ("dropped board",
     lambda r: _patch(r, lambda s: s["boards"].pop("overall"))),
    ("status counts inflated",
     lambda r: _patch(r, lambda s: s["status"]["summary"].__setitem__("sources_published", 10))),
]


def _flip(p):
    """Change exactly one byte in the middle of a file, keeping its length."""
    b = bytearray(p.read_bytes())
    i = len(b) // 2
    b[i] ^= 0x01
    p.write_bytes(bytes(b))


def _patch(root, fn):
    p = Path(root) / SNAPSHOT
    snap = json.loads(p.read_text())
    fn(snap)
    snap["snapshot_sha256"] = canonical(snap)                 # a tamperer can re-seal the digest
    p.write_text(json.dumps(snap, indent=1, sort_keys=True) + "\n")


def self_test():
    ok = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "clean"
        shutil.copytree(HERE, base, ignore=shutil.ignore_patterns("__pycache__"))
        validate(base)
        ok += 1
        for name, tamper in TAMPERS:
            work = Path(tmp) / ("t%d" % ok)
            shutil.copytree(base, work)
            tamper(work)
            try:
                validate(work)
            except Fail:
                ok += 1
                continue
            except Exception as e:                            # structurally broken: also a rejection
                ok += 1
                print(f"note: the {name} tamper was rejected by {type(e).__name__}: {e}")
                continue
            raise Fail(f"self-test failed: a snapshot with a {name} was accepted")
        print(f"self-test: clean copy accepted, {len(TAMPERS)} tampered copies rejected")
    return ok


def main():
    snap = validate(HERE)
    self_test()
    refs = [i for i, e in snap["entries"].items() if e["status"] == "published"]
    print(f"snapshot {snap['snapshot_sha256']} taken {snap['snapshot_utc']}")
    print(f"  boards: " + ", ".join(f"{b}=submission {snap['board_references'][b]['submission']} "
                                    f"(promotion {snap['board_references'][b]['promotion_id']})"
                                    for b in BOARDS))
    print(f"  public references (hash-matched): {', '.join(refs) or 'none'}")
    withheld = [i for i, e in snap["entries"].items() if e["status"] == "withheld"]
    print(f"  withheld (documented, not bypassed): {', '.join(withheld) or 'none'}")
    for b in BOARDS:
        s = snap["scores"][b]
        c = s["champion_over_public_reference"]
        print(f"  {b}: champion over public reference "
              f"{c['S_champion_over_baseline']} (bar for a 3% win: {c['candidate_bar_over_baseline']})"
              if c["S_champion_over_baseline"] is not None else
              f"  {b}: champion over public reference unavailable — {c['open_reason']}")
    print("verify: pass")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fail as e:
        print(f"verify: FAIL: {e}")
        sys.exit(1)
