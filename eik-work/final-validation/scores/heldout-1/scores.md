# Held-out paired score comparison, seed 849230117

- inputs_sha256 `30c46675a8f6b6fd8238b30b25bde12fe102e8f9648acd6463be79f4cc104aca`; measurement identity `2c8fd1f3a6711f0639685319fb25262b02bfecf4c6589c52cb58928270a46322`; verifier identity `ebbf9d5cac596a718532b34798dc452e4050d6940594005c44f9a729c699c5a8`
- candidate: `entry.c` sha256 `593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b`; id50: `eik-work/baselines/former-50/entry.c` sha256 `88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3`
- full populations per function: typical 2000, wide 1000, hard 300, uniform 1000; fresh hard pools (sigmoid 569, tanh 172, exp 453); target sample 98304 words per target, 0 wrong
- status: **incomplete**. No current-board reference source is public, so no current S, ratio or eligibility exists.

## Candidate vs former champion 50 (historical comparison, not a current board)

| board | candidate S | id50 S | ratio | <= 0.970 |
|---|---|---|---|---|
| rv32im | 28.335213294739 | 28.335213294739 | 1.000000000000 | no |
| thumbv6m | 40.152570920253 | 40.139825565919 | 1.000317523909 | no |
| overall | 33.730278109697 | 33.724924299751 | 1.000158749354 | no |

The overall denominator is sqrt(rv32im S x thumbv6m S) of id50 itself. thumbv7em (reported only): candidate 39.677310386989, id50 39.668638833110.

## Candidate vs current board references

| board | current champion | reference bytes | current S | ratio | eligibility |
|---|---|---|---|---|---|
| rv32im | submission 52 (`12614bf3cd9c`) | none (SOURCE_WITHHELD) | null | null | undetermined |
| thumbv6m | submission 53 (`6662dc198cf2`) | none (SOURCE_WITHHELD) | null | null | undetermined |
| overall | submission 56 (`1deb2fad47d3`) | none (SOURCE_WITHHELD) | null | null | undetermined |

## Per-class mean instructions per call (typical / wide / hard / uniform), code bytes, hard p99.9

| entry | target | function | typical | wide | hard | uniform | hard p99.9 | bytes |
|---|---|---|---|---|---|---|---|---|
| candidate | rv32im | sigmoid | 29.0825 | 20.0900 | 29.5167 | 11.8790 | 111 | 18960 |
| candidate | rv32im | tanh | 25.7495 | 14.2160 | 51.2633 | 8.9350 | 92 | 18960 |
| candidate | rv32im | exp | 30.6560 | 24.6150 | 42.4967 | 13.6380 | 90 | 18960 |
| candidate | thumbv6m | sigmoid | 38.0515 | 28.4490 | 44.3900 | 18.1090 | 187 | 20508 |
| candidate | thumbv6m | tanh | 36.9665 | 20.4120 | 73.2733 | 14.4490 | 117 | 20508 |
| candidate | thumbv6m | exp | 43.0685 | 34.1560 | 58.5100 | 20.3550 | 154 | 20508 |
| candidate | thumbv7em | sigmoid | 37.9950 | 29.1370 | 45.2133 | 19.8640 | 171 | 21254 |
| candidate | thumbv7em | tanh | 35.8780 | 21.2040 | 70.2967 | 16.3190 | 113 | 21254 |
| candidate | thumbv7em | exp | 39.9100 | 32.6610 | 55.1800 | 21.5160 | 151 | 21254 |
| id50 | rv32im | sigmoid | 29.0825 | 20.0900 | 29.5167 | 11.8790 | 111 | 18960 |
| id50 | rv32im | tanh | 25.7495 | 14.2160 | 51.2633 | 8.9350 | 92 | 18960 |
| id50 | rv32im | exp | 30.6560 | 24.6150 | 42.4967 | 13.6380 | 90 | 18960 |
| id50 | thumbv6m | sigmoid | 38.0515 | 28.4490 | 44.3900 | 18.1090 | 187 | 20500 |
| id50 | thumbv6m | tanh | 36.9615 | 20.3660 | 73.2433 | 14.4430 | 117 | 20500 |
| id50 | thumbv6m | exp | 43.0685 | 34.1560 | 58.5100 | 20.3550 | 154 | 20500 |
| id50 | thumbv7em | sigmoid | 37.9950 | 29.1370 | 45.2133 | 19.8640 | 171 | 21254 |
| id50 | thumbv7em | tanh | 35.8730 | 21.1700 | 70.2367 | 16.3150 | 113 | 21254 |
| id50 | thumbv7em | exp | 39.9100 | 32.6610 | 55.1800 | 21.5160 | 151 | 21254 |

## eik evaluate --quick --json (opponent: the kit's local incumbent, not a board champion)

| entry | status | seconds | timed out | quick host check (3 functions x 134217728 words) |
|---|---|---|---|---|
| candidate | would-take-over-after-full-check | 167.8 | no (cap 600 s) | 0 wrong, complete=false |
| id50 | would-take-over-after-full-check | 168.2 | no (cap 600 s) | 0 wrong, complete=false |

The evaluate status only says the entry is far below the kit's ~140k-instruction incumbent; the incumbent state was left as setup made it. It is not a takeover of any live board.
