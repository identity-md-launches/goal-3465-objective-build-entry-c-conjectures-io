# Freeze of root `entry.c` — e03 kernel trials

**Outcome:** the frozen root `entry.c` is trial `m0-tanh-refine`, byte for byte
(SHA-256 `593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b`, normalised
`adf3a5a8074ffcca8e58ea852f58143a20a00aa6a74df8f14c1b742fa21a03c8`). It is the best eligible single by the
selection rule. **It does not beat id50.** None of the eight trials gets below 1.0 on any board, so this entry
takes no board at 0.970 and would not take over. Machine-readable binding: [manifest.json](manifest.json).
To verify offline: `python3 eik-work/freeze/verify.py`.

## Selection rule

The control is id50 (`eik-work/trials/paired-control`), on paired seeds 1874435642 and 1947282751. Both
seeds use the same inputs digest, hard pools, verifier `ebbf9d5c…` and measurement `2c8fd1f3…` for every
packet. For each candidate, take the worse ratio over the two seeds on each board (rv32im, thumbv6m,
overall), then that candidate's best board. Lowest value wins, and ties go to the worse overall ratio.
A combination is built only when two eligible candidates gain (ratio < 1) on the same board. No board had
any gain, so I built no combination.

Eligibility means all of these hold:
- the packet passes the shared verifier;
- the status is measured;
- check and gate pass;
- the quick host check passes on both seeds;
- the normalised hash differs from the control, from the accepted former sources (37/42/46/48/50) and
  from every other candidate;
- at least one targetcheck run on the candidate's own object code passed.

## Ledger (all eight trial packets, cross-checked with the shared verifier)

S is absolute. Ratios are candidate/id50 on the same seed. Every value is recomputed from raw logs by
`eik-work/trials/paired-control/verify.py`. The cross-check outputs are in [crosscheck/](crosscheck/).
All nine packets, the control included, PASS.

Control id50 S: seed 1874435642: rv32im 28.522714, thumbv6m 40.515261, overall 33.994194. Seed 1947282751:
rv32im 28.517414, thumbv6m 40.303039, overall 33.901895.

| trial | seed | S rv32im | S thumbv6m | S overall | ratio rv32im | ratio thumbv6m | ratio overall |
|---|---|---|---|---|---|---|---|
| `m0-exp-layout` | 1874435642 | 28.522714 | 42.118337 | 34.660198 | 1.000000 | 1.039567 | 1.019592 |
| `m0-exp-layout` | 1947282751 | 28.517414 | 41.903767 | 34.568585 | 1.000000 | 1.039717 | 1.019665 |
| `m0-exp-reduction` | 1874435642 | 28.522714 | 41.117854 | 34.246062 | 1.000000 | 1.014873 | 1.007409 |
| `m0-exp-reduction` | 1947282751 | 28.517414 | 40.919484 | 34.160180 | 1.000000 | 1.015295 | 1.007619 |
| `m0-sigmoid-cell` | 1874435642 | 28.522714 | 42.187310 | 34.688565 | 1.000000 | 1.041270 | 1.020426 |
| `m0-sigmoid-cell` | 1947282751 | 28.517414 | 41.979863 | 34.599959 | 1.000000 | 1.041605 | 1.020591 |
| `m0-tanh-refine` | 1874435642 | 28.522714 | 40.530569 | 34.000615 | 1.000000 | 1.000378 | 1.000189 |
| `m0-tanh-refine` | 1947282751 | 28.517414 | 40.316224 | 33.907440 | 1.000000 | 1.000327 | 1.000164 |
| `rv-exp-interval` | 1874435642 | 32.896202 | 40.515261 | 36.507509 | 1.153334 | 1.000000 | 1.073934 |
| `rv-exp-interval` | 1947282751 | 32.836443 | 40.303039 | 36.378681 | 1.151452 | 1.000000 | 1.073057 |
| `rv-exp-loads` | 1874435642 | 28.995332 | 40.515261 | 34.274677 | 1.016570 | 1.000000 | 1.008251 |
| `rv-exp-loads` | 1947282751 | 28.993483 | 40.303039 | 34.183702 | 1.016694 | 1.000000 | 1.008312 |
| `rv-tanh-quadratic` | 1874435642 | 30.692301 | 40.515261 | 35.263389 | 1.076065 | 1.000000 | 1.037336 |
| `rv-tanh-quadratic` | 1947282751 | 30.738936 | 40.303039 | 35.197621 | 1.077901 | 1.000000 | 1.038220 |
| `shared-small-sigmoid` | 1874435642 | 30.745566 | 45.476042 | 37.392334 | 1.077933 | 1.122442 | 1.099962 |
| `shared-small-sigmoid` | 1947282751 | 30.820392 | 45.345929 | 37.384212 | 1.080757 | 1.125124 | 1.102717 |

### Per-candidate verdict (selection order)

| rank | trial | best board (worse seed) | worse overall | eligible | note |
|---|---|---|---|---|---|
| 1 | `m0-tanh-refine` | rv32im 1.000000 | 1.000189 | yes | **chosen**. Loss: Thumb guard overhead exceeds the saved refinements. Full host check on 2^32 inputs and full targetcheck for all 3 targets × 3 functions |
| 2 | `m0-exp-reduction` | rv32im 1.000000 | 1.007619 | yes | loss: Thumb +1.5% |
| 3 | `rv-exp-loads` | thumbv6m 1.000000 | 1.008312 | yes | loss: RV +1.7%, +128 B |
| 4 | `m0-exp-layout` | rv32im 1.000000 | 1.019665 | yes | loss: Thumb +4.0%, +2084 B. Its targetcheck reports come from `--out` copies |
| 5 | `m0-sigmoid-cell` | rv32im 1.000000 | 1.020591 | yes | loss: Thumb +4.2%, +1584 B |
| 6 | `rv-tanh-quadratic` | thumbv6m 1.000000 | 1.038220 | yes | loss: RV +7.8%, +256 B |
| 7 | `rv-exp-interval` | thumbv6m 1.000000 | 1.073934 | yes | loss: RV +15.3% |
| — | `shared-small-sigmoid` | rv32im 1.080757 | 1.102717 | **rejected** | no targetcheck run on its object code. Also a regression on both boards (+8%/+12.5%) |

A best board at exactly 1.000000 means that target emitted the same code as id50, so the trial is neutral
there.

## Change versus base (id50)

Base: `eik-work/baselines/former-50/entry.c` (SHA-256 `88617bb4…60c3`, normalised `e8722042…4db8`). Diff:
[entry-vs-id50.diff](entry-vs-id50.diff). It matches the trial's own `id50.diff` in content.
- Only the guard at the end of the biased-exponent-119 Thumb tanh path changes. It now refines when the
  Q23 remainder is below 253952 instead of 262144, which admits 5,632 more fast returns per sign. The
  trial's `prove-bound.py` and `ROUNDING.md` certify the bound.
- RV32IM linked `.text`/`.rodata` are identical to id50. The Thumbv6-M image is 8 bytes larger.
- Thumbv6-M S is +0.038% / +0.033% on the two seeds.

## Freeze re-check of the chosen bytes

The commands, exit codes and stdout/stderr are in [evidence/logs/](evidence/logs/), with SHA-256 values in the manifest:
- `run.py test/scratch/freeze freeze check check entry.c` returned PASS, exit 0. Bytes: rv32im 18960,
  thumbv6m 20508, thumbv7em 21254. Stack bound: 176 / 312 / 280 (8 KiB cap). Within the 64 KiB image cap.
- `gate` accepted the source with the normalised hash above. Source size is 166756 bytes (cap 256 KiB).
- `fingerprint --details` matches the pinned verifier and measurement IDs.
- Target objects and guest images are in [evidence/objects/](evidence/objects/). The manifest binds their
  file SHA-256 and the SHA-256 of each allocated section.
  - File bytes embed the case build path.
  - The section bytes (`.text`, `.rodata*`, `.ARM.exidx`) were identical in a second independent case
    (`rebuild`).
  - No section is writable.
- I did not re-run the paired scores. Root `entry.c` is byte-identical to the trial source, so the trial's
  `evaluate-<seed>` logs are referenced by path and digest (`manifest.freeze_runs.trial_scores_referenced`).

## Follow-up

- No combination was warranted. id50 remains the stronger base on every board.
- The next attempts should target the Thumbv6-M typical class, which is the largest cost, with changes
  that do not add bytes:
  - fold the exp/sigmoid high-multiply emulation into fewer partial products;
  - share the tanh/sigmoid cell tables.
- The tanh-119 guard only pays off if the compiler emits it as one shift and branch. As written it costs
  two literal loads.
- Live champions 52/53/56 are withheld (HTTP 403), so ratios are against id50 only.
