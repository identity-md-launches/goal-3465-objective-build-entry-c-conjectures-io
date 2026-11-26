# Held-out seed 2715043869

| Board | Candidate S | Former 50 S | Candidate / 50 | ≤ 0.970 vs 50 | Current submission | Current S | Candidate / current | Eligibility |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| rv32im | 28.395531955 | 28.395531955 | 1.000000000 | no | 52 | — | — | undetermined |
| thumbv6m | 40.299877643 | 40.286226412 | 1.000338856 | no | 53 | — | — | undetermined |
| overall | 33.828042559 | 33.822312597 | 1.000169414 | no | 56 | — | — | undetermined |
| thumbv7em | 39.762614187 | 39.750796606 | 1.000297292 | — | — | — | — | reported only |

The overall score uses the RV32IM and Thumbv6-M measurements from the same source.
Explicit kit comparisons corroborated the former-50 ratios on all three boards.
Each current source returned HTTP 403 SOURCE_WITHHELD in the board snapshot.
A current-board ratio at or below 0.970 would still require exhaustive correctness.
Each independent measurement scored 4,300 words and checked 32,768 stratified words per function on every target.
The three quick host sanitizer checks covered 134,217,728 words per function.
All scored words, target samples and quick host checks had zero wrong outputs.

The initial quick evaluate command exited 124 at its ten-minute whole-command limit.
It had generated the fresh pools and was cut off before producing a report or host checker.
The paired scores come from the unchanged measure stage with all target samples.
Separate quick fullcheck stages supplied the host sample evidence.

A preview replay also completed. The system startup module shadowed its watchdog, so its command ledger records an attempted cap and the effective cap is null.

The first comparison-scoped attempt exited -9 after 602.866 seconds wall time. It hit the 600-second comparison timer while profiling was also active in worker processes. Its separate measure and quick fullcheck stages reproduced the paired evidence.

The coordinator-only watchdog run completed in 287.730 seconds. The local incumbent comparison took 261.777 seconds under its 600-second phase cap. The repeat reproduced the paired scores and clean quick checks.

Full-precision scores and eligibility are in `scores.json`. The command ledger and raw reports are in `raw/`.
The offline bootstrap used the exact toolkit dependency pins. The fetch command restored payloads omitted from the reduced runtime export.
