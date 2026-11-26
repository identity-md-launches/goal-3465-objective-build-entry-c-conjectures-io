# Independent review of the frozen fallback

The frozen [entry.c](../../../entry.c) is byte-identical to `m0-tanh-refine`, with SHA-256 `593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b`. It is the least-regressing eligible trial under the original selection rule. It ties id50 on RV32IM and loses on Thumbv6-M and overall. It reaches 0.970× id50 on zero boards. The review result is **incomplete** for the live objective. The retained board snapshot records withheld sources for 52, 53 and 56, and supplies no same-input live champion denominator. Live takeover and duplicate status against private sources remain unknown. [Freeze manifest](../../freeze/manifest.json) · [Historical source responses](../../trials/m0-tanh-refine/live-sources.json)

## Source, runtime and correctness

- I reran pinned `eik check`, `eik gate` and `fingerprint --details` on Linux x86-64 with Python 3.12.3 and GCC 13.3.0. The network namespace exposed only loopback. The kit commit is `5a32428ad4aa23bce737d50a738ace24ddeeed2e`. The fresh fingerprint matches the freeze, including compiler settings, reference digests and measurement constants. Three omitted runtime payloads were recovered at their exact SHA-256 pins in scratch. The committed export still lacks them, so a cold downstream evaluator run requires the exact payload restoration. [Fresh commands](logs/commands.json) · [Bootstrap log](logs/isolated-bootstrap.stdout) · [Fingerprint](logs/fingerprint.stdout) · [Runtime manifest](../../offline-runtime/manifest.json)
- Source size is 166,756 bytes within the 256 KiB cap. The pinned text, AST, preprocessing, host-width and linked-image checks passed. The source has integer arithmetic, static constant tables and no include directives. The retained ELF section and whole-file digests agree with the freeze. The three submission objects export exactly the entry points. They and their guest images have zero writable allocated bytes. RV32IM imports the integer helper `__udivdi3` and neither Thumb object imports a helper. [Check](logs/check.stdout) · [Gate](logs/gate.stdout) · [Frozen objects](../../freeze/evidence/objects/) · [Pinned rules](../../toolkit/kit/RULES.md)
- Fresh compiled selector probes returned 1 on GCC x86-64 and RV32IM, and 0 on both Thumb targets. The inherited `L'\0' - 1 < 0` selector uses the implementation-defined type of a wide character constant. Preprocessing produces the same entry tokens across builds, while compilation chooses different kernel arms. The fresh RV32IM scored guest has byte-identical `.text` and `.rodata*` to id50. Both Thumb guests differ. The GCC sanitizer results cover the host-selected arm. Evidence for the Thumb arm comes from its proof and target runs. [Probe](logs/probe.stdout) · [Source](../../../entry.c)
- Fresh Unicorn runs checked ±0, ±∞, quiet and signaling NaNs of both signs with representative payloads, and adjacent exp words around overflow, the normal/subnormal boundary and underflow to zero. All three guests matched the explicit special-value expectations and pinned reference on the threshold inputs. In particular `exp(0x42b17217)` returns `0x7f7fff84` and `exp(0x42b17218)` returns `0x7f800000`. [Probe vectors and results](logs/probe.stdout)
- Fresh pinned normalization produced `adf3a5a8074ffcca8e58ea852f58143a20a00aa6a74df8f14c1b742fa21a03c8`. It differs from the recomputed normalized digests of available accepted sources 37, 42, 46, 48 and 50. Their raw bytes match the retained publication metadata. The eight candidate digests are distinct. [Probe](logs/probe.stdout) · [Published-source metadata](../../toolkit/api/)
- The distinct historical full-check evidence records 4,294,967,296 inputs per function under GCC with UBSan and ASan, and the same count for each of the nine target/function pairs in QEMU. All record zero mismatches on the frozen source hash. The review validates those reports and their command/log hashes. The fresh exhaustive-range work in this review consists of the four Thumb guard shards below. [Merged report](../../trials/m0-tanh-refine/exhaustive-merged.stdout) · [Per-run evidence index](result.json)

| Target | Code and tables (bytes) | Static stack bound (bytes) |
|---|---:|---:|
| RV32IM | 18,960 | 176 |
| Thumbv6-M | 20,508 | 312 |
| Thumbv7E-M | 21,254 | 280 |

All three are within 65,536 bytes of code and tables and 8,192 bytes of stack. The instruction maxima reported for the two scored populations are within the 20 million instruction cap.

## Exponent-119 tanh change

The sole source edit changes the remainder test at the end of `t_l998689`. With `r = z mod 2^23`, the old fast path requires `r ≥ 262144`. The new test reads bits 13–22 and requires their value to be at least 31, equivalent to `r ≥ 253952`. The quotient and the slow-path argument are unchanged. The sign falls out of the exponent and cell extraction. Each certified fast result subtracts the same magnitude correction from either sign's bit pattern. [One-line diff](../../freeze/entry-vs-id50.diff) · [Rounding derivation](../../trials/m0-tanh-refine/ROUNDING.md)

The first cell `f = 32768` bypasses this guard because the unsigned left shift by 17 is zero. Its inherited branch covers the lower binade boundary. The certificate establishes `tanh(x) > 1/256` at the first word of the next cell. Since tanh is increasing and below `x < 1/128` throughout, every remaining exact result is in the same binade. The 32,767 certified cells span all remaining magnitude words through the final cell. The polynomial products and sum fit unsigned 32-bit arithmetic there. The outward Q96 Taylor enclosure plus one unit for the tail bounds the monotone correction at cell endpoints. In Q54 units the resulting residual is `[-250889, -33522]`. At the new cutoff the exact correction clears the lower midpoint by at least 3,063 units. At the largest remainder it stays at least 33,523 units below the upper midpoint. The strict interval removes any need for a tie decision in the newly fast cases. Below the cutoff the original refinement remains in place. [Proof script](../../trials/m0-tanh-refine/prove-bound.py) · [Fresh proof replay](logs/prove-bound.stdout)

The proof accounts for 5,632 new fast returns per sign in positive chunks 952–958 and the corresponding negative chunks 3000–3006. I reran chunks `952:960` and `3000:3008` on both Thumb targets, including the bypassed first cell and the final binade cell. Each of the four fresh QEMU runs covered 8,388,608 words with zero mismatches. The historical disassembly shows two literal loads plus mask and compare for the new guard. The witness `0x3b859800` and its negative benefit, while existing fast calls pay extra instructions. Thumbv6-M grows by eight bytes and regresses on both paired seeds. [Fresh shard logs](logs/) · [Disassembly](../../trials/m0-tanh-refine/thumb-disassembly.txt) · [Instruction witnesses](../../trials/m0-tanh-refine/thumb-witness.stdout)

## Paired scoring and original selection

I recomputed the weighted instruction means, hard-tail factor, size factor, per-target S and overall from the raw class statistics. Each paired row has matching seed-specific input SHA-256 and hard-pool metadata across the control and all eight trials. Each logged target/seed checks 12,900 scored outputs and 98,304 stratified samples, and every packet has the 134,217,728-word quick GCC check per function and seed. Stage-form measurements and full evaluator outputs enter the same absolute-S comparison. Incumbent remeasurement timeouts are preserved as unscored attempts. Empty local-board takeover labels in successful evaluator logs carry no same-seed live comparison. [Full ledger](ledger.json) · [Control packet](../../trials/paired-control/packet.json)

| Trial | Seed | RV32IM S (ratio) | Thumbv6-M S (ratio) | Overall S (ratio) |
|---|---:|---:|---:|---:|
| id50 paired control | 1874435642 | 28.522714 (1.000000) | 40.515261 (1.000000) | 33.994194 (1.000000) |
| id50 paired control | 1947282751 | 28.517414 (1.000000) | 40.303039 (1.000000) | 33.901895 (1.000000) |
| m0-exp-layout | 1874435642 | 28.522714 (1.000000) | 42.118337 (1.039567) | 34.660198 (1.019592) |
| m0-exp-layout | 1947282751 | 28.517414 (1.000000) | 41.903767 (1.039717) | 34.568585 (1.019665) |
| m0-exp-reduction | 1874435642 | 28.522714 (1.000000) | 41.117854 (1.014873) | 34.246062 (1.007409) |
| m0-exp-reduction | 1947282751 | 28.517414 (1.000000) | 40.919484 (1.015295) | 34.160180 (1.007619) |
| m0-sigmoid-cell | 1874435642 | 28.522714 (1.000000) | 42.187310 (1.041270) | 34.688565 (1.020426) |
| m0-sigmoid-cell | 1947282751 | 28.517414 (1.000000) | 41.979863 (1.041605) | 34.599959 (1.020591) |
| m0-tanh-refine | 1874435642 | 28.522714 (1.000000) | 40.530569 (1.000378) | 34.000615 (1.000189) |
| m0-tanh-refine | 1947282751 | 28.517414 (1.000000) | 40.316224 (1.000327) | 33.907440 (1.000164) |
| rv-exp-interval | 1874435642 | 32.896202 (1.153334) | 40.515261 (1.000000) | 36.507509 (1.073934) |
| rv-exp-interval | 1947282751 | 32.836443 (1.151452) | 40.303039 (1.000000) | 36.378681 (1.073057) |
| rv-exp-loads | 1874435642 | 28.995332 (1.016570) | 40.515261 (1.000000) | 34.274677 (1.008251) |
| rv-exp-loads | 1947282751 | 28.993483 (1.016694) | 40.303039 (1.000000) | 34.183702 (1.008312) |
| rv-tanh-quadratic | 1874435642 | 30.692301 (1.076065) | 40.515261 (1.000000) | 35.263389 (1.037336) |
| rv-tanh-quadratic | 1947282751 | 30.738936 (1.077901) | 40.303039 (1.000000) | 35.197621 (1.038220) |
| shared-small-sigmoid | 1874435642 | 30.745566 (1.077933) | 45.476042 (1.122442) | 37.392334 (1.099962) |
| shared-small-sigmoid | 1947282751 | 30.820392 (1.080757) | 45.345929 (1.125124) | 37.384212 (1.102717) |
| shared-small-sigmoid v2 | 1874435642 | 31.108405 (1.090654) | 43.638988 (1.077100) | 36.844800 (1.083856) |
| shared-small-sigmoid v3 | 1874435642 | 30.912174 (1.083774) | 43.404485 (1.071312) | 36.629592 (1.077525) |

The original rule first minimizes the best board's worse-of-two-seeds ratio, then uses worse-seed overall as the tiebreaker. The seven originally eligible trials all have best-board ratio 1.0. `m0-tanh-refine` wins the tiebreak at 1.000188903 overall. Neither seed has a board gain for any of the eight trials, so the rule triggers no combination. Thumbv7E-M is reported in the ledger for diagnostics and has no scored board.

## Shared-small-sigmoid eligibility discrepancy

The 36 reported target shards are present. Their command records and JSON reports sit in [runlogs](../../trials/shared-small-sigmoid/evidence/runlogs/) and [targetcheck](../../trials/shared-small-sigmoid/evidence/targetcheck/). For each of three ISAs I matched all 12 single-chunk sigmoid reports to exit-zero commands by `--out` basename, function, ISA and exact chunk arguments. The source hash and evaluator identities agree, and all report zero mismatches, 1,048,576 words and completed ranges. The separate three full-host reports also bind to that source and their matching commands. Those target runs cover 12,582,912 sigmoid words per ISA. They do not establish full target coverage.

The original [packet](../../trials/shared-small-sigmoid/packet.json) does not index any of these target or full-host runs. The freeze verifier searches packet-indexed target runs, which explains the original rejection. All 36 target command stdout files are empty because the JSON went to `--out`; the historical command log hashes cannot authenticate those external reports on their own. Each ISA also has 12 distinct reported whole-image hashes and no corresponding retained shard executables for section comparison. The evidence inventory now pins each retained report and command record, with these provenance limits. Counting the external evidence for the original one-target-run eligibility condition leaves the frozen choice unchanged. Shared-small-sigmoid ranks last, with worst-seed ratios 1.080757 RV32IM, 1.125124 Thumbv6-M and 1.102717 overall. The two measure-only variants v2 and v3 regress on both scored targets on seed 1874435642. [Ledger, supplements and variants](ledger.json)

## Episode 5 faults and next experiments

- Fix packet assembly to index correctness commands and the actual bytes of `--out` reports. Store a stable executable section or object digest alongside each reported whole-image hash and preserve the evidence for connecting shards. Keep historical and fresh coverage claims separately identifiable.
- Treat the wide-character selector as a cross-ABI assurance issue. The token gate accepts it, while host sanitizer testing and Thumb target testing cover distinct code paths. Review the inherited byte offsets from table subobjects at `entry.c:2732` and `entry.c:2940` for strict C11 object bounds and audit reachability of incompatible struct views around `entry.c:3230` and `entry.c:3255`. These are source portability concerns. The pinned checks reported zero wrong outputs.
- Use id50 as the public performance baseline. Inspect emitted code before spending a holdout seed. Try a cheaper Thumb typical-path multiply reconstruction or an in-path sigmoid shortcut that avoids adding a prologue test. For the tanh guard, consider a one-test code shape with a cutoff covered by the same certificate. Remeasure one change at a time and retain negative outcomes. A live takeover comparison still needs an authoritative same-input measurement for the current champions.

`python3 eik-work/final-validation/review/verify.py` verifies the retained evidence offline and reruns the integer certificate. It verifies the negative outcome and the evidence gaps. Fresh evaluator commands are separate from this evidence check.

To reproduce the fresh evaluator runs, stage copies of `eik-work/toolkit` and `eik-work/offline-runtime` as siblings under `test/scratch/source-review/restore`. The retained recovery script downloads only the three manifest-pinned omissions into that scratch tree and verifies every whole-file and slice digest. Run the copied `prepare.py` as recorded in the result, then use the recorded isolated commands. The standard-library evidence verifier requires no downloads or restored runtime. [Recovery script](restore-payload.py) · [Staged payload hashes](logs/restored-payloads.json) · [Command records](result.json)
