# RV32IM exp reduction constant access

This trial starts from former submission 50, SHA-256 `88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3`. The candidate SHA-256 is `8e5f8332e0fdf6a70edaecd6255c7b11a9920f988329a0b753dd5559e47f5595`. [id50.diff](id50.diff) contains the complete source change. The experiment replaces the three fixed byte-offset constant reads in each of the two positive reduction blocks with typed row indexing.

## Integer equivalence and rounding

The 256-word `hi` array occupies 1024 bytes, and the 256-halfword `lo` array occupies 512 bytes. In the pinned builds the offsets 1536, 1540 and 1552 are the addresses of `row[0]`, `row[1]` and `row[4]`. The previous reader dereferenced a `const uint32_t *`, so the typed expression reads the same complete word under the same byte order.

| Table pointer on entry | Prior byte accesses relative to the object | Typed row indices | Words returned in order |
| --- | --- | --- | --- |
| `&ex8_r` | 1536, 1540, 1552 | 0, 1, 4 | 1549082005, 1488522236, 387465216 |
| `&ex8_r + 4 bytes` | 1540, 1544, 1556 | 1, 2, 5 | 1488522236, 5592664, 96817625 |

The normal positive entry sets `pb` to the object base. The jumps from `nmain_` can use a byte pointer advanced by four. That negative block starts at the object base, or at base plus four if entered through `kink_`. The latter cannot advance again. Its `T` read uses an aligned offset from 4 through 1024 inclusive, where each word is nonzero. This follows from the nonzero `hi[1..255]` entries and the nonzero first pair of `lo` halfwords at offset 1024. Both entry bases therefore give the identical three integer operands. Negative reduction, the table pointer itself and all other reads retain the original expressions.

The operands feed the same unsigned product, shifts, subtraction and correction. Thus `Y`, `k2`, `rho`, the lookup index, `V` and `qp` agree bit for bit. Each fast return uses the original `V & 248u` test and returns the original word. At a midpoint or whenever the guard leaves rounding unresolved, the identical `cT`, `ck`, `cC`, `cX`, `cV`, `cE` and `pb` reach the original `posr_` and `ex_res_r` refinement. The argument is equivalence to the control's rounding decision, including ties, with no new approximation bound needed.

The RV32IM digest checks cover the neighboring inputs at `0x3b7fffff/0x3b800000` (start of the positive reduction), `0x41000000/0x41000001` (reduction block transition) and `0x42b17217/0x42b17218` (overflow). They also cover the near-midpoint examples `0x3f89f9bd` and `0x4114171a` from the kit's reference hard list. These give `V = 0xbc120e05` and `0xa37da805` respectively, both with `(V & 248u) == 0`, exercising refinement in each block. The broad negative shard covers the original negative dispatch and the conditions that can lead to the shared labels.

## Emitted RV32IM instructions

[The control listing](id50-rv32.disasm) and [candidate listing](candidate-rv32.disasm) show the entire `eik_exp` symbol from the pinned relocatable objects. Relocation annotations identify address materialisation, including `lui` followed by the low relocation shown as `mv` before linking. Capstone prints PC-relative branch and jump displacements.

- Control `pmain_` forms the table base once at `0x0d18` and uses `lw` with offsets `0x600` and `0x604`. The exceptional route loads `0x610` at `0x0d80`. Control `pbig_` at `0x0fdc` uses the same base and all three immediate-offset loads.
- The candidate retains the two or three coefficient loads, and the indexed `hi` load. In `pmain_` at `0x0d14` and `pbig_` at `0x1004`, the compiler emits a second table-base materialisation followed by `xor`, `snez`, `slli` and `add` to address `Ct`. It selects a small displacement for `Bq` with a branch and an immediate, then adds and loads. It also emits displacement selection and address formation for `C`, after the guard in `pmain_` and before the polynomial in `pbig_`.
- The coefficient values themselves remain memory loads. The new literals are small index displacements. The existing `lui 0x17184` elsewhere is in the original refinement path and does not replace the touched `C` load. The `eik_exp` symbol grows from 2028 to 2156 bytes, or 32 RV32 instructions. Whole-image sizes and observed stack are reported below.

For either unshifted entry, the table-base and `Ct`/`Bq` access sequence grows from 4 to 14 retired instructions. Where the `C` access runs, its sequence grows from 1 to 5 retired instructions. These counts exclude the separate indexed `hi` load and arithmetic.

A follow-up would test passing the three typed constants from direct positive dispatch and retaining byte loads at separate legacy re-entry labels. That would give the compiler distinct inputs before the merge and show whether folding wins against RV32IM's already cheap displacement loads.

## Paired measurements

These are same-input comparisons against former submission 50. Lower is better. Live submissions 52 (RV32IM), 53 (Thumbv6-M) and 56 (overall) withheld their sources with HTTP 403, so the live champion scores and ratios are unavailable and a live takeover is unverified. See [live-reference.json](live-reference.json).

| Seed | Board | Id50 S | Candidate S | Candidate / id50 |
| --- | --- | ---: | ---: | ---: |
| 1874435642 | rv32im | 28.522714242 | 28.995332483 | 1.016569890 |
| 1874435642 | thumbv6m | 40.515260593 | 40.515260593 | 1.000000000 |
| 1874435642 | overall | 33.994193627 | 34.274676534 | 1.008250906 |
| 1874435642 | thumbv7em (report only) | 39.956338503 | 39.956338503 | 1.000000000 |
| 1947282751 | rv32im | 28.517414314 | 28.993482723 | 1.016693954 |
| 1947282751 | thumbv6m | 40.303038974 | 40.303038974 | 1.000000000 |
| 1947282751 | overall | 33.901894645 | 34.183701733 | 1.008312429 |
| 1947282751 | thumbv7em (report only) | 39.749544203 | 39.749544203 | 1.000000000 |

Both Thumb targets have identical linked allocatable section contents. On RV32IM the read-only data matches and the linked text grows by 128 bytes. The gate accepted the candidate and its normalized source hash differs from id50. The distinct RV32IM code regressed, so this experiment produced no optimization to carry forward. None of the paired ratios reaches 0.970.

| Seed | Target | exp typical | exp wide | exp hard | exp uniform | exp hard p99.9 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1874435642 | rv32im | 30.56350 → 31.59600 | 24.73800 → 26.64200 | 41.48667 → 43.82333 | 13.29700 → 13.57500 | 80 → 84 |
| 1874435642 | thumbv6m | 42.92750 → 42.92750 | 34.36700 → 34.36700 | 56.89333 → 56.89333 | 19.86000 → 19.86000 | 146 → 146 |
| 1874435642 | thumbv7em | 39.77550 → 39.77550 | 32.86100 → 32.86100 | 53.59667 → 53.59667 | 21.08500 → 21.08500 | 136 → 136 |
| 1947282751 | rv32im | 30.32700 → 31.32500 | 24.84700 → 26.87200 | 43.09000 → 45.38000 | 13.32200 → 13.56600 | 90 → 90 |
| 1947282751 | thumbv6m | 42.68500 → 42.68500 | 34.30900 → 34.30900 | 59.44667 → 59.44667 | 20.14700 → 20.14700 | 153 → 153 |
| 1947282751 | thumbv7em | 39.54550 → 39.54550 | 32.76000 → 32.76000 | 56.11000 → 56.11000 | 21.38700 → 21.38700 | 151 → 151 |

All tail factors were 1.0 for every function and target on both seeds. The full instruction statistics match for sigmoid and tanh on every target.

| Seed | Target | Scored image bytes | Observed stack bytes |
| --- | --- | ---: | ---: |
| 1874435642 | rv32im | 18960 → 19088 | 0 → 0 |
| 1874435642 | thumbv6m | 20500 → 20500 | 60 → 60 |
| 1874435642 | thumbv7em | 21254 → 21254 | 40 → 40 |
| 1947282751 | rv32im | 18960 → 19088 | 8 → 8 |
| 1947282751 | thumbv6m | 20500 → 20500 | 60 → 60 |
| 1947282751 | thumbv7em | 21254 → 21254 | 40 → 40 |

Static stack bounds were 176, 312 and 280 bytes on RV32IM, Thumbv6-M and Thumbv7E-M for both sources. Per seed and target the candidate passed all 12,900 scored outputs and 98,304 stratified sample outputs with zero mismatches. The packet retains all functions and classes, including both fresh input digests.

## Verification evidence

The [target replay script](replay-targetcheck.sh) runs the pinned QEMU check from the repository root with staged dependencies. [Input hashes](targetcheck-inputs.sha256) identify the ordinary source and reference files used by the replay. The RV32IM `eik_exp` disassembly matched across the evaluation, measurement and targetcheck build cases.

| RV32IM exp chunk range | Words checked | Mismatches | Raw report |
| --- | ---: | ---: | --- |
| 951–952 | 2,097,152 | 0 | [Boundary at the start of positive reduction](targetcheck-rv32im-exp-951.stdout) |
| 1039–1041 | 3,145,728 | 0 | [Boundary at 8](targetcheck-rv32im-exp-1039.stdout) |
| 1066–1067 | 2,097,152 | 0 | [Overflow boundary](targetcheck-rv32im-exp-1066.stdout) |
| 952–1066 | 120,586,240 | 0 | [Bulk of the positive reduction interval](targetcheck-rv32im-exp-952.stdout) |
| 3064–3116 | 55,574,528 | 0 | [Negative dispatch and reduction](targetcheck-rv32im-exp-3064.stdout) |

Every listed range passed against the corresponding reference chunk digests. The positive ranges together cover the full positive reduction interval and the neighboring boundary words. Some ranges overlap, so the row counts are per run.

Both `eik evaluate --quick --json` reports completed in fresh local cases without registered board references. Their local takeover labels describe unheld boards. The paired ratios use the independently recorded former-50 control and the identical input digests. Both seeds also ran the standalone measure and quick host stages, which agree with the evaluations. Each quick sanitizer result checked 134,217,728 words per function, with zero mismatches or sanitizer reports.

Two additional evaluations used the kit's setup-registered local incumbent. Each exceeded the 570-second command limit during evaluation and returned 124 without a final report. [The attempt record](incumbent-evaluate-attempts.json) retains both commands and their stdout and stderr hashes. These attempts are separate from the successful unheld-case evaluations and the pinned same-seed id50 comparison.

The exhaustive host sanitizer checks each covered all 4,294,967,296 inputs with zero mismatches and no UBSan or ASan reports. [Exp](exhaustive-host-exp.stdout), [sigmoid](exhaustive-host-sigmoid.stdout), [tanh](exhaustive-host-tanh.stdout).
