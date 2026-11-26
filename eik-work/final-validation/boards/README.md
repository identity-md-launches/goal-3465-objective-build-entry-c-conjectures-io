# Dated public board snapshot — conjectures.io exact-integer-kernels

One snapshot of the public competition state, taken by unauthenticated GET, for the goal's final
comparisons. It answers, from the API's own bytes: which submission holds each board, which
promotion that is, what source hash the API declares for it, whether that source is published or
withheld, and which published numbers describe it. `snapshot.json` is the record; the raw bodies
under `raw/` and `references/` are the evidence; `verify.py` re-derives every claim from those bytes
offline.

## What was fetched

| endpoint | request key |
| --- | --- |
| `GET /v1/competitions/exact-integer-kernels/boards` | `boards` |
| `GET /v1/competitions/exact-integer-kernels/leaderboard?board=rv32im\|thumbv6m\|overall` | `leaderboard-<board>` |
| `GET /v1/competitions/exact-integer-kernels/submissions/<id>` | `submission-<id>` |
| `GET /v1/competitions/exact-integer-kernels/submissions/<id>/source` | `source-<id>` |

`<id>` covers every submission named by a board reference or a leaderboard challenger, plus the five
submissions the goal's baselines were taken from (37, 42, 46, 48, 50). No credentials, no
registration, no authentication and no attempt to work around a withholding.

The 2026-11-26 snapshot (see `snapshot.json` for the exact UTC instant and hashes) found: rv32im held
by submission 52 (promotion 59), thumbv6m by 53 (promotion 60), overall by 56 (promotion 61) — all
three sources answered `403 SOURCE_WITHHELD`, as the rules say a current champion's source is never
published. Submissions 37, 42, 46, 48 and 50 are published; each was kept only because its bytes hash
to the `source_sha256` the API declares for it.

## Promotion → submission resolution

Resolved from evidence, never assumed:

* a leaderboard reference names `(promotion_id, submission, source_sha256)` together;
* every evaluation names `reference_promotion_id` and the `reference_hash` it was scored against;
* a promotion resolves to a submission only when every hash attributed to it is one submission's
  declared source hash, and the leaderboard's stated submission agrees.

A promotion whose hash matches no submission (a launch champion, or an entry this snapshot did not
ask about) is recorded `unresolved` with the hashes and provenance that say so. It is never guessed.

## Published absolute S vs takeover ratios

The API publishes no absolute S per call for any board or submission: `published_absolute_S` is
`null` everywhere and `verify.py` fails if anything else appears, or if a raw body carries an
absolute per-call score field. What is published is an S **ratio** per evaluation — the candidate's S
over the reference champion's S at that moment (`decision.score`, and the API's own wording "S ratio
1.0125 > 0.97"). Those ratios are not comparable across the season: each is relative to whoever held
the board then.

Two things are therefore kept apart in `scores.<board>`:

* `ratio_records` — every published takeover ratio, each with its own reference promotion and hash,
  flagged `measured_against_current_champion` only when that reference is the promotion holding the
  board now;
* `champion_over_public_reference` — a **derived** product of those published ratios, walked from the
  champion back to the first promotion that resolves to a retained public reference. It is labelled
  derived and carries a caveat: the validator measured it on its own inputs, while local comparisons
  run on local seeds.

Where the walk cannot close, the value is `null` and `open_reason` says why. At the 2026-11-26
snapshot: rv32im is open (the champion took the board from promotion 53, which resolves to no
submission), while thumbv6m closes at submission 50 through promotion 57 and overall closes at
submission 50 through promotion 58. Those two are the only honest public statements about how far
today's champion sits above the last public reference, and they imply that a candidate must reach
roughly `0.97 x 0.9684 ≈ 0.9394` of that reference on thumbv6m, and `≈0.9391` on overall, to take the
board — not `0.97`. Re-measure locally; do not treat the product as a score.

## Refreshing

```sh
python3 eik-work/final-validation/boards/fetch_snapshot.py   # network, anonymous GETs
python3 eik-work/final-validation/boards/verify.py           # offline, standard library only
```

`fetch_snapshot.py` replaces `raw/`, `references/`, `snapshot.json` and `result.json`; it retains a
downloaded source only on a declared-hash match. `verify.py` never touches the network.

## What verify.py checks

* `snapshot_sha256` is the canonical digest of the snapshot that carries it;
* the declared file ledger equals the `raw/` and `references/` directories exactly, byte counts and
  hashes included — a missing, extra or edited file fails;
* the request ledger is anonymous (no credential header of any kind), https and API-only, UTC-stamped
  with offsets, body hashes matching the saved bytes, and exactly the URLs the scope implies;
* boards and leaderboards agree on board set, configuration hash, current promotion and reference
  hash; each reference hash is the referenced submission's own declared hash;
* promotions, entries, source classifications and score records all match a replay over the raw
  bodies;
* every retained reference hashes to its declared source hash, every withheld source carries its raw
  403 body with `SOURCE_WITHHELD`, and no reference file exists for a withheld submission;
* the status counts, the gaps, and `result.json`'s hashes, commands and measured facts match the
  evidence;
* ten tampered copies (edited ratio, withheld source promoted to published, flipped reference byte,
  deleted body, invented absolute S, altered promotion resolution, rewritten status, extra file,
  dropped board, inflated counts) are each rejected.

## Local identities

`snapshot.json` records the hashes of the root `entry.c` and of
`eik-work/baselines/former-50/entry.c` at snapshot time, and whether that local baseline is
byte-identical to submission 50's published source (it is). Only repository-relative paths are
recorded; nothing about this machine, its user or its accounts is in the evidence. Those hashes are a
point-in-time identity, so a later change to `entry.c` prints a note rather than failing the check.

## Gaps

* No current champion's source is public, so the 0.970x bar cannot be computed from public data: it
  has to be measured locally against a locally built incumbent on the same inputs.
* No absolute S is published for any board, so every score comparison that can be made from the API
  is a ratio, and only against the reference in force when it was taken.
* `ratio_records` cover only the submissions this snapshot fetched; older promotions that resolve to
  no fetched submission are marked unresolved rather than omitted.
