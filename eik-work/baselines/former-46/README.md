# Baseline packet: former champion id46

`entry.c` is a byte-identical copy of `eik-work/toolkit/sources/id46.c`
(sha256 `788bb4ef7d88df26ec558306b8c038ca141dfc66404aa1d7bba6bb50774ff4b7`, matches the manifest). It was not edited.
Measured with the pinned offline toolkit (`run.py`, case `former-46`, scratch work dir `test/scratch/eik-baseline`),
verifier `ebbf9d5c…`, measurement `2c8fd1f3…`, sandbox `none`, development mode.

## S per board (lower is better)

| seed | rv32im | thumbv6m | overall | thumbv7em (diagnostic only) |
|---|---|---|---|---|
| 180434352 | 30.047304173201553 | 45.71845463423567 | 37.06367915795186 | 45.388285551835686 |
| 2851275305 | 30.12469923100875 | 46.14166525286234 | 37.28275456240278 | 45.8212169952562 |

Image bytes: rv32im 19928, thumbv6m 20438, thumbv7em 21484. Stack bound (static check): rv32im 192, thumbv6m 580,
thumbv7em 488; measured stack 8 / 68 / 48. Target sample wrong outputs: 0 of 98304 words per target; quick host check 0
mismatches on 134217728 words per function. Per-function/class mean, median, p999, max are in `report.json`.

**Coverage is partial**: `--quick` host check (2^27 of 2^32 words per function, no UBSan/ASan). No fullcheck was run.
The scoring inputs, fresh hard pools (hardscan, 2^26 samples) and target samples were at full pinned size.
The `comparison` ratios printed by the evaluator are against the **local upstream incumbent placeholder**
(S ≈ 1.5e5), not against the current champion. The current champion sources (submissions 52/53/56) are
recorded in the manifest as HTTP 403, so there is no same-seed comparison with the current champion here.

## Techniques

- **Target selection**: there is no `#ifdef` on the target. A constant `RVB = (L'\0' - 1 < 0)` is 1 where wchar_t is
  signed (rv32im, x86-64 host) and 0 where it is unsigned (thumbv6m/v7em). Every target sees the same tokens and drops the
  other body as dead code. The only other directives are `#ifndef r_EIK_SEL` and `#ifdef r_EIK_STATS` (off).
- **RV32IM body (`r_`)**: uses 64-bit products (MULH/MULHU).
  - exp: k2 = floor(2y·512/ln2)|1, e^y = 2^(k2>>10)·2^((2j+1)/1024)·e^r with |r| < ln2/1024. It reads the
    `exp8_r` table (256×u32 + 256×u16, with the rounding offset 130 folded in), then a short polynomial in r.
  - exp on −4 < x ≤ −1/4: returns the output word directly from cubic cells (`te128_r`, 64 per binade, plus
    `te125_126_r`, `eq4s33_r`, `nsm13_r`). Tiny |x| uses series fast paths.
  - tanh: two one-sided compares on w<<1, then cubic "deficit" cells. `tdl_r[257]` covers 1/8 ≤ y < 2 and returns
    w − (V>>8). `ta_r[138]` covers y up to about 9.1. The series `tsr_r` handles y < 1/8, and large |x| saturates.
  - sigmoid: shares the tanh cells and adds its own (`sb64_r`, `sq_r`, `tq_r`). It has a series for |x| < 1/4, cells
    for 2 ≤ x < 17.33, saturation, and goes through exp's exact path for subnormal results (x ≤ −87).
- **Thumb body (`t_`, M0+ has no 32×32→64 multiply)**: uses 16-bit limb products. The ep cells `t_t_eps` (11648 B,
  quadratic/cubic) and the refit cubic cells `t_t_tw[128]` serve sigmoid/tanh, along with the banks
  `t_t_sm12`/`t_t_pdrow`/`t_t_crows`. exp uses `t_t_exp_lo[512]` with a 64-bit `exp_mid2` fallback.
- **Polynomial degree**: mostly cubic per cell, quadratic on some Thumb cells, and degree 2–3 series near 0.
- **Hard cases**: each fast value carries B guard bits. `r_FAST_r` accepts it unless the guard bits fall in a window
  around the midpoint that was found by exhaustive runs. Otherwise the call declines to an out-of-line cold tier
  (`r_cold_r`/`r_ex_cold_r`, codes 0–4) that computes higher-precision 64-bit products, plus a list of the inputs that
  tier rounds wrongly. The Thumb equivalents are `t_t_mid_pos`/`t_t_mid_neg`/`t_t_sigp_exact64`.
- **Tables** (read-only bytes, nm on a host object): `r_` body 13448 B, `t_` body 16614 B (see `report.json`).

## Proposed single-technique experiments

1. rv32im exp: replace `exp8_r` (1536 B) with a 128-entry 2^(j/256) table plus one more polynomial term. Measure the
   code-size factor against the exp typical-class mean.
2. thumbv6m: shrink `t_t_eps` (11648 B, the largest table) by deriving wide-class sigmoid from tanh cells
   (sigmoid(x) = (1 + tanh(x/2))/2), keeping the typical-class cells. Measure the size_factor drop against the extra
   instructions.

## Files

`check.*`, `evaluate-<seed>.*`, `fingerprint.*`: the runner's command, exit, elapsed time, digest records and the full
stdout/stderr. `packet.json`: assembled by `packet.py`. `report.json`: the extracted identities and measurements.
