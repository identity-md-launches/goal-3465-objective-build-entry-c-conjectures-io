# Former champion id50

`entry.c` is the exact source pinned for submission 50 in the toolkit manifest. This packet measures a historical baseline. The evaluator compares it against its local incumbent. A current-champion ratio and board takeover verdict are unavailable from these runs.

## Local scores

| Seed | RV32IM | Thumb v6-M | Overall | Thumb v7E-M (diagnostic) |
|---:|---:|---:|---:|---:|
| 180434352 | 28.501406296161065 | 40.4306405096557 | 33.94598815736148 | 39.85817679176508 |
| 2851275305 | 28.623918516972903 | 40.575572089958854 | 34.0797868139245 | 40.03987958031529 |

| Target | Code bytes | Read-only data bytes | Score-counted bytes | Static stack bound (bytes) |
|---|---:|---:|---:|---:|
| rv32im | 5484 | 13476 | 18960 | 176 |
| thumbv6m | 4636 | 15760 | 20500 | 312 |
| thumbv7em | 5390 | 15760 | 21254 | 280 |

Read-only data bytes include coefficient tables, constants and padding. The Thumb object totals also include 104 bytes of unwind index data.

Both runs used 4,300 scoring inputs per function and 32,768 stratified sample inputs per function on each target. Each host quick check covered 134,217,728 words per function. All mismatch counts were zero.

## Source techniques

- **Selection.** `EIK_SEL` defaults to `(L'\0' - 1 < 0)`. This tests wide-character signedness at compile time and selects the `_r` paths on the host and RV32IM and the `t_` paths on both Thumb targets. The preprocessed entry tokens are identical. The host quick sanitizer run exercises the host-selected path, and the target samples exercise the paths compiled for their respective targets.
- **RV32IM exp.** `ex8_r` holds 256 high words, 256 low halfwords and 15 reduction constants. A fixed-point multiply by a reciprocal estimates the base-two exponent and the subinterval on the ln(2)/256 grid. The residual is formed by subtraction with an extra low-part correction on wider inputs. The main table reconstruction uses a degree-two residual correction. `ext_r` overlays word and halfword coefficient views and supplies direct binary32-indexed cells for parts of the negative domain, including cubic Horner cells and a four-multiply region that mixes the input word and local offset. Tiny positive inputs return 1 or a linear correction, and tiny negative inputs also use a quadratic correction. Overflow, underflow, subnormals and NaN payloads have explicit paths.
- **RV32IM tanh and sigmoid.** Exponent and high mantissa bits index the cubic Horner rows in `tl_r`, `tld_r` and `ta_r`. Smaller banks include `kr_r`, `sx_r`, `sq_r` and `tsr_r`. For small arguments, tanh can return the original word or evaluate an odd correction through degree five. Small sigmoid inputs return ½, use a linear correction, or use an odd polynomial through degree five. Larger inputs use sign-specific saturation thresholds and exp-based tails.
- **Thumb kernels.** The exp, tanh and sigmoid paths share the interleaved 16-byte rows of `t_eps`. The exp paths use a 9-bit reduction index, a split fixed-point ln(2)/512 reduction and a quadratic residual approximation. `t_exp_lo[512]` supplies low bits for refinement. The small exp bank and several tanh and sigmoid banks use cubic cells indexed by binary32 bit fields. The fast residual reconstruction in functions such as `t_exp_den` multiplies selected high and low pieces with 32-bit products. The shared bank is supplemented by `t_srow`, `t_crows`, `t_xrow` and small parameter tables. Tiny-input, saturation and special-value branches work directly on the input word.
- **Hard cases.** Guard-bit tests on the fast fixed-point results decide when an output can be rounded immediately. Close cases use extra table bits and higher-order residuals (for example `ex_res_r` and `t_exp_res`), or dedicated midpoint tests (for example `th_core_r` for the small odd-series path). Some branches reconstruct results via exp or perform an integer division. The exp subnormal paths separately track the bits used for rounding across the normal/subnormal boundary.

## Two single-technique experiments for a later candidate

1. **RV32IM exp loads.** In the positive-domain reduction path, replace byte-offset loads of `ex8_r.row[0]`, `[1]` and `[4]` with direct named constants or typed access. Keep the coefficients and arithmetic unchanged. Inspect the emitted instructions for constant materialization and load changes, then measure RV32IM exp typical and wide means and the size term on fresh seeds.
2. **Thumb exp table layout.** Move only the 512 hot exp reconstruction high words into a contiguous 32-bit bank, replacing their original storage wherever those fields serve exp. Keep the residual polynomial, index calculation and low-halfword refinement intact. Inspect net object bytes and the addressing sequence, then measure Thumb exp typical, wide and hard means on fresh seeds.

Coverage is partial. See `report.json` and the raw evaluator logs for the actual scoring inputs, target samples, host sample and mismatch counts. Neither full-domain host checking nor exhaustive target checking is part of this baseline packet.
