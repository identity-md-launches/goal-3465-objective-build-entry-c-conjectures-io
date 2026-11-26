# Exact integer kernels, season 1: rules

## The task

Write one C file with three functions:

```c
uint32_t eik_sigmoid(uint32_t x);   /* correctly rounded 1 / (1 + e^-x) */
uint32_t eik_tanh(uint32_t x);      /* correctly rounded tanh x */
uint32_t eik_exp(uint32_t x);       /* correctly rounded e^x */
```

- `x` and the result are IEEE-754 binary32 bit patterns.
- The result must be **the binary32 value nearest to the exact real result, ties to even**, for
  **every** one of the 2³² inputs.
- **Special values:**
  - A NaN is quieted, keeping its sign and payload.
  - σ(+∞) = 1, σ(−∞) = +0, σ(±0) = ½.
  - tanh(±∞) = ±1, tanh(±0) = ±0.
  - exp(+∞) = +∞, exp(−∞) = +0, exp(±0) = 1.
  - exp overflows to +∞ from x ≈ 88.7228 (word `0x42B17218`), gives subnormal results below
    x ≈ −87.3365, and rounds to +0 below x ≈ −103.9721.

**Use only integer arithmetic.** The targets have no FPU, and floating point is not allowed in the
source.

**Starting point:** [template/entry.c](template/entry.c). It is correct on every input as it stands:
each function tries a fast path and falls back to the incumbent, `exact-c`'s implementation, which is
correct everywhere and takes ~100–200k instructions per call. The incumbent alone is in
[examples/incumbent.c](examples/incumbent.c).

## What the file may contain

The build force-includes [harness/eik.h](harness/eik.h). It provides:
- the fixed-width integer types, `size_t` and `bool`;
- `memcpy`, `memset` and `memmove`;
- the three prototypes.

**Allowed:**
- C11.
- Integer types up to 64 bits.
- `static const` tables.
- Local variables and arrays.
- Loops and `goto`.
- `static` helper functions.
- Pointers to your own locals and tables.
- These builtins: `__builtin_clz`/`clzll`/`ctz`/`ctzll`/`popcount`/`unreachable`.
- `__builtin_expect(value, hint)` as a condition only: in `if`/`while`/`for`/`do`, as the `?:` test, or as an operand of `!`, `&&` or `||`. `value` must be 32 bits or narrower and `hint` an integer literal, e.g. `if (__builtin_expect(x > y, 0))` or `#define likely(c) __builtin_expect(!!(c), 1)`.

**Rejected:**

| Rule | Why |
|---|---|
| Any directive except `#define`, `#undef`, `#if`, `#ifdef`, `#ifndef`, `#elif`, `#else`, `#endif`, in any spelling (`%:include`, a directive split by `\`-newline or around comments, `#include_next`, `#import`, `#embed`, `#pragma`, `#line`, …) | One prelude, no compiler control, no other files read |
| Trigraphs (`??=`, `??/`, …) | They are replaced before everything else and can hide directives |
| `_Pragma` (also when a macro assembles it), `__attribute__`, `[[…]]`, `asm`, `__has_include`, `__has_embed` | No compiler control, no probing of the file system |
| Code that depends on predefined macros (`__clang__`, `__riscv`, `__arm__`, `__x86_64__`, `__SANITIZE_ADDRESS__`, …) | Every build (each target, and the host's full check) must compile exactly the same tokens, or the full check would verify different code |
| Subtraction, shifts, division, remainder, comparisons, bitwise operators, `~` or `-` on a `sizeof` result or a pointer difference, or widening one to 64 bits | `sizeof` is 64-bit on the host and 32-bit on the targets, so these can give different answers. `+`, `*`, `sizeof a / sizeof a[0]` and storing into a 32-bit variable are fine; otherwise cast first: `(uint32_t)sizeof x` |
| Any floating-point type, literal or cast | Integer-only targets; floats could slip in via soft-float |
| File-scope or `static` variables that are not `const` | No state survives a call, so no caching of results |
| Non-`static` functions other than the three entry points | Only the entry points are exported |
| `volatile`, `_Atomic`, function pointers, indirect calls, pointer↔integer casts | Determinism and analysability |
| Plain `char`, `long` | Their signedness and width differ between the targets and the 64-bit host |
| `__builtin_expect` on a 64-bit value, with a non-literal hint, or whose result is used as a number | It returns `long`: a 64-bit value is truncated on the targets but not on the host |
| Recursion | Bounded stack |
| Calls to anything but your own functions, the three memory functions and the builtins above | No hidden library code |

The object file for each target is also checked:
- It has no writable data.
- It references only integer compiler-rt helpers, such as `__aeabi_lmul` and `__muldi3`. Any
  soft-float helper fails the check.
- It exports only the three entry points.

## Builds

- **Targets:** pinned clang (the `ziglang` wheel), with these flags:

  ```
  -std=c11 -O2 -ffreestanding -fno-builtin -ftrivial-auto-var-init=zero -fno-unwind-tables
  ```

  for `riscv32` (RV32IM), `thumbv6m` (Cortex-M0+) and `thumbv7em` (Cortex-M4/M33).
- **Host check:** gcc with `-fsanitize=undefined,address`.

`-ftrivial-auto-var-init=zero` gives an uninitialised local the same value (zero) on every target.
Its cost is counted in your score, so initialise only what you need.

## Correctness: every input

1. **Scored inputs.** Every output the scorer sees must be right.
2. **Target sample.** 32,768 words, one from each equal slice of the 2³² inputs at a seeded offset,
   are run on each emulated target per function and compared with the reference.
3. **Full host check.** All 2³² inputs per function are run under UBSan and ASan, which abort on the
   first undefined behaviour. The outputs are compared with SHA-256 digests of the reference over
   1M-word chunks.

Step 3 runs for every entry that would take over a board. A single wrong output or a single
undefined behaviour on any input rejects the entry. A board-winning entry's object code is also run
on every input for each target (rv32im, thumbv6m and thumbv7em), in QEMU, and must be right on all
of them before it takes any board.

**Why the host check stands for the targets:**
- The rules remove the usual sources of difference between 32-bit targets and the 64-bit host:
  `long`, `char`, `sizeof` arithmetic, uninitialised reads and pointer/integer casts.
- UBSan proves the absence of the remaining undefined behaviour on every input.
- What is left is the compilers' correctness. The target sample and the per-target check cover that.

**The reference.** The digests come from `exact-c` ([third_party/exact-c](third_party/exact-c)). An
independent implementation on GNU MPFR agrees with it on all 2³² inputs of every function.

## Score (lower is better)

There is one score per target board (`rv32im`, `thumbv6m`):

```
S = GM over {sigmoid, tanh, exp} of [ mean_typ^0.55 · mean_wide^0.30 · mean_hard^0.10 · mean_uniform^0.05
                                       · (1 + max(0, p99.9_hard − 20·mean_typ)/10^6)^0.1 ]
    · (1 + code_and_table_bytes / 64 KiB)^0.5
```

- **The means** are retired instructions per call in the emulator, on inputs drawn fresh for each
  evaluation from a recorded seed:

  | Set | Count per function | Content |
  |---|---|---|
  | Typical | 2,000 | sigmoid, tanh: N(0, 3) and N(0, 1) pre-activations. exp: softmax's x − max, −\|N(0, 3)\| (80%), and N(0, 3) (20%) |
  | Wide | 1,000 | Uniform over exponents for \|x\| ∈ [2⁻³¹, 2⁸] |
  | Hard | 300 | Near-midpoint inputs (within 2⁻¹⁸ ulp of a rounding boundary), specials, each function's thresholds, subnormals |
  | Uniform | 1,000 | Uniform over all 2³² words: every input counts a little, so a slow path anywhere costs score |

- **The tail term** stops an entry from sending whole regions to a slow fallback.
- **The size term** charges for code and tables.
- **The weights** were set by a dry run against deliberately gamed entries (memoising the hard
  set, trading bytes for speed, slow paths outside the scored sets): none of them gets within 3% of
  an honest equivalent.
- **`overall` board:** √(S_rv32im · S_thumbv6m).
- **`thumbv7em`:** measured and reported, not scored.

**Takeover:**
- On each board, an entry needs **S ≤ 0.97 × the champion's S, measured on the same fresh inputs**,
  then a clean full check.
- The metric has no noise. The same file with the same seed always gives the same counts, and the
  champion is re-measured with the challenger's seed.

**Caps:**
- 64 KiB of code plus tables per target.
- 8 KiB of stack, for every input. The gate bounds it from the compiled code before anything
  runs: the sum of the stack frames of every function in the linked image, yours and the
  compiler's helpers, as if all were active at once. An entry whose bound exceeds 8 KiB on any
  target is rejected at `stack:<target>`, and so is one whose bound cannot be established (an
  indirect jump, or a call cycle through compiler helpers). The incumbent's bound is about 3.5 KiB.
- 20M instructions per call.
- 256 KB of source.

**Duplicates:** an entry whose preprocessed source matches an accepted entry is rejected. The
comparison ignores whitespace, comments, macro wrappers and the names of everything the entry
declares, so a renamed copy is still a copy.

## Rewards

- **The champion only.** Each board pays its current champion; nothing goes to the runner-up.
- **Board shares.** The competition's share of the validator's weight is split between the boards:
  at launch overall 50%, rv32im 25%, thumbv6m 25%. The split is published live
  (`GET /v1/competitions/exact-integer-kernels/boards`); use that, not this page.
- **The reign limit.** A champion is paid in full for 5 days after taking a board, then linearly
  less, and nothing from day 7 on, while it keeps the board unbeaten. A new takeover starts a new
  reign.
- **Unheld boards pay the treasury.** Every board opens with a launch champion that is nobody's
  entry, so its share goes to the conjectures.io treasury until a miner takes it.
- Weights are set once per epoch (about 72 minutes).

## Submitting

One submission is one file, `entry.c` (at most 256 KB, UTF-8). Each subnet registration buys one
submission, and a rejected entry still uses it, so check first:

```bash
python -m eik check entry.c                     # static rules and builds (seconds)
python -m eik evaluate entry.c --quick          # score against the incumbent, 3% of inputs checked
python -m eik fullcheck entry.c --function tanh # every input of one function
python miner/submit.py submit entry.c --hotkey ~/.bittensor/wallets/W/hotkeys/H
```

The upload is signed by your hotkey over the competition slug `exact-integer-kernels`, the file's
SHA-256 and a timestamp. The validator runs the same checks and scoring as `eik evaluate`, on a seed
you cannot know in advance.

## Licence

Submitting grants the code under MIT or Apache-2.0 (at the recipient's option), so that winners can
ship in `exact-c`.

## Published sources

A former champion's source is published under that licence, at
`GET /v1/competitions/exact-integer-kernels/submissions/{id}/source`, once it holds no board. A
current champion's source is never published.

A source also stays unpublished while it **discloses a current champion**: while 80% or more of a
current champion's code also appears in it. The comparison ignores comments, whitespace and names,
and does not count code from the template or the incumbent, which everyone has. Such a source is
published once no current champion is that close to it.

This matters when one author's entries are near-copies, for example two builds of one file tuned
for different boards. Without it, the one that lost its board would publish the code of the one
still reigning.
