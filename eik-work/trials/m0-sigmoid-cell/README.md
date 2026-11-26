# Thumb sigmoid negative cells

One paired experiment against unchanged former submission 50. See [the exact patch](id50.diff), [the candidate](entry.c), and [the control packet](../paired-control/packet.json).

| Source | SHA-256 |
|---|---|
| id50 | `88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3` |
| Candidate | `f8c2ac2d2752bfec1febb2d6d0789d2b7776fe64bc551e668965d58732d0de90` |

## Integer equivalence

The changed caller is the direct negative sigmoid branch entered when the sign bit and bit 30 of the input word are both set and `w < 0xc05b0000`. Its words are `0xc0000000…0xc05affff`. Write `w = 0xc0000000 + (i << 16) + f`, with `0 <= i <= 90` and `0 <= f <= 65535`. The base indexes `t_eps[475 + ((int32_t)(w - 0xc05b0000) >> 16)]` with the pinned builds' arithmetic signed right shift. The shifted difference is `i - 91` for every `f`, including both endpoints, so the original row is `384 + i`. The candidate uses `(w >> 16) & 127u == i`.

Each new row copies the full `q`, `v` and `p` and stores `(uint16_t)p` and `(uint8_t)q` in narrow fields. [The trace script](inspect-cells.py) checks all 91 rows and verifies that the shared table fields are intact. Multiplication by the unsigned 32-bit `f` promotes the narrow coefficients to the same unsigned type used in id50. Every product, sum and subtraction retains its modulo-2³² behavior. The three logical shifts by 15 remain at the same points. The resulting `t_Y` is identical bit for bit across the entire changed interval.

Both implementations apply the original fast-return predicates and reconstruct the same output from the same intermediate. The low bits that select midpoint refinement are identical, including the negative-`t_m6` branch and the special `0x3d708b74` return. The dispatch into the old packed `t_ev13` path, the refinement path `t_rjn`, the positive bank, and the original shared table including `t_aux` are intact. Just outside the changed interval, `0xbfffffff` and `0xc05b0000` take their original source paths. The compiled traces include those two values, both in-bank endpoints, and the midpoint-refinement witnesses `0xc0000021` and `0xc05a0037`.

## Code generation

The [retired instruction traces](thumb-trace.txt) show the baseline loading the three full words with one `ldm`, then extracting the narrow coefficients with `uxth` and `uxtb`. The candidate drops those two coefficient extractions and emits `ldrh` at offset 12 and `ldrb` at offset 14, three individual full-word loads, and an additional literal load in that block. The input fraction still uses `uxth`. For `0xc0123456`, the compiled Thumb sigmoid call grows from 38 to 47 instructions. The two refinement witnesses grow from 115 to 123 and from 120 to 128. Out-of-bank trace changes show that the inlined sigmoid's register allocation and branch layout also moved. The RV32IM linked `.text` and `.rodata` addresses and hashes match id50.

The 16-byte cell adds 1,456 bytes of table. The total Thumbv6-M image grows by 1,584 bytes. Thumbv7E-M grows by 1,636 bytes. The size term charges the extra image bytes for all three functions through the board score. Keep id50 for this trial. A follow-up would need to retain the compact multi-register load or reuse space after auditing every consumer of the shared rows.

## Offline checks

The pinned source, verifier, harness and full reference digests are ordinary files in this checkout. The data oracle for the selected chunks is [sigmoid.digest](../../toolkit/kit/reference/sigmoid.digest), SHA-256 `a62545e4b3067576aa72b26eca71d60f20f8db9774f58fadb45dd0c5a4d69e95`. Each chunk contains 2²⁰ input words, generated from its index by the kit harness. The selected range `3071:3079` covers `0xbff00000…0xc06fffff`, including every changed input and both adjacent branches. The pinned offline runtime assets are declared in [dependencies.json](../../toolkit/dependencies.json). Provision the scratch cache once on a connected machine with `python3 eik-work/toolkit/provision.py --fetch`. With that cache staged, these commands run offline and rebuild the exact scored target object with the kit.

```sh
t=eik-work/toolkit/run.py
w=test/scratch/replay-m0-sigmoid
src=eik-work/trials/m0-sigmoid-cell/entry.c
python3 "$t" "$w" verify-thumb targetcheck-negative targetcheck "$src" --function sigmoid --target thumbv6m --chunks 3071:3079 --jobs 2
python3 "$t" "$w" verify-thumb targetcheck-negative-m4 targetcheck "$src" --function sigmoid --target thumbv7em --chunks 3071:3079 --jobs 2
python3 "$t" "$w" verify-thumb hostcheck-negative fullcheck "$src" --function sigmoid --chunks 3071:3079 --seed 1874435642
```

The compiled target checks and table trace supplement the two quick sanitizer evaluations. The selected chunk checks cover the changed domain. No exhaustive all-function or all-target qualification is claimed.

## Scoring and incumbent availability

The standard kit setup ran in a separate scratch case. Both requested `evaluate --quick --json --seed` commands ran in a fresh isolated case with empty local board state. This avoids measuring the unrelated built-in exact-c incumbent. Evaluator code, input generation, sample populations and scorer settings are unchanged. Compare the resulting absolute S against the landed id50 control on the matching seeds and input digests. Any board-takeover labels in the isolated evaluator report are artifacts of empty local state.

The [public board snapshot](public-board-snapshot.json) identifies the live references as submissions 52 (RV32IM), 53 (Thumbv6-M), and 56 (overall). Their source endpoints returned HTTP 403 with `SOURCE_WITHHELD`. Same-seed absolute S and candidate/current-champion ratios are unavailable for those references. No board takeover is established. The paired comparison uses id50 throughout.

## Experiment results

Lower S is better. The ratio is candidate / id50 on the exact same inputs. Thumbv7E-M is reported by the kit for diagnosis.

| Seed | Board or diagnostic target | id50 S | Candidate S | Ratio |
|---|---|---:|---:|---:|
| 1874435642 | rv32im | 28.522714242 | 28.522714242 | 1.000000000 |
| 1874435642 | thumbv6m | 40.515260593 | 42.187309581 | 1.041269610 |
| 1874435642 | overall | 33.994193627 | 34.688565491 | 1.020426190 |
| 1874435642 | thumbv7em | 39.956338503 | 41.133724138 | 1.029466805 |
| 1947282751 | rv32im | 28.517414314 | 28.517414314 | 1.000000000 |
| 1947282751 | thumbv6m | 40.303038974 | 41.979862805 | 1.041605394 |
| 1947282751 | overall | 33.901894645 | 34.599958677 | 1.020590709 |
| 1947282751 | thumbv7em | 39.749544203 | 40.919461778 | 1.029432226 |

No ratio meets 0.970× against id50. The source passed the gate with a different normalized hash. RV32IM's scored code and data are unchanged. Both Thumb targets emit changed code and regress.

These are retired instruction means. Each cell gives id50 → candidate. The weights and populations are the kit defaults, with 2,000 typical, 1,000 wide, 300 hard and 1,000 uniform inputs per function. RV32IM means match the control.

| Seed | Target | Function | Typical | Wide | Hard | Uniform | Hard p99.9 |
|---|---|---|---:|---:|---:|---:|---:|
| 1874435642 | thumbv6m | sigmoid | 37.908 → 42.148 | 29.537 → 32.057 | 48.503 → 50.820 | 18.579 → 21.120 | 178 → 180 |
| 1874435642 | thumbv6m | tanh | 37.149 → 37.149 | 20.731 → 20.731 | 75.933 → 75.933 | 14.698 → 14.698 | 117 → 117 |
| 1874435642 | thumbv6m | exp | 42.928 → 42.928 | 34.367 → 34.367 | 56.893 → 56.893 | 19.860 → 19.860 | 146 → 146 |
| 1874435642 | thumbv7em | sigmoid | 37.824 → 40.473 | 29.983 → 31.559 | 49.230 → 49.957 | 20.233 → 22.382 | 164 → 169 |
| 1874435642 | thumbv7em | tanh | 35.997 → 35.997 | 21.468 → 21.468 | 72.413 → 72.413 | 16.627 → 16.627 | 113 → 113 |
| 1874435642 | thumbv7em | exp | 39.776 → 39.776 | 32.861 → 32.861 | 53.597 → 53.597 | 21.085 → 21.085 | 136 → 136 |
| 1947282751 | thumbv6m | sigmoid | 37.440 → 41.690 | 29.272 → 31.784 | 46.580 → 48.797 | 18.766 → 21.342 | 187 → 190 |
| 1947282751 | thumbv6m | tanh | 36.761 → 36.761 | 21.070 → 21.070 | 74.360 → 74.360 | 14.364 → 14.364 | 117 → 117 |
| 1947282751 | thumbv6m | exp | 42.685 → 42.685 | 34.309 → 34.309 | 59.447 → 59.447 | 20.147 → 20.147 | 153 → 153 |
| 1947282751 | thumbv7em | sigmoid | 37.216 → 39.864 | 29.959 → 31.457 | 47.220 → 47.960 | 20.470 → 22.629 | 171 → 176 |
| 1947282751 | thumbv7em | tanh | 35.666 → 35.666 | 21.741 → 21.741 | 71.190 → 71.190 | 16.293 → 16.293 | 113 → 113 |
| 1947282751 | thumbv7em | exp | 39.545 → 39.545 | 32.760 → 32.760 | 56.110 → 56.110 | 21.387 → 21.387 | 151 → 151 |

The hard tail multiplier is 1.0 for every function, target and seed in both sources.

| Target | Image bytes | Size term | Static stack bound (bytes) | Peak stack (bytes), seed 1874435642 | Peak stack (bytes), seed 1947282751 |
|---|---:|---:|---:|---:|---:|
| rv32im | 18960 → 18960 | 1.135476394 → 1.135476394 | 176 → 176 | 0 → 0 | 8 → 8 |
| thumbv6m | 20500 → 22084 | 1.145777106 → 1.156276393 | 312 → 336 | 60 → 68 | 60 → 68 |
| thumbv7em | 21254 → 22890 | 1.150786819 → 1.161582404 | 280 → 296 | 40 → 48 | 40 → 48 |

| Correctness check | Coverage | Mismatches |
|---|---|---:|
| Scored outputs | 12,900 words per target and seed | 0 |
| Stratified target sample | 98,304 words per target and seed | 0 |
| Quick UBSan/ASan | 134,217,728 words per function and seed | 0 |
| Offline Thumbv6-M sigmoid targetcheck | 8,388,608 words | 0 |
| Offline Thumbv7E-M sigmoid targetcheck | 8,388,608 words | 0 |
| UBSan/ASan sigmoid on the same selected chunks | 8,388,608 words | 0 |

[packet.json](packet.json) indexes the raw command records, outputs and input hashes. The public current-champion S and same-seed ratios are null for both seeds on all boards.
