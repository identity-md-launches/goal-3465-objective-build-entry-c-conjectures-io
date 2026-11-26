# rv-tanh-quadratic: guarded quadratic in eik_tanh_r (negative result)

Outcome: **measured, regression** (not an eligible optimisation). Source `entry.c` SHA-256
`595ce32546773015313ae8d5785d474304f2b4242b402604095e4443a9f60745`; id50 base
`88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3`. Diff: `id50.diff`. Hashes: `hashes.txt`.

## Change (one technique)
In `eik_tanh_r`, label `cells_`, for `tld_r` rows 0..27 (|x| roughly 0.07..0.17, `c1 != 0`) the cubic
`V = c0 + mulhs(c1 + mulhs(c2 + mulhsx(c3,t), th), th)` is replaced by a quadratic with the row's
`c2' = c2 + mulhsx(c3, t_centre)` taken from a new 28-entry table `tq_r` (112 bytes). Same high-half multiply
formulation (`mulhs_r`). Fast return `w - (Vq>>8)` only if
`((Vq - 4) - 40*(th>>31)) & 255 < 210`; otherwise control falls to the unchanged cubic/refinement code.

## Why each fast return is correct
`bound-proof.c` evaluates, for every `w` of rows 0..27 (7,337,984 inputs, whole selected interval, same integer
arithmetic as the entry), V (cubic) and Vq. Exhaustive result: `Vq - V` is in [-42,+2] for even rows and [-2,+42]
for odd rows (th sign = cell parity), so V in [Vq-2,Vq+42] (even) / [Vq-42,Vq+2] (odd). Accepting only
Vq mod 256 in [4,213] (even) / [44,253] (odd) forces V mod 256 in [2,255] with the same floor, i.e. the cubic would
itself take its `V & 254` fast return with the identical `V>>8`. The program also counts disagreements: 0 of
6,019,525 accepted (82%); the window edges are the proven bound edges (not separately enumerated).
Midpoint-adjacent values (V mod 256 in {0,1}) are never accepted. Rejected inputs run the cubic unchanged.
Fixed-point error is included because the bound is on the integer results, not on real values.

## Results
Absolute S, ratio candidate/id50 (lower is better): see `packet.json` (`ratio_vs_control`).
rv32im 30.692 vs 28.523 (**1.0761**) seed 1874435642, 30.739 vs 28.517 (**1.0779**) seed 1947282751;
thumbv6m 1.0 (EIK_SEL selects the `t_` path; identical object code); overall 1.0373 / 1.0382.
rv32im tanh class means (seed 1874435642) typical 25.80 -> 34.79, wide 14.50 -> 16.53, hard 51.69 -> 57.38,
uniform 9.20 -> 9.44; hard p99.9 92 -> 108; sigmoid/exp unchanged. Bytes rv32im 18960 -> 19216 (+256: table
and code); stack bound unchanged 176/312/280. Correctness: zero wrong outputs, sample 0 mismatches, quick host
checks 0 mismatches on all functions both seeds, `check` PASS, gate accepted (normalised hash differs from id50).
`targetcheck-tanh-rv32im-985-992` and `-3033-3040` (7,340,032 words each, all affected positive/negative chunks
on rv32im QEMU) passed.
Instruction inspection (`touched-path.s`): the family path is lui/addi/add table address, 2 lw, 2 mulh, a
`bgeu` guard and `srli`; the new range test (`qi_ < 28`) adds instructions to every cells_ call. The expected
saving (one lw/mulh/add) is outweighed by 18% fallbacks that pay quadratic + full cubic, and by the range test.
Typical tanh evidently concentrates in this family, so the typical mean rose.

## What to try next
Do not reduce degree with a 2^18-wide cell: the dropped term is up to 42/256 ulp. A usable version needs half
cells (error ~21) or a 3-instruction-free selection without a range branch.

## Environment note
This worker had no GCC: a Ubuntu GCC 13.3 was extracted from debs into scratch and exposed as `gcc` through the
scratch kit's sandbox PATH (the sandbox.py copy in the scratch case only; evaluator files hashed in the
fingerprint were untouched, fingerprint matches the pinned identities except possibly the host GCC line).
Failed first attempts (zig libc probe with a `cc` shim) are not part of the packet.

Scores were taken in stage form (`measure` + `fullcheck --quick` per seed), as in the control; `evaluate` was not run.
