# Trial `shared-small-sigmoid`: affine small-|x| sigmoid fast path before id50's selector

**Outcome: eligible but a negative trial.** The candidate is correct everywhere it was checked. It is not a
duplicate: its normalised source differs from id50's. It regresses S on both boards on both seeds, so it
takes no board.

- Candidate `entry.c` SHA-256 `1593022e89963ac5abe3dcc4808470099be554e04094f9e1c72cd7094bbaf262`,
  normalised `666165f9b81aeb43c191257587d78cf6ad3da6e7ca78af387e977e8eab0d0775`.
- Base id50 (`eik-work/baselines/former-50/entry.c`) SHA-256 `88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3`,
  normalised `e8722042f89400f887e0e526338d22ae756c029c4646c49c4d290da1bda04db8`.
- Exact diff: [`id50.diff`](id50.diff). It adds one 17-entry `static const uint16_t` table and 14 lines at the top of `eik_sigmoid`.
  id50's `EIK_SEL` selector, `eik_sigmoid_r`, `t_eik_sigmoid`, tanh and exp are unchanged. There are no target or compiler probes.
- Evaluator: pinned verifier `ebbf9d5c…`, measurement `2c8fd1f3…` (same as the control). Linux x86-64, Python 3.12.3, gcc 13.3.0.
  Stage form (`measure` + quick `fullcheck`), exactly like the control. `eik evaluate` re-measures the local ~10^5-instruction
  incumbent and does not fit this run's time budget. The per-entry numbers are the same either way.

## S per board (lower is better)

| seed | board | id50 (control) | candidate | candidate / id50 |
|---|---|---|---|---|
| 1874435642 | rv32im | 28.52271424241966 | 30.74556592260963 | 1.0779 |
| 1874435642 | thumbv6m | 40.515260593492414 | 45.47604248247939 | 1.1224 |
| 1874435642 | overall | 33.99419362722625 | 37.39233426846292 | 1.1000 |
| 1874435642 | thumbv7em (reported only) | 39.95633850332885 | 40.876179395484385 | 1.0230 |
| 1947282751 | rv32im | 28.517414314250885 | 30.820392303525246 | 1.0808 |
| 1947282751 | thumbv6m | 40.30303897386101 | 45.34592865165533 | 1.1251 |
| 1947282751 | overall | 33.90189464529962 | 37.38421204748982 | 1.1027 |
| 1947282751 | thumbv7em (reported only) | 39.74954420309734 | 40.704955283999155 | 1.0240 |

The candidate would take no board, since it needs ≤ 0.970. tanh and exp class means are identical to id50 on every target.
All sigmoid class means rise: see [`evidence/class-means.md`](evidence/class-means.md). On rv32im, typical +4.0, wide +7.6..8.1,
hard +17.7..18.4, uniform +3.3..3.4, hard p99.9 111→115. On thumbv6m, typical +12.7, wide +14.7..15.2, hard +25.0..25.4,
uniform +9.6..9.7, hard p99.9 178→192 / 187→202. The tail factor stays 1.0 everywhere.

Image bytes / measured stack / static stack bound:

| target | id50 | candidate |
|---|---|---|
| rv32im | 18960 / 0–8 / 176 | 19132 / 0–8 / 176 |
| thumbv6m | 20500 / 60 / 312 | 20704 / 76 / 328 |
| thumbv7em | 21254 / 40 / 280 | 21374 / 40 / 280 |

## Correctness counts

- `check` PASS and `gate` accepted (stage null).
- `measure`, both seeds, every target: 0 wrong scored outputs, 98304 sample words with 0 mismatches.
- Quick host check (`fullcheck --quick --seed`), both seeds × 3 functions: 134217728 words each, 0 mismatches.
- **Full host check, every input, UBSan+ASan:** sigmoid, tanh and exp, 4294967296 words each, 0 mismatches, `complete: true`.
  See [`evidence/hostfull/`](evidence/hostfull) and the raw run.py logs in [`evidence/runlogs/full-host-*`](evidence/runlogs).
- **Target check (object code in QEMU)** of sigmoid on 12 affected 1M-word chunks × rv32im, thumbv6m and thumbv7em: 36 shards, all
  `passed`, 0 mismatches. See [`evidence/targetcheck/`](evidence/targetcheck) and `evidence/runlogs/tc-*`. These are not full
  target coverage; no merge verdict over all 4096 chunks was produced. The chunks are:
  - 0: +0, subnormals, the tiny 0.5 path;
  - 823 and 824: e8 102→103, the boundary of the 0.5 return and of the affine path, x > 0;
  - 952 and 959: e8 = 119, where the bound is largest and the fallback rate highest;
  - 960: x = 2^-7, first word outside the fast region;
  - 2048, 2871, 2872, 3000, 3007 and 3008: the same chunks for x < 0.

Command shapes (run from the repository root, w = test/scratch/eik):
`python3 eik-work/toolkit/run.py $w full-host-<fn> shard fullcheck eik-work/trials/shared-small-sigmoid/entry.c --function <fn> --chunks 0:4096 --threads 8 --out …`
and `python3 eik-work/toolkit/run.py $w tc-<target>-<c> shard targetcheck eik-work/trials/shared-small-sigmoid/entry.c --function sigmoid --target <target> --chunks <c>:<c+1> --jobs 1 --out …`.
The packet's own runs and their exact commands are in `packet.json` → `runs`.

## The change and why every fast return is correctly rounded

Let `t = w << 1`, `e = t >> 24` (biased exponent) and `n = w >> 31`. The block runs only when `t < 0x78000000`, that is |x| < 2^-7.
This includes ±0 and subnormals; NaN and Inf never enter it.

1. **e < 103 (|x| < 2^-24): return 0x3F000000 (0.5).**
   - For x > 0, σ(x) − ½ < x/4 < 2^-26, less than half of ulp(½) = 2^-24.
   - For x < 0, ½ − σ(x) < |x|/4 < 2^-26, which is exactly half of the ulp 2^-25 just below ½.
   - So the nearest float is ½. σ(x) is irrational for rational x ≠ 0, so ties never occur.
2. **103 ≤ e ≤ 119.** σ(x) = ½ + ½·tanh(x/2). The tanh series is alternating, with decreasing terms for |x/2| ≪ π/2, so
   σ(x) = ½ + x/4 − δ·sign(x) with 0 < δ < |x|³/48.
   - **x > 0:** the result lies in [½, 1), whose ulp is 2^-24. The float is 0x3F000000 + round(a − d), with a = x·2^22 and d = δ·2^24.
   - **x < 0:** the result lies in [¼, ½], whose ulp is 2^-25. The float is 0x3F000000 − round(a − d), with a = |x|·2^23 and d = δ·2^25.
     A result of 0 gives ½ correctly, because the midpoint between pred(½) and ½ is ½ − 2^-26.
   - In both cases round(a − d) = floor(z − d) with z = a + ½, and floor(z − d) = floor(z) whenever frac(z) > d.
3. **Integer form.** The code computes `Z = (((w<<8)|2^31) >> (121 − e − n)) + 2^14`.
   - The shift is 1..18 and Z < 2^31 + 2^14.
   - Z = floor(a·2^15) + 2^14, so `Z>>15` = floor(z) exactly and `F = Z & 0x7FFF` ≤ the true frac(z)·2^15.
   - It fast-returns 0x3F000000 ± (Z>>15) only if F > TH[e]. TH[e] = floor(2^(3e−338)/48) is the x < 0 bound of d·2^15, using
     |x| < 2^(e−126). It is also an upper bound for x > 0, which is half as large. Then F ≥ TH+1 > d·2^15, so frac(z) > d.
   - The values for e = 115..119 are {2, 21, 170, 1365, 10922}; for e ≤ 114 the value is 0, so only F = 0 falls back.
4. **Everything else falls through to id50's unchanged selector and kernels.** This covers F ≤ TH, the ambiguous near-midpoint
   or affine-exact-midpoint words, and every word outside the region.

Exhaustive fallback counts per sign and exponent are in [`evidence/fallback-counts.txt`](evidence/fallback-counts.txt).
256–512 of 2^23 words per binade fall back for e ≤ 114. At e = 119, the binade just below 2^-7, about 33% fall back.

## Emitted instructions of the touched path ([`evidence/disasm/`](evidence/disasm))

- **rv32im:** id50's `eik_sigmoid` starts directly with `bltz a0`. The candidate adds `slli, srli, addi, bltu` (4 instructions)
  in front of every call.
  - Tiny inputs return after about 6 more instructions.
  - The full fast body is about 22 instructions plus the test. That is longer than id50's own rv32 affine path for
    0x33FFF000..0x3A689000, which takes about 14.
  - The gain is limited to 8.9e-4..2^-7, where id50 uses its polynomial.
- **thumbv6m:** id50 starts `push; add r7; lsls; bmi`. The candidate starts with `push {r4–r7,lr}; sub sp,#12; str r0,[sp,#8]`,
  then a 4–6 instruction range test, and reloads `w` from the stack later.
  - The extra register pressure adds a spill frame on every call. The measured stack goes 60→76 and the bound 312→328.
  - This is why typical rises by about 12.7 instructions, not by the cost of the test alone.

## Experiment log (seed 1874435642, `measure` only; raw logs in `evidence/experiments/`)

| # | source | change | rv32im S (ratio) | thumbv6m S (ratio) | overall ratio |
|---|---|---|---|---|---|
| 0 | id50 (control) | none | 28.5227 (1) | 40.5153 (1) | 1 |
| 1 | **this entry.c** | \|x\|<2^-7, 0.5 for e<103, table bound up to e=119 | 30.7456 (1.0779) | 45.4760 (1.1224) | 1.1000 |
| 2 | v2 | single range test for e∈[90,114], bound F≠0, no table or 0.5 branch | 31.108 (1.0907) | 43.639 (1.0771) | 1.0839 |
| 3 | v3 | as v2 with e∈[103,114] | 30.912 (1.0838) | 43.404 (1.0713) | 1.0775 |

The second seed (1947282751) was measured for #1 only: rv32im 1.0808, thumbv6m 1.1251.

v2 and v3 avoid the v6m spill, but still pay about 6 rv32 and about 8 v6m instructions per call for the test, and are slower in their
region than id50's existing paths. **Conclusion:** a pre-selector small-|x| test cannot pay off for id50. The region is only a large
share of the *wide* and *uniform* classes, and id50's rv32 path already handles most of it with an affine shortcut.

What to try next:
- Put the affine shortcut *inside* `t_eik_sigmoid` after its existing exponent test, so the test costs nothing extra. This needs
  per-path code, which falls outside this trial's "target-independent pre-selector" scope.
- Reuse the Q15 bound to extend id50's rv32 affine path from 8.9e-4 up to 2^-9 or 2^-8 in place of the polynomial.
