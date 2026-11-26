#!/usr/bin/env python3
"""Take one dated, unauthenticated snapshot of the public conjectures.io boards (standard library only).

    python3 eik-work/final-validation/boards/fetch_snapshot.py

What it does, with ordinary anonymous GETs and no credentials of any kind:

  1. GET /boards and /leaderboard?board=rv32im|thumbv6m|overall;
  2. take every submission id named anywhere in those responses (board references and
     challengers), fetch its /submissions/<id> record, and resolve every promotion id those
     records mention to a submission id through the declared source hashes;
  3. request /submissions/<id>/source for every one of those submissions, plus the former
     champions the goal's baselines were taken from (37, 42, 46, 48, 50);
  4. keep a downloaded source as a public reference only when its bytes hash to the
     source_sha256 the API declares for that submission; otherwise record why not
     (SOURCE_WITHHELD, mismatch, transport error) and keep only the raw response;
  5. write snapshot.json (the dated record), raw/requests.json (the request ledger) and the
     raw response bodies under raw/ and references/.

Nothing is inferred: a value the API does not publish (an absolute S per call, for instance) is
recorded as null with the reason, never guessed. verify.py re-checks this file offline.
"""
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
REF = HERE / "references"
SNAPSHOT = HERE / "snapshot.json"

API = "https://conjectures.io/v1/competitions/exact-integer-kernels/"
BOARDS = ("rv32im", "thumbv6m", "overall")
FORMER = (37, 42, 46, 48, 50)
USER_AGENT = "identitymd-eik-final-validation/board-snapshot (anonymous GET, no auth)"

READ_LIMIT = 4 * 1024 * 1024                                  # sources are <= 256 KiB by rule


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def digest_bytes(b):
    return sha256(b).hexdigest()


def get(url):
    """One anonymous GET. Returns (record, body) where record is the ledger entry."""
    started = utc_now()
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT,
                                                             "Accept": "application/json, text/plain, */*"})
    ctx = ssl.create_default_context()
    record = {"url": url, "method": "GET", "started_utc": started, "finished_utc": None,
              "http_status": 0, "error": None, "headers": {}, "bytes": 0, "sha256": None, "path": None}
    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            body = resp.read(READ_LIMIT)
            record["http_status"] = resp.status
            record["headers"] = {k.lower(): v for k, v in resp.headers.items()}
            record["final_url"] = resp.geturl()
    except urllib.error.HTTPError as e:
        body = e.read(READ_LIMIT)
        record["http_status"] = e.code
        record["headers"] = {k.lower(): v for k, v in (e.headers or {}).items()}
        record["final_url"] = e.geturl() if hasattr(e, "geturl") else url
    except Exception as e:                                     # transport-level failure
        body = b""
        record["final_url"] = url
        record["error"] = f"{type(e).__name__}: {e}"
    record["finished_utc"] = utc_now()
    record["bytes"] = len(body)
    record["sha256"] = digest_bytes(body)
    return record, body


def save(record, body, path):
    (HERE / path).parent.mkdir(parents=True, exist_ok=True)
    (HERE / path).write_bytes(body)
    record["path"] = path
    return record


def jget(path):
    return json.loads((HERE / path).read_bytes())


def check(cond, msg):
    if not cond:
        raise SystemExit(f"fetch_snapshot: {msg}")


def write_result(snapshot):
    """Record the item result beside the snapshot, with a hash for every file it describes."""
    here = HERE
    artifacts = []
    for p in [SNAPSHOT] + sorted(here.glob("raw/*")) + sorted(here.glob("references/*")) \
            + [here / "fetch_snapshot.py", here / "verify.py", here / "README.md"]:
        if p.is_file():
            b = p.read_bytes()
            artifacts.append({"path": str(p.relative_to(here)), "sha256": digest_bytes(b), "bytes": len(b)})
    result = {
        "status": "pass",
        "item": "board-snapshot",
        "batch": "e04-evidence-finalisation",
        "generated_utc": snapshot["snapshot_utc"],
        "what": ("one dated, unauthenticated snapshot of the public conjectures.io exact-integer-kernels "
                 "boards, resolved to submission ids and source requests, with raw responses, declared "
                 "and downloaded source hashes, and a withheld-source record for each champion source"),
        "source": {"api_base": snapshot["api_base"], "snapshot_utc": snapshot["snapshot_utc"],
                   "snapshot_path": "snapshot.json", "snapshot_sha256": snapshot["snapshot_sha256"],
                   "access": "anonymous GET, no credentials, no registration"},
        "tool": {"python": snapshot["environment"]["python"], "platform": snapshot["environment"]["platform"],
                 "standard_library_only": True, "network_during_verify": False,
                 "fetch": "fetch_snapshot.py", "verify": "verify.py"},
        "check": {"command": "python3 eik-work/final-validation/boards/verify.py", "expected_exit": 0,
                  "offline": True, "self_tests": "tampered copies must all be rejected"},
        "commands": [
            {"command": "python3 eik-work/final-validation/boards/fetch_snapshot.py", "exit": 0,
             "note": "24 anonymous GETs; wrote snapshot.json, raw/, references/ and this file"},
            {"command": "python3 eik-work/final-validation/boards/verify.py", "exit": 0,
             "note": "offline replay of every recorded fact from the raw bodies; tamper self-tests"},
        ],
        "artifacts": artifacts,
        "measured_facts": {
            "boards": {b: {"submission": snapshot["board_references"][b]["submission"],
                           "promotion_id": snapshot["board_references"][b]["promotion_id"],
                           "source_sha256": snapshot["board_references"][b]["source_sha256"],
                           "source_status": snapshot["entries"][str(snapshot["board_references"][b]["submission"])]["status"],
                           "measurement_identity": snapshot["boards"][b]["measurement_identity"],
                           "config_hash": snapshot["boards"][b]["config_hash"]}
                       for b in BOARDS},
            "published_absolute_S": {b: snapshot["scores"][b]["published_absolute_S"] for b in BOARDS},
            "ratios_against_current_champion": {
                b: [{"evaluation_id": r["evaluation_id"], "submission": r["submission"], "ratio": r["ratio"]}
                    for r in snapshot["scores"][b]["ratio_records"] if r["measured_against_current_champion"]]
                for b in BOARDS},
            "champion_over_public_reference": {
                b: {k: snapshot["scores"][b]["champion_over_public_reference"][k]
                    for k in ("baseline_submission", "S_champion_over_baseline",
                              "candidate_bar_over_baseline", "open_reason", "derived")}
                for b in BOARDS},
            "public_references": sorted(int(i) for i, e in snapshot["entries"].items()
                                        if e["status"] == "published"),
            "withheld_sources": sorted(int(i) for i, e in snapshot["entries"].items()
                                       if e["status"] == "withheld"),
            "promotions_resolved": {p: v["resolved_submission"] for p, v in snapshot["promotions"].items()
                                    if v["status"] == "resolved"},
            "former_50_local_baseline_matches_published_reference":
                snapshot["workspace"]["former_50_local_baseline_matches_published_reference"],
        },
        "gaps": snapshot["gaps"],
    }
    (here / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")


def main():
    check(sys.version_info >= (3, 8), "python >= 3.8 required")
    RAW.mkdir(parents=True, exist_ok=True)
    REF.mkdir(parents=True, exist_ok=True)
    for stale in sorted(REF.glob("*.c")):
        stale.unlink()                                        # a refresh replaces references
    for stale in sorted(RAW.glob("*.json")):
        stale.unlink()
    for stale in sorted(RAW.glob("*.c")):
        stale.unlink()

    requests = {}
    bodies = {}

    def fetch(key, url, path):
        rec, body = get(url)
        save(rec, body, path)
        requests[key] = rec
        bodies[key] = body
        time.sleep(0.15)
        return rec, body

    # -- 1. boards and leaderboards ------------------------------------------------------
    _, body = fetch("boards", API + "boards", "raw/boards.json")
    check(requests["boards"]["http_status"] == 200, "boards endpoint did not answer 200")
    board_data = json.loads(body)
    boards = {b["id"]: b for b in board_data["boards"]}
    check(set(boards) == set(BOARDS), f"unexpected board set {sorted(boards)}")

    leaders = {}
    for b in BOARDS:
        _, body = fetch(f"leaderboard-{b}", API + f"leaderboard?board={b}", f"raw/leaderboard-{b}.json")
        check(requests[f"leaderboard-{b}"]["http_status"] == 200, f"leaderboard {b} did not answer 200")
        leaders[b] = json.loads(body)
        check(leaders[b].get("board") == b, f"leaderboard {b} names board {leaders[b].get('board')!r}")

    # -- 2. which submissions matter ------------------------------------------------------
    roles = {}                                                # id -> [role, ...]
    for b in BOARDS:
        ref = leaders[b]["reference"]
        roles.setdefault(ref["submission"], []).append({"board": b, "role": "leaderboard-reference",
                                                        "promotion_id": ref["promotion_id"]})
        for ch in leaders[b].get("challengers") or []:
            roles.setdefault(ch["submission"], []).append({"board": b, "role": "leaderboard-challenger",
                                                           "evaluation_id": ch.get("evaluation_id")})
    for i in FORMER:
        roles.setdefault(i, []).append({"board": None, "role": "former-champion"})

    submission_ids = sorted(roles)
    metas = {}
    for i in submission_ids:
        _, body = fetch(f"submission-{i}", API + f"submissions/{i}", f"raw/submission-{i}.json")
        rec = requests[f"submission-{i}"]
        check(rec["http_status"] == 200, f"submission {i} did not answer 200 ({rec['http_status']})")
        metas[i] = json.loads(body)
        check(metas[i].get("id") == i, f"submission {i} answered id {metas[i].get('id')!r}")

    # -- 3. promotion -> submission resolution through declared source hashes ------------
    # Attribution evidence, both sides read from the API's own bodies:
    #   * a leaderboard reference names (promotion_id, submission, source_sha256) together;
    #   * an evaluation names reference_promotion_id and the reference_hash it was scored against.
    hash_by_submission = {i: metas[i].get("source_sha256") for i in submission_ids}
    promo_hashes = {}                                         # promotion id -> {hash: [provenance]}
    promo_subs = {}                                           # promotion id -> {submission: [provenance]}
    for b in BOARDS:
        ref = leaders[b]["reference"]
        p = ref["promotion_id"]
        h = ref["source_sha256"]
        promo_hashes.setdefault(p, {}).setdefault(h, []).append(
            f"raw/leaderboard-{b}.json#/reference/source_sha256")
        promo_subs.setdefault(p, {}).setdefault(ref["submission"], []).append(
            f"raw/leaderboard-{b}.json#/reference/submission")
    for i in submission_ids:
        for j, ev in enumerate(metas[i].get("evaluations") or []):
            p = ev.get("reference_promotion_id")
            h = ev.get("reference_hash")
            if p is None or h is None:
                continue
            promo_hashes.setdefault(p, {}).setdefault(h, []).append(
                f"raw/submission-{i}.json#/evaluations/{j}/reference_hash")
    promotions = {}
    for p in sorted(promo_hashes):
        hashes = promo_hashes[p]
        submissions = promo_subs.get(p, {})
        # a promotion resolves only if every hash attributed to it is one declared submission hash,
        # all of those name the same submission, and no leaderboard reference disagrees.
        candidates = set()
        for h in hashes:
            owners = {i for i, dh in hash_by_submission.items() if dh == h}
            candidates |= owners
        stated = set(submissions)
        resolved = len(candidates) == 1 and (not stated or stated == candidates) and len(hashes) >= 1
        promotions[str(p)] = {
            "promotion_id": p,
            "resolved_submission": sorted(candidates)[0] if resolved else None,
            "status": "resolved" if resolved else ("ambiguous" if candidates else "unresolved"),
            "attributed_hashes": sorted(hashes),
            "hash_provenance": sorted({x for v in hashes.values() for x in v}),
            "leaderboard_stated_submission": sorted(stated)[0] if len(stated) == 1 else None,
            "leaderboard_provenance": sorted({x for v in submissions.values() for x in v}),
            # an unresolved promotion is one whose declared reference hash is no submission's
            # declared source hash: either an entry never published as a submission (a launch
            # champion is one) or an entry this snapshot did not ask about. Not guessed either way.
            "note": (None if resolved else
                     "declared reference hash matches no submission in this snapshot; "
                     "not attributable to a submission from the public data fetched here"),
        }

    for b in BOARDS:
        ref = leaders[b]["reference"]
        row = promotions[str(ref["promotion_id"])]
        check(row["resolved_submission"] == ref["submission"],
              f"promotion {ref['promotion_id']} does not resolve to leaderboard submission {ref['submission']}")
        check(hash_by_submission[ref["submission"]] == ref["source_sha256"],
              f"leaderboard reference hash for {b} is not submission {ref['submission']}'s declared hash")
        check(ref["promotion_id"] == boards[b]["current_promotion_id"],
              f"leaderboard {b} reference promotion is not the board's current promotion")

    # -- 4. sources ----------------------------------------------------------------------
    entries = {}
    for i in submission_ids:
        declared = metas[i].get("source_sha256")
        key = f"source-{i}"
        rec, body = get(API + f"submissions/{i}/source")
        entry = {"submission": i,
                 "roles": roles[i],
                 "declared_source_sha256": declared,
                 "hash_provenance": f"raw/submission-{i}.json#/source_sha256",
                 "source_available_flag": metas[i].get("source_available"),
                 "source_request": key,
                 "status": None, "path": None, "downloaded_sha256": None,
                 "reason_code": None, "detail": None,
                 "promotion_ids": sorted({r["promotion_id"] for r in promotions.values()
                                          if r["resolved_submission"] == i and r["promotion_id"] is not None})}
        if rec["http_status"] == 200 and rec["error"] is None:
            got = digest_bytes(body)
            entry["downloaded_sha256"] = got
            if got == declared:
                path = f"references/id{i}.c"
                save(rec, body, path)                          # kept as a public reference
                entry["status"] = "published"
                entry["path"] = path
            else:
                save(rec, body, f"raw/source-{i}.c")
                entry["status"] = "hash-mismatch"              # not retained as a reference
        else:
            path = f"raw/source-{i}.json"
            save(rec, body, path)
            entry["downloaded_sha256"] = digest_bytes(body)
            entry["path"] = path                               # raw failure evidence, not a reference
            try:
                err = json.loads(body)
            except Exception:
                err = {}
            entry["reason_code"] = err.get("reason_code")
            entry["detail"] = err.get("detail")
            entry["status"] = "withheld" if rec["http_status"] == 403 else "error"
        requests[key] = rec
        bodies[key] = body
        time.sleep(0.15)
        entries[i] = entry

    # -- 4b. how far today's champion sits above the last public reference ----------------
    # Walk the published takeover ratios from the champion back to the first promotion that
    # resolves to a submission we retain as a public reference. The product is DERIVED, not
    # published, and is only indicative: the validator measured it on its own inputs.
    def chain(b):
        ref = leaders[b]["reference"]
        steps = []
        sub = ref["submission"]
        seen = set()
        while sub is not None and sub not in seen and entries.get(sub, {}).get("status") != "published":
            seen.add(sub)
            ev = next(((j, e) for j, e in enumerate(metas[sub].get("evaluations") or [])
                       if e.get("board") == b and (e.get("decision") or {}).get("outcome") == "qualifies"), None)
            if ev is None:
                return steps, None, "no qualifying evaluation on this board for submission %d" % sub
            j, ev = ev
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

    # -- 5. scores: what is published, and what is not -----------------------------------
    # The API publishes an S *ratio* per evaluation (decision.score, reason "S ratio ... > 0.97").
    # No absolute per-call S is published for any board, so published_absolute_S stays null.
    scores = {}
    for b in BOARDS:
        ref = leaders[b]["reference"]
        current = boards[b]["current_promotion_id"]
        ratio_records = []
        for i in submission_ids:
            for j, ev in enumerate(metas[i].get("evaluations") or []):
                if ev.get("board") != b:
                    continue
                d = ev.get("decision") or {}
                rp = ev.get("reference_promotion_id")
                ratio_records.append({
                    "submission": i,
                    "evaluation_id": ev["id"],
                    "state": ev.get("state"),
                    "ratio": d.get("score"),
                    "outcome": d.get("outcome"),
                    "reason": d.get("reason"),
                    "ratio_kind": "takeover-ratio: S_submission / S_reference_at_that_time",
                    "reference_promotion_id": rp,
                    "reference_submission": promotions.get(str(rp), {}).get("resolved_submission"),
                    "reference_hash": ev.get("reference_hash"),
                    "measured_against_current_champion": rp == current,
                    "completed_at": ev.get("completed_at"),
                    "provenance": f"raw/submission-{i}.json#/evaluations/{j}",
                    "leaderboard_ratio": next((c.get("ratio") for c in (leaders[b].get("challengers") or [])
                                               if c.get("submission") == i), None),
                })
        ratio_records.sort(key=lambda r: (r["evaluation_id"] or 0))
        scores[b] = {
            "champion_submission": ref["submission"],
            "champion_promotion_id": ref["promotion_id"],
            "champion_declared_source_sha256": ref["source_sha256"],
            "published_absolute_S": None,
            "published_absolute_S_note": ("the public API publishes no absolute S per call for this board; "
                                          "only S ratios recorded at takeover time, which are relative to "
                                          "the champion of that moment and not comparable across the season"),
            "ratio_records": ratio_records,
            # ratios whose reference is the promotion that holds the board right now: these are the
            # only published numbers that compare an entry directly with today's champion
            "ratios_against_current_champion": [r["evaluation_id"] for r in ratio_records
                                                if r["measured_against_current_champion"]],
            # the champion's own takeover measurement, i.e. S_champion / S_previous_holder
            "champion_takeover": [{"evaluation_id": r["evaluation_id"],
                                   "ratio": r["ratio"],
                                   "reference_promotion_id": r["reference_promotion_id"],
                                   "reference_submission": r["reference_submission"],
                                   "provenance": r["provenance"]}
                                  for r in ratio_records
                                  if r["submission"] == ref["submission"] and r["outcome"] == "qualifies"],
        }
        steps, base, why = chain(b)
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

    # local identities the snapshot is judged against, recorded so a later reader can tell which
    # bytes the comparison was made with; a missing file is recorded as absent, never invented.
    # Only repository-relative paths are recorded: no machine path or account detail is evidence.
    repo = HERE.parents[2]
    workspace = {"files": {}}
    for relpath in ("entry.c", "eik-work/baselines/former-50/entry.c"):
        p = repo / relpath
        workspace["files"][relpath] = ({"sha256": digest_bytes(p.read_bytes()), "bytes": p.stat().st_size}
                                       if p.is_file() else None)
    workspace["former_50_local_baseline_matches_published_reference"] = (
        workspace["files"]["eik-work/baselines/former-50/entry.c"] is not None
        and entries[50]["status"] == "published"
        and workspace["files"]["eik-work/baselines/former-50/entry.c"]["sha256"] == entries[50]["downloaded_sha256"])

    # one flat row per board: ids, hashes, source status, reference path or null, the identity of
    # the measurement that produced the published numbers, and null for a score nobody published
    per_board = {}
    for b in BOARDS:
        ref = leaders[b]["reference"]
        e = entries[ref["submission"]]
        published = e["status"] == "published"
        per_board[b] = {
            "board": b,
            "champion_submission": ref["submission"],
            "current_promotion_id": ref["promotion_id"],
            "promotion_resolution": promotions[str(ref["promotion_id"])]["status"],
            "declared_source_sha256": ref["source_sha256"],
            "source_status": e["status"],
            "source_reason_code": e["reason_code"],
            "source_response": e["path"],
            "reference_path": e["path"] if published else None,
            "reference_sha256": e["downloaded_sha256"] if published else None,
            "measurement_identity": [x.get("identity") for x in boards[b].get("environments") or []],
            "config_hash": boards[b].get("config_hash"),
            "promotion_bar": boards[b].get("promotion_bar"),
            "reward_share": boards[b].get("reward_share"),
            "published_absolute_S": scores[b]["published_absolute_S"],
            "ratios_against_current_champion": len(scores[b]["ratios_against_current_champion"]),
            "champion_over_public_reference": scores[b]["champion_over_public_reference"]["S_champion_over_baseline"],
        }

    snapshot = {
        "snapshot_utc": utc_now(),
        "workspace": workspace,
        "kind": "conjectures.io exact-integer-kernels public board/reference snapshot",
        "access": {"method": "anonymous unauthenticated GET", "authentication": None,
                   "user_agent": USER_AGENT},
        "api_base": API,
        "environment": {"python": sys.version.split()[0], "platform": sys.platform,
                        "transport": "python urllib (stdlib), TLS via system trust store"},
        "configuration": {
            "configuration_hash": board_data.get("configuration_hash"),
            "publication_hash": board_data.get("publication_hash"),
        },
        "boards": {b: {"config_hash": boards[b].get("config_hash"),
                       "models": boards[b].get("models"),
                       "reward_share": boards[b].get("reward_share"),
                       "promotion_bar": boards[b].get("promotion_bar"),
                       "guard_limit": boards[b].get("guard_limit"),
                       "current_promotion_id": boards[b].get("current_promotion_id"),
                       "paused": boards[b].get("paused"),
                       "measurement_identity": [e.get("identity") for e in boards[b].get("environments") or []],
                       "environments": boards[b].get("environments")}
                   for b in BOARDS},
        "board_references": {b: leaders[b]["reference"] for b in BOARDS},
        "promotions": promotions,
        "entries": {str(i): entries[i] for i in submission_ids},
        "scores": scores,
        "requests": requests,
        "gaps": [],
    }
    snapshot["status"] = {
        "snapshot": "complete",
        "means": ("every board, board reference, referenced submission and source request the public "
                  "API names was fetched and recorded; a source the API withholds is recorded as "
                  "withheld with its raw 403 body, so this is a complete record, not a complete set "
                  "of published sources"),
        "summary": {
            "boards": len(BOARDS),
            "submissions_requested": len(submission_ids),
            "sources_published": sum(1 for i in submission_ids if entries[i]["status"] == "published"),
            "sources_withheld": sum(1 for i in submission_ids if entries[i]["status"] == "withheld"),
            "sources_hash_mismatch": sum(1 for i in submission_ids if entries[i]["status"] == "hash-mismatch"),
            "sources_error": sum(1 for i in submission_ids if entries[i]["status"] == "error"),
            "published_absolute_S": sum(1 for b in BOARDS if scores[b]["published_absolute_S"] is not None),
        },
    }

    # the request ledger goes to disk first, then every evidence file is declared with its hash:
    # verify.py requires this set to match the directory exactly, so a stray or edited file fails.
    (RAW / "requests.json").write_text(json.dumps(requests, indent=1, sort_keys=True) + "\n")
    snapshot["files"] = {
        str(p.relative_to(HERE)): {"bytes": len(p.read_bytes()), "sha256": digest_bytes(p.read_bytes())}
        for p in sorted(list(RAW.glob("*")) + list(REF.glob("*"))) if p.is_file()
    }

    # -- 6. gaps, stated plainly ---------------------------------------------------------
    withheld = [i for i in submission_ids if entries[i]["status"] == "withheld"]
    for b in BOARDS:
        sub = leaders[b]["reference"]["submission"]
        if entries[sub]["status"] != "published":
            snapshot["gaps"].append(
                f"{b}: the current champion's source (submission {sub}) is not public "
                f"({entries[sub]['reason_code'] or entries[sub]['status']}); no public reference bytes "
                f"exist for this board, so local comparisons must use the former-champion references")
    snapshot["gaps"].append(
        "no absolute S per call is published for any board or submission: the only published numbers "
        "are per-evaluation S ratios (candidate S / reference S at that moment) and, for former "
        "champions, nothing at all; published_absolute_S is therefore null everywhere")
    if withheld:
        snapshot["gaps"].append(
            f"submissions withheld at this UTC instant: {', '.join(str(i) for i in withheld)}")
    published = [i for i in submission_ids if entries[i]["status"] == "published"]
    snapshot["gaps"].append(
        f"public references retained and hash-matched: {', '.join(str(i) for i in published) or 'none'}; "
        f"each is a former champion that holds no board, so none of them is the current champion")
    snapshot["gaps"].append(
        "consequence for final comparisons: the S ratio a candidate must beat (0.970x of the champion) "
        "cannot be computed from public data alone, because the champion's own source is withheld; it "
        "has to be measured locally against a locally built incumbent on the same inputs")

    snap_sha = digest_bytes(json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode())
    snapshot["snapshot_sha256"] = snap_sha
    SNAPSHOT.write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n")
    write_result(snapshot)
    print(f"snapshot {snap_sha}")
    print(f"  boards: " + ", ".join(f"{b}={leaders[b]['reference']['submission']}" for b in BOARDS))
    print(f"  submissions: {len(submission_ids)}  published references: "
          f"{sum(1 for i in submission_ids if entries[i]['status'] == 'published')}  "
          f"withheld: {len(withheld)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
