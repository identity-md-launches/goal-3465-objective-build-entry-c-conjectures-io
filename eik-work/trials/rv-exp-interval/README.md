# rv-exp-interval: early unsigned exp interval dispatch

This packet tests exactly one dispatch change from unchanged former submission 50.
The source is `entry.c`; `id50.diff` is the complete byte-for-byte source diff.
No arithmetic, tables, selector, target/compiler probes, scorer settings, or fallback
paths were changed. The run is local; nothing was signed or submitted.

## Exact equivalence argument

The old cubic path is reached precisely when all three conditions hold:

1. `(int32_t)w < 0`;
2. `w > 0xBF800000u`;
3. `(w - 1) <= (0xC0800000u - 1)`.

Their intersection is the inclusive unsigned interval
`[0xBF800001, 0xC0800000]`, containing 16,777,216 words. Binary32 encodings
there represent `-4 <= x < -1`. The new condition
`(w - 0xBF800001u) <= 0x00FFFFFFu` selects exactly that interval: unsigned
subtraction wraps modulo 2^32, and a result at most 2^24-1 occurs exactly for
these words. It introduces no signed overflow or undefined shift. Every word
outside the interval follows the complete old dispatch. `dispatch-proof.c`
exhaustively checks the equality of these predicates over all 2^32 words;
its command records and raw output are retained.

The new goto lands before the first declaration/initializer in the old block.
No automatic value computed by bypassed comparisons or blocks is needed there.
For a selected word, every following integer intermediate is identical to id50:
`ix`, `u`, `F1`, both signed high-product stages of `s`, `p`, and `rr`. The
coefficient row and each table access are identical. Consequently the predicate
`(rr << 24) >= F1` has the same truth value, and its fast return
`ext_r.w[ix] - (rr >> 8)` is bit-for-bit identical. No new approximation or
rounding decision is introduced.

If that return is unresolved, the same `F0` and `F1` choose the same refinement:
negative `F1` sets exactly the same `cF0` and `crr` before `kink_`; otherwise
`cV=rr>>8` and `cE=F0` precede the unchanged `cresA_` refinement. All fast
returns, including exceptional inputs, tiny inputs, and endpoints outside this
interval, retain id50's integer intermediates and round-to-nearest-even logic.
The exhaustive reference checks, rather than a new error bound, validate those
inherited rounding decisions.

Endpoint ownership is unchanged: `0xBF800000` (-1) uses its old non-cubic path;
`0xBF800001` uses its original `ix=161` cell; `0xC0800000` (-4) uses
its original `ix=673`, `u=0` cubic endpoint arithmetic; `0xC0800001` uses the next old path. The selected
QEMU chunks `3063:3082` contain the full modified interval and neighborhoods
on both sides. Boundary tests additionally exercise each cell edge, adjacent
words, cell centers, fresh near-midpoint inputs and neighbors, NaNs, infinities,
and signed zeros on the actual scored guest images.

## Reproduction and evidence

`run-trial.py` records the pinned `run.py` setup, fingerprint, check, gate, two
unmodified full-population measurements and quick host checks, then object-code
checks on all three targets and complete host checks of all three functions.
Builds, dependencies and caches go exclusively in `test/scratch/`.
`packet.json` follows the paired-control schema and is verified by its verifier.
All per-command records contain argv, source hash, exit code, runtime, and hashes
of raw stdout/stderr. Supplemental instrumentation is in `inspect-path.py`;
its dynamically executed conditional-branch counts do not contribute to S.

The competition's current-board response is retained in `boards.json`.
The paired comparator is former id50, not the current unpublished champions;
current-champion scores/ratios and board-takeover claims are unavailable (`null`).
A bounded `evaluate --quick --json --seed` attempt is made for each seed as
required; if local exact-c incumbent remeasurement times out, the accepted
paired-control stage form provides absolute S and candidate/id50 ratios with
the exact same scoring populations, fresh hard pools, and quick host checks.

From a clean checkout, reproduce in this order (no submission commands):

```sh
python3 eik-work/toolkit/provision.py --fetch
python3 eik-work/trials/rv-exp-interval/run-trial.py
python3 eik-work/trials/rv-exp-interval/run-inspection.py
test/scratch/rv-exp-interval/runtime/bin/python eik-work/trials/rv-exp-interval/compare-sections.py
python3 eik-work/trials/rv-exp-interval/finalize.py
```

`compare-sections.py` is the final disassembly pass: ARM `$t`/`$d` mapping symbols
keep embedded literal pools as data and prevent a linear decoder from stopping
before `eik_exp`. It also compares all allocated sections; metadata-only ELF
changes do not count as changed machine code. The final evidence checksum list
is `evidence.sha256`. `verify-evidence.py` validates supplemental claims in
addition to the required paired-control verifier.

`compiled-image-metadata.json` separately records entry-object, guest-ELF, and
QEMU-checker file sizes and hashes, plus guest allocated-section byte totals.
These file lengths are distinct from the competition's charged image bytes in
`packet.json`; the supplemental verifier binds the recorded checker ELF hash to
the actual `targetcheck` report.
