# Paired measurements

Lower S is better. All ratios use former submission 50 with the same
scoring inputs, seed and evaluator. Thumbv7-M is diagnostic only.

| Seed | Board | id50 S | Trial S | Trial / id50 |
| --- | --- | ---: | ---: | ---: |
| 1874435642 | rv32im | 28.522714242 | 28.522714242 | 1.000000000 |
| 1874435642 | thumbv6m | 40.515260593 | 40.530568943 | 1.000377842 |
| 1874435642 | overall | 33.994193627 | 34.000615230 | 1.000188903 |
| 1874435642 | thumbv7em | 39.956338503 | 39.969717549 | 1.000334842 |
| 1947282751 | rv32im | 28.517414314 | 28.517414314 | 1.000000000 |
| 1947282751 | thumbv6m | 40.303038974 | 40.316224057 | 1.000327149 |
| 1947282751 | overall | 33.901894645 | 33.907439671 | 1.000163561 |
| 1947282751 | thumbv7em | 39.749544203 | 39.759604645 | 1.000253096 |

Thumbv6-M S rises by 0.0378% and 0.0327%. RV32IM is flat. The
experiment clears the static gate and changes the normalised source
and actual Thumb instructions. Its results support retaining id50
for this comparison. Live board scores are unavailable. For a follow-on
experiment, target a family that appears more often in scored inputs
and inspect whether the guard can reuse existing condition flags.

## Tanh retired instructions

| Seed | Target | Typical mean | Wide mean | Hard mean | Uniform mean | Hard p99.9 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1874435642 | rv32im | 25.8045 → 25.8045 | 14.4990 → 14.4990 | 51.6867 → 51.6867 | 9.2000 → 9.2000 | 92 → 92 |
| 1874435642 | thumbv6m | 37.1490 → 37.1520 | 20.7310 → 20.7880 | 75.9333 → 76.0133 | 14.6980 → 14.7040 | 117 → 117 |
| 1874435642 | thumbv7em | 35.9970 → 36.0000 | 21.4680 → 21.5200 | 72.4133 → 72.5733 | 16.6270 → 16.6310 | 113 → 113 |
| 1947282751 | rv32im | 25.7205 → 25.7205 | 14.7650 → 14.7650 | 52.7300 → 52.7300 | 8.9860 → 8.9860 | 92 → 92 |
| 1947282751 | thumbv6m | 36.7610 → 36.7635 | 21.0700 → 21.1210 | 74.3600 → 74.4033 | 14.3640 → 14.3700 | 117 → 117 |
| 1947282751 | thumbv7em | 35.6660 → 35.6690 | 21.7410 → 21.7830 | 71.1900 → 71.2767 | 16.2930 → 16.2970 | 113 → 113 |

All tanh hard-tail factors were 1.0 on both seeds. The Thumb guard
increased all four tanh class means on both Thumb targets and seeds.
Per-function counts, class means and tail factors are in the packet.
[Measurement packet](packet.json)

## Image, stack and coverage

| Target | id50 → trial image bytes | id50 → trial static stack bound | id50 → trial sampled peak stack (both seeds) |
| --- | ---: | ---: | ---: |
| rv32im | 18960 → 18960 | 176 → 176 | 0/8 → 0/8 |
| thumbv6m | 20500 → 20508 | 312 → 312 | 60/60 → 60/60 |
| thumbv7em | 21254 → 21254 | 280 → 280 | 40/40 → 40/40 |

Per seed and target, each function scored on all 4,300 words
with zero wrong outputs. The target samples checked 98,304 words per
target and seed with zero mismatches. Each quick host check covered
134,217,728 words per function under UBSan and ASan with zero mismatches.
Thumbv6-M and Thumbv7-M targetcheck each checked 16,777,216 tanh
words spanning the affected exponent for both signs, with zero
mismatches on each target.

The exhaustive UBSan/ASan host check and QEMU object-code checks on all
three targets each covered 4,294,967,296 words per function, with zero
mismatches. The pinned kit merged all 12 reports into one passing verdict.
[Exhaustive coverage report](exhaustive-merged.stdout)
