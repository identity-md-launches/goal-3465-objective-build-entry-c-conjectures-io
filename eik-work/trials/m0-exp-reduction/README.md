# Thumbv6-M exp row 10 reduction

Keep id50 as the freeze candidate for this experiment. In both trials the specialization regressed Thumbv6-M, and RV32IM was byte-identical in the executable text section. The normalized candidate source differs from id50 and the Thumb code changed. This is a measured regression.

- id50 SHA-256 `88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3`
- Candidate SHA-256 `c33bec89f7767b513aeaa81a54fd1945b3cba077d57d55b9733adad4c9424c88`
- Candidate normalized SHA-256 `3e4f5ac106825a160e3680290b31dd567d0c2045ed927e65a42c2cb8cd9a4951`
- The one source change is in [id50.diff](id50.diff).

## Integer equivalence and rounding

The normal Thumb exp dispatcher computes `t_s = ((int32_t)t_w >> 23) + 138`. Row 10 corresponds to signed high bits −128 and input words `c0000000..c07fffff`, or negative inputs of magnitude [2, 4). This row covered 572 and 618 of the two 2,000-word typical exp sets, respectively.

The original negative-row reduction for row 10 uses `C = 2^32 - 2955`, `M = 2^32 - 2^19`, `K = 1317922824`, and `B = 3476905865`.

1. `C * (w >> 9) + B` and `B - 2955 * (w >> 9)` agree modulo 2³². The same logical right shift by 15 produces the exact same unsigned reduced index.
2. `K * index + M * w` and `K * index - (w << 19)` agree modulo 2³². This is the entire 32-bit residual, including the bits later consumed by midpoint resolution.
3. `B & 31 = 9` and `(0u - B) & 31 = 23`. Both paths rotate the same index by the same counts and carry the same table pointer, `&t_eps[0].t_aux`.

Every new operation is on unsigned 32-bit quantities with shifts less than 32. The identities hold for any word passed into row 10, including both endpoints. The branch jumps to the existing `t_xn` reconstruction with the same `t_P0`, `t_kb` and `t_tb`. Its estimate, guard test, fast return, `t_exp_res` midpoint resolution and `t_exp_tail` handling therefore have the same integer inputs and decisions as id50. The generic reduction still handles all other rows and the alternate entries at `t_xa` and `t_xb`.

| Input word | Row | Index before rotate | Rotated index | Residual | Thumbv6-M output |
| --- | --- | --- | --- | --- | --- |
| `bfffffff` | 9 | — | — | — | `3e0a9556` |
| `c0000000` | 10 | `0000f63a` | `1d00007b` | `291e41d0` | `3e0a9555` |
| `c07fffff` | 10 | `0000f075` | `3a800078` | `f06a8ba8` | `3c960ab0` |
| `c0800000` | 11 | — | — | — | `3c960aae` |

The six affected near-midpoint words found by the fresh hard scans had the same compiled Thumbv6-M result in both entries. For example, `c0382e72` was 4.598e-8 ulp from a midpoint and produced `3d666d27`. The QEMU digest check covers these words as well as the endpoints and all other words in the row.

## Emitted instructions

[audit-target.json](audit-target.json) contains the retired instructions for `c0000000` from both pinned Thumbv6-M guest images, the executable text hashes for all targets, and the same-input binade split. The baseline enters the row at `0x2486c` and loads the five fields with one `ldm`. The candidate pays a `cmp` and branch, loads separate literals for C, B and K, materializes rotate count 9 in a register, shifts the word by 19, and branches to the shared reconstruction. Replacing the original residual multiply did not make up for the extra loads and control flow. The word retires 47 instructions versus 41, with six extra instructions on every affected scored exp word in both seeds. The average on all other typical exp words rises by 1.69 and 1.70 instructions, respectively.

A future reconstruction experiment could compute the table byte offset `(index & 511u) << 4` and exponent contribution `(index >> 9) << 23` directly for reductions with rotate count 9. It could defer rotation until the slow paths need it.

## Scoring and correctness

All scores below are absolute S. Thumbv7E-M is reported by the kit for comparison.

Both `evaluate --quick --json` runs completed and agreed with the standalone `measure` runs. The evaluator compared against the kit's local `examples/incumbent.c` and cleared its threshold on all three local boards. The tables below compare to id50 on the same inputs.

| Seed | Board or target | id50 S | Candidate S | Candidate/id50 |
| --- | --- | ---: | ---: | ---: |
| 1874435642 | rv32im | 28.522714242 | 28.522714242 | 1.000000000 |
| 1874435642 | thumbv6m | 40.515260593 | 41.117853670 | 1.014873237 |
| 1874435642 | overall | 33.994193627 | 34.246062409 | 1.007409171 |
| 1874435642 | thumbv7em | 39.956338503 | 40.549185465 | 1.014837370 |
| 1947282751 | rv32im | 28.517414314 | 28.517414314 | 1.000000000 |
| 1947282751 | thumbv6m | 40.303038974 | 40.919484267 | 1.015295256 |
| 1947282751 | overall | 33.901894645 | 34.160179835 | 1.007618606 |
| 1947282751 | thumbv7em | 39.749544203 | 40.360758211 | 1.015376629 |

Thumbv6-M regressed by 1.49% and 1.53%. No board reached 0.970× of id50.
The live board endpoint reports promotions 59/60/61 and omits absolute S.
Those promotions map to submissions 52/53/56 in the pinned manifest. All three source requests returned HTTP 403, so the same-input live champion scores, ratios and takeover decisions are null. [Live comparison](live-comparison.json), [board response](live-boards.json)

| Seed | Target | exp typical | exp wide | exp hard | exp uniform | exp hard p99.9 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1874435642 | rv32im | 30.564 → 30.564 | 24.738 → 24.738 | 41.487 → 41.487 | 13.297 → 13.297 | 80 → 80 |
| 1874435642 | thumbv6m | 42.928 → 45.849 | 34.367 → 34.989 | 56.893 → 57.530 | 19.860 → 20.157 | 146 → 146 |
| 1874435642 | thumbv7em | 39.776 → 42.697 | 32.861 → 33.225 | 53.597 → 54.030 | 21.085 → 21.135 | 136 → 136 |
| 1947282751 | rv32im | 30.327 → 30.327 | 24.847 → 24.847 | 43.090 → 43.090 | 13.322 → 13.322 | 90 → 90 |
| 1947282751 | thumbv6m | 42.685 → 45.714 | 34.309 → 34.911 | 59.447 → 60.100 | 20.147 → 20.427 | 153 → 153 |
| 1947282751 | thumbv7em | 39.545 → 42.574 | 32.760 → 33.119 | 56.110 → 56.580 | 21.387 → 21.442 | 151 → 151 |

Hard tail factors were 1.0 for every function and target. The full class means, tail, measured peak stack, input digests, source hashes and paired ratios for both seeds are indexed in [packet.json](packet.json) and in the [control packet](../paired-control/packet.json).

| Target | Code and table bytes | Static stack bound (bytes) |
| --- | ---: | ---: |
| rv32im | 18960 → 18960 | 176 → 176 |
| thumbv6m | 20500 → 20548 | 312 → 312 |
| thumbv7em | 21254 → 21310 | 280 → 280 |

Each scoring run used 2,000 typical, 1,000 wide, 300 hard and 1,000 uniform inputs per function on each target. Every scored output matched. Each of the six seed/target combinations also passed the 98,304-word stratified sample with zero mismatches.

Measured peak stack matched id50. RV32IM used 0 and 8 bytes on the two seeds, Thumbv6-M used 60 bytes, and Thumbv7E-M used 40 bytes. The largest scored instruction count across both seeds and all functions was 187.

The host UBSan and ASan checks and all nine QEMU targetchecks covered 4,294,967,296 words per function with zero mismatches. The host selects id50's RV implementation through the existing selector. The QEMU checks exercise both compiled Thumb implementations, including the specialized branch. [Merged coverage report](exhaustive-merge.stdout)

## Local reproduction

The pinned suite runs offline once `provision.py --fetch` has staged its verified dependencies under scratch. `python3 eik-work/toolkit/verify.py bootstrap --offline` passed on Linux x86-64 with Python 3.12 and GCC. To replay targetcheck, use the candidate source and the tracked kit harness, build inputs, and `reference/exp.digest`. The runner rebuilds the image and executes it in QEMU. To reproduce the trace and class split, first run both measure stages under the work directory and case in the packet. [Bootstrap log](bootstrap.stdout)

```sh
d=eik-work/trials/m0-exp-reduction
w=test/scratch/m0-exp-reduction
python3 eik-work/toolkit/run.py "$w" replay thumb-exp targetcheck "$d/entry.c" \
  --function exp --target thumbv6m --chunks 3071:3081 --jobs 2
PYTHONDONTWRITEBYTECODE=1 "$w/runtime/bin/python" "$d/audit-target.py" "$w"
python3 eik-work/trials/paired-control/verify.py "$d"
```

The chunk range is half-open. Chunks 3072–3079 cover all 8,388,608 affected words, and chunks 3071 and 3080 cover the contiguous neighbors. Targetcheck matched all 10,485,760 words against the pinned exp digests.
