# Baseline packet: former champion id48

Source: `entry.c`, a byte-exact copy of `eik-work/toolkit/sources/id48.c`
(sha256 `c858c54e3e0b07b469d4445028a5ddd7c7ce579932bf42d4575cc3044ef61661`, 168695 bytes). I did not edit it.
Toolkit: the pinned offline runner (`verify.py bootstrap --offline` passed). The case was isolated in `test/scratch/eik-baseline/cases/former-48`.

## S (lower is better), `eik evaluate --quick --json`, full-size scoring inputs

| seed | rv32im | thumbv6m | overall | thumbv7em (diagnostic only) |
|---|---|---|---|---|
| 180434352 | 29.2792 | 43.2725 | 35.5947 | 42.2153 |
| 2851275305 | 29.3848 | 43.4302 | 35.7238 | 42.4128 |

- Wrong outputs: 0 on every target, in both scored inputs and the stratified target samples (98304 words per target).
- Host quick check: 0 mismatches on 2^27 words per function.
- **Coverage is PARTIAL.** These were quick runs, so the host check is incomplete (`complete:false`), and I ran no fullcheck or targetcheck shards.
- Code bytes: rv32im 20528, thumbv6m 20256, thumbv7em 21060. Stack bound: 192, 324 and 288 bytes.
- The comparison ratios printed in the logs are against the toolkit's local *incumbent* (template). They are **not** current-champion comparisons.

## Techniques
- **Per-target source split (target macro).** `EIK_SEL` defaults to `(L'\0' - 1 < 0)`, which tests whether wchar_t is signed. wchar_t is signed on x86-64 and RV32 and unsigned under ARM AAPCS. So the host and rv32im compile the `*_r` kernels, and thumbv6m/thumbv7em compile the `t_*` kernels. The tokens are identical on every target, and the selection is a constant folded by the compiler. Consequence: the host sanitizer checks only the `_r` path. The ARM path is covered only by target checks.
- **exp (`_r`).** Range reduction is k = round(x·256/ln2), computed with `mulhu` against Q-format constants plus a Cody-Waite-style two-part ln2/256 (`m*1488522235`, `0xE8E7C000`). The 2^(j/256) table is split into `uint32 hi[256]` and `uint16 lo[256]` (`ex8_r`). The polynomial on r is degree 3, in Q32 with `mulhs` chains. Negative and large binades use per-binade piecewise cubic Horner cells (`nx_all[181]`, `nq4_r[5x32]`). Fast paths handle tiny |x| (1+x, and 1-x+x² with one mulhu), under/overflow constants and NaN.
- **tanh/sigmoid (`_r`).** Piecewise **degree-3** Horner cells are indexed directly by the exponent and top mantissa bits: `tl_r` 132, `tld_r` 156, `ta_r` 138, `tb_r` 68, `tla_r` 35, `kr_r` 6 refinement rows, `sq_r` 5x33, `tsr_r`. Each cell keeps 8-9 guard bits. If the guard bits are not near a midpoint (`V&254`, `V&0x1FE`, `Z&255`), the code rounds immediately. Saturation fast paths cover 1, ±1, the small-x identity and x - x³/3.
- **Hard-case strategy.** Near-midpoint results fall to a cold path: either an odd-series rounding test (`th_core_r`, `th_sdecb_r`), a refinement row (`kr_r`), or an exact fallback through `eik_exp` and a 64-bit division (`ex_prec_r`, `ex_cold_r`, `sg_cold_r`).
- **ARM path (`t_*`).** This code looks machine-generated (labels and empty-statement padding). One shared 4-word-row table `t_eps[]` (11664 B) serves exp, tanh and sigmoid. Supporting tables are `t_exp_lo[512]` u16, `t_srow[56]`, `t_crows` and `small_exp_rows[25]` cubic rows. It uses the same scheme: a degree-3 cell, a guard-bit test, then rare exact corrections (`t_exp_small_fix`, `t_exp_tail`, `t_sig_nb`). Wide multiplies are written as uint64 products, because thumbv6m has no 32x32->64 instruction.
- **Table bytes** (host gcc estimate): 14476 B on the `_r` path and 15272 B on the `t_` path. Tables make up most of the code-size term.

## Two proposed single-technique experiments
1. **thumbv6m: replace the uint64 products in the hot `t_*` cell evaluation with 16x16 partial products truncated to the bits actually kept.** v6m has no long multiply, so each `(uint64)a*b>>32` expands to about 4 MULS plus adds and carries. The cell's guard-bit margin should tolerate dropping the low×low partial. Measure the thumbv6m typical/wide means. This is the largest board (S 43.3, against 29.3 for rv32im).
2. **rv32im: merge `ex8_r.hi`/`.lo` into a single 256-entry uint32 table (or 128 entries with a degree-4 polynomial), dropping the second load and the `(Th<<18)|(Tl<<2)` reassembly in `ex_core_r`.** Change only exp and measure the exp typical/wide geo-means and the size factor. Code bytes (about 20 KiB, size_factor ≈ 1.149 on v7em) are a direct S multiplier.
