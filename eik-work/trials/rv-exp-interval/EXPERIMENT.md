# Experiment log and outcome

**Reject for integration: a correct, nonduplicate RV32 regression.** Keep id50 as
the better base. This trial adds one early unsigned word-range dispatch and no
other optimisation. It does not reach 0.970× id50 on any board. Current private
champions cannot be remeasured from their unavailable sources, so those ratios
and a current-board takeover result are `null`, not inferred from API ratios.

## Sources and eligibility

| source | SHA-256 | normalised SHA-256 |
|---|---|---|
| exact id50 | `88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3` | `e8722042f89400f887e0e526338d22ae756c029c4646c49c4d290da1bda04db8` |
| candidate | `259751b6c7fd5072a081211b8a11f4e27a5d0e8bda9aaab666ae067dd20a0ea9` | `332cb47966adb4e07c1485aa843f5aee6a191a29da3dd7f718ef477dd2b5713d` |

The gate accepts the candidate. Its normalised tokens differ from id50, and its
RV32 instructions differ: this is a genuine dispatch experiment, not a renamed
copy. Both Thumb targets have identical allocated machine-code/table sections
and identical counts. The existing selector picks their unchanged alternative
implementation; they are unchanged code generation, not eligible improvements.
Whole ELF hashes differ because metadata differs; `loaded-section-hashes.json`
compares allocated sections and `branch-counts.json` separately hashes `eik_exp`.

## One technique, two paired seeds

| seed | board | id50 S | candidate S | candidate/id50 |
|---|---|---:|---:|---:|
| 1874435642 | rv32im | 28.52271424241966 | 32.896202279994895 | 1.153333515190882 |
| 1874435642 | thumbv6m | 40.515260593492414 | 40.515260593492414 | 1.000000000000000 |
| 1874435642 | overall | 33.99419362722625 | 36.507508925017504 | 1.073933664241364 |
| 1947282751 | rv32im | 28.517414314250885 | 32.83644311370611 | 1.151452328456613 |
| 1947282751 | thumbv6m | 40.30303897386101 | 40.30303897386101 | 1.000000000000000 |
| 1947282751 | overall | 33.90189464529962 | 36.3786812099431 | 1.073057467452985 |

This is absolute S calculated by the pinned scorer, with all populations and
fresh pools unchanged. The paired control uses identical input digests and hard
pool sizes. Each seed measures 2,000 typical, 1,000 wide, 300 hard, and 1,000
uniform inputs **per function**, on all three targets. Sigmoid/tanh are unchanged.
`packet.json`, `comparison.json`, `scores.csv`, and `exp-class-means.csv` retain
full precision and all targets. No API challenger/reference ratio is treated as S.

## Affected exp class means and branches

RV32 instructions per complete exp call (old → candidate):

| seed | typical | wide | hard | uniform | hard p99.9 |
|---|---:|---:|---:|---:|---:|
| 1874435642 | 30.5635 → 44.1400 | 24.738 → 41.079 | 41.486667 → 57.750000 | 13.297 → 28.900 | 80 → 112 |
| 1947282751 | 30.3270 → 43.7170 | 24.847 → 40.910 | 43.090000 → 59.156667 | 13.322 → 28.850 | 90 → 112 |

Hard-tail multiplicative factors remain exactly 1.0 for every function/target/seed.
All Thumb class means and hard tails remain unchanged; their full values are in
the packet. This is a regression for typical, wide, hard, and uniform RV32 exp.

Dynamically executed conditional branches per exp call, using a supplemental
block hook on the exact guest image (not used to score S):

| seed | target | typical old → candidate | wide old → candidate |
|---|---|---:|---:|
| 1874435642 | rv32im | 4.7350 → 4.2275 | 4.975 → 5.894 |
| 1947282751 | rv32im | 4.6815 → 4.1365 | 4.957 → 5.876 |
| 1874435642 | thumbv6m | 3.3845 → 3.3845 | 5.079 → 5.079 |
| 1947282751 | thumbv6m | 3.3490 → 3.3490 | 5.085 → 5.085 |

Affected RV32 words save exactly two conditional branches per call. There are
1,005/1,030 affected typical inputs, but only 27 wide inputs in each seed.
For affected typical inputs the old/candidate means are 27.999005/37.999005
and 27.754369/37.754369 instructions: **+10 instructions despite fewer branches**.
The measured population deltas match `((n - affected_n) - 2*affected_n)/n`:
one added conditional branch outside the interval and two saved inside it.
Unconditional branches, calls, and returns are excluded from the RV32/M0 branch
metric; S counts all instructions. The JSON includes affected-subset branch means too.

## Emitted instructions and cost

The full executable-section disassemblies for both sources and all targets are
retained as `id50-*.asm` and `candidate-*.asm`. RV32 `eik_exp` starts at `0x15238`.
The original entry immediately executes `bltz a0`; the candidate first executes:

```
addi sp, sp, -0x10
sw   ra, 0xc(sp)
sw   s0, 8(sp)
sw   s1, 4(sp)
addi s0, sp, 0x10
lui  a1, 0x40800
addi a1, a1, -1
add  a1, a0, a1
srli a1, a1, 0x18
bnez a1, <outside interval>
```

The compiler reduced the unsigned interval test to a top-byte test after adding
`0x407fffff`. Selected words then execute the same `mulhsu`, `mulhsu`, and `mulhu`
cubic arithmetic. However, `nx_cell_r`, inlined in id50, is emitted as a separate
72-byte function here. A rare path now calls it while preserving `s1`; the whole
exp entry acquires the five-instruction prologue and shared five-instruction
restore/move sequence. Id50's stack frame was confined to its rare division path.
This explains the +10 instructions even inside the interval; the interval test
itself uses five instructions, as do the three original nested comparisons.
The out-of-interval population also pays the new test, sometimes an extra call.
The disassembly demonstrates these changes; compiler inlining/frame-placement
heuristics are the explanation inferred from it, not a separate measured score.

| target | charged bytes old → candidate | static stack bound old → candidate | measured peak old → candidate (seed 1 / seed 2) |
|---|---:|---:|---:|
| rv32im | 18960 → 19060 | 176 → 192 | 0 → 24 / 8 → 28 |
| thumbv6m | 20500 → 20500 | 312 → 312 | 60 → 60 / 60 → 60 |
| thumbv7em | 21254 → 21254 | 280 → 280 | 40 → 40 / 40 → 40 |

Charged bytes are the kit's code-plus-table metric, not on-disk ELF file lengths.
The candidate respects source/image/stack/instruction caps. Source and gate
records bind these values to the candidate hash. The unchanged source selector
is preserved exactly; no target macro or compiler option was introduced.

## Checks and limits

- `check` and `gate`: accepted, identical preprocessed tokens across builds.
- Two full-population scored measurements: zero wrong outputs. Per seed/target,
  98,304 stratified sample words have zero mismatches.
- Two quick UBSan/ASan checks for each function: 134,217,728 inputs per check,
  zero mismatches. These are samples, not exhaustive checks.
- Exact unsigned-dispatch equivalence: all 4,294,967,296 words, zero mismatches.
- Compiled guest boundaries/midpoints: 1,098 words per source/target, zero wrong
  outputs. Includes 12 and 9 fresh near-midpoint words in the changed interval,
  their neighbors, cell boundaries, center words, endpoint neighbors and specials.
- QEMU `targetcheck`, `--chunks 3063:3082 --jobs 2`: 19,922,944 exp words on
  **each** of RV32IM, Thumbv6M, Thumbv7EM, zero mismatches. This covers the entire
  modified interval and surrounding words; it is not an all-input target check.
- Complete host UBSan/ASan checks and bounded evaluate attempts are recorded by
  `run-trial.py`; their final raw reports and exact coverage are indexed in
  `comparison.json`. Never infer a complete check from a quick check.

## What to try next

Do not integrate this dispatch into the best entry. A later, separately assigned
experiment could move the existing cubic block rather than retaining two entry
edges, and inspect whether the compiler preserves `nx_cell_r` inlining and the
rare-path-only frame. That is outside this one-change trial. Saving branch tests
alone did not reduce retired instructions; wide and uniform populations penalise
an early check before the existing special/tiny dispatch.

## Completed exhaustive host checks

The GCC host checker used ASan and UBSan together, with no quick or chunk limit.
All checks returned exit 0, complete=true, and no sanitizer failure.

| function | inputs | mismatches | checker seconds |
|---|---:|---:|---:|
| sigmoid | 4,294,967,296 | 0 | 857.6 |
| tanh | 4,294,967,296 | 0 | 870.6 |
| exp | 4,294,967,296 | 0 | 858.0 |

These are full host checks. The target-object checks remain the selected exp
chunks documented above, not exhaustive checks of all three functions on every ISA.

## Standard evaluate attempts

- Seed 1874435642: wrapper cap 180 s; observed runtime 180.105 s; process exit -9; no completed evaluator report. Exact command and raw streams are in `evaluate-attempt-1874435642.*`.
- Seed 1947282751: wrapper cap 180 s; observed runtime 180.023 s; process exit -9; no completed evaluator report. Exact command and raw streams are in `evaluate-attempt-1947282751.*`.

The bounded standard evaluations include remeasurement of the local exact-c
incumbent, not a current private champion. They emitted no completed score
report; their scores and kit verdicts are null. Successful unmodified
`measure --seed` plus the matching `fullcheck --quick --seed` stages supply
the packet's absolute S and paired id50 ratios, exactly as in paired-control.
No scorer populations, hard pools, weights, targets or sampling settings were
reduced to obtain these results.
