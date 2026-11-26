# Frozen fallback delivery

The chosen entry slightly regresses against id50. It ties historical id50 on RV32IM and regresses on Thumbv6-M and overall on all three held-out seeds. No 3% gain against a current champion has been demonstrated. This is a completed fallback package with competition outcome **incomplete / undetermined**, not a winning entry.

The delivered [entry.c](entry.c) is an exact copy of [root entry.c](../../entry.c), SHA256 `593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b` (166,756 bytes). Root source was left unchanged. The manifest binds both copies.

## Held-out results

Lower is better; takeover requires candidate/current ≤ 0.970 on identical fresh inputs, followed by correctness checks. Historical id50 is a public former champion, not any current champion. The kit's local incumbent is also not a current champion. Neither comparison establishes a live takeover.

| Seed | Board | Candidate S | Historical id50 S | Candidate / id50 | Current S / ratio |
| ---: | --- | ---: | ---: | ---: | --- |
| 849230117 | rv32im | 28.335213294739 | 28.335213294739 | 1.000000000000 | null / null |
| 849230117 | thumbv6m | 40.152570920253 | 40.139825565919 | 1.000317523909 | null / null |
| 849230117 | overall | 33.730278109697 | 33.724924299751 | 1.000158749354 | null / null |
| 2715043869 | rv32im | 28.395531955152 | 28.395531955152 | 1.000000000000 | null / null |
| 2715043869 | thumbv6m | 40.299877643125 | 40.286226411649 | 1.000338856048 | null / null |
| 2715043869 | overall | 33.828042559452 | 33.822312597226 | 1.000169413674 | null / null |
| 396172055 | rv32im | 28.381597262180 | 28.381597262180 | 1.000000000000 | null / null |
| 396172055 | thumbv6m | 40.333895135348 | 40.319962289478 | 1.000345557016 | null / null |
| 396172055 | overall | 33.834011996015 | 33.828167720500 | 1.000172763585 | null / null |

Exact values, raw-report citations, input hashes and explicit null fields are in [scores.json](scores.json) and [scores.csv](scores.csv). Thumbv7E-M is diagnostic only and is included in JSON. No board takeover is verified; which boards this entry would actually take remains undetermined.

## Packaging board refresh

Anonymous public GETs were made once at packaging; see [snapshot](public-refresh/snapshot.json) and its ten hash-bound request/response records. The references remain rv32im submission 52 / promotion 59, thumbv6m submission 53 / promotion 60, and overall submission 56 / promotion 61. None changed from the landed [board snapshot](../final-validation/boards/snapshot.json); no affected comparison is stale. Sources still return HTTP 403 SOURCE_WITHHELD and absolute current S is unpublished. Current S, candidate/current ratio and 0.970 predicate remain null for every board/seed, eligibility undetermined. Historical promotion ratios published by the service are not multiplied into a claimed same-input champion score.

## Correctness evidence and limits

The selected [merged coverage](../final-validation/merged/coverage-matrix.json) contains 12 complete runtime/function cells, each [0,4096) with 2^32 inputs and zero mismatches. Pinned eik merge exited 0 with verdict passed. Nine target cells bind the actual checker ELF. Host records report GCC ASan+UBSan. This is the retained reports' coverage result, not a claim of exhaustive success for every aspect of the competition or source portability. See [CHECKS.md](CHECKS.md) for selected runs, exclusions and missing provenance.

The [independent source review](../final-validation/review/review.md) supplies the rounding derivation and explains evidence discrepancies. The one-line Thumb tanh guard change is certified by an integer enclosure and target checks, but the host and Thumb compilation arms differ through the inherited wide-character selector. The review flags strict C11 subobject-offset/struct-view concerns. Novelty was checked against five public sources only; private-source duplicate status is unknown.

The committed evaluator runtime export is incomplete: three pinned payloads are missing. Historical fresh checks used exact restored bytes in scratch. Offline verification of the delivered evidence is available now; a new cold evaluator replay from committed files alone is not. No success is inferred from failed preparation, quick samples or evaluator timeouts.

## Review map

- [Manifest](manifest.json): complete repository-local log/source/tool inventory, SHA256 and size; files remain at their original repository paths.
- [Result](result.json): machine-readable identities, commands/exits, measured facts, explicit claims and gaps.
- [Experiment log](experiment-log.md) and [complete reviewed ledger](experiments.json): all eight trials, controls, two extra variants, regressions and unscored attempts.
- [Change note](change-note.md), [provenance](PROVENANCE.md), [offline replay](REPLAY.md) and [next steps](next-steps.md).

Run `python3 eik-work/delivery/verify.py` from the repository root. It uses Python's standard library, reads only local files, validates all inventory hashes, recomputes raw-score arithmetic and coverage, checks claims/nulls, and reruns the seven landed offline evidence verifiers. It does not rescore or rerun 2^32 inputs.
