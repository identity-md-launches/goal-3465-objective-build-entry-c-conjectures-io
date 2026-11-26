# current-rv32im baseline availability packet

The setup manifest resolves this selector to **submission 52**, promoted as **59**.
The source hash advertised by the submission metadata is
`12614bf3cd9cac500684f28120361c360e2735914b990ebc8f5049a7d843038d`.
The pinned source request returned HTTP 403 with reason `SOURCE_WITHHELD`.
The public recheck and its timestamp are in `evidence/recheck-requests.json`.
The competition rules withhold current champions' source until they hold no board.

There is no `entry.c`: the response is an error document, not C source.
The historical source identity is preserved without substituting a former champion,
the kit template, or a promotion number for the submission number.
`packet.json` uses the verifier's explicit unavailable-source representation.

| Shared seed | RV32IM S | Thumbv6m S | Overall S | Thumbv7em diagnostic S |
| --- | --- | --- | --- | --- |
| 180434352 | unavailable | unavailable | unavailable | unavailable |
| 2851275305 | unavailable | unavailable | unavailable | unavailable |

Neither seed was measured. No check, sanitizer run, object-code test, target sample,
or hard-pool generation ran for this unavailable source. Size, stack, class means,
tails and mismatches are unknown, not zero. There is no coverage or takeover claim.
The offline runner commands to use once the source is published are recorded as
**not run** in `report.json`; evaluator and reference settings remain unchanged.

The API did not advertise absolute S. It did advertise historical ratios for
submission 52: RV32IM 0.9663356577371272 against promotion 53 (evaluation 154),
Thumbv6m 1.0 against promotion 57 (evaluation 155), and overall
0.9953888317067958 against promotion 58 (evaluation 156). These have different
historical references and are not local scores or live-board comparison evidence.

All six requested technique categories are explicitly unknown in `report.json`:
tables, polynomial degrees, range reduction, fast paths, hard cases and target
macros. The source cannot be analyzed from a hash or withheld-source error.
`experiments` contains two conditional proposals for when the bytes are published:
replace a costly exp range selector with a reciprocal multiply and correction,
and introduce certified tiny-input returns where absent. Neither was implemented
or measured. No source was optimized.

`evidence/` retains the original board/reference/submission/source-error JSON,
timestamped request metadata, setup manifest, public rechecks and toolkit integrity
hashes. `logs/` and `commands.json` retain command stdout/stderr and exit codes.
The toolkit is unchanged. No submission, signing, registration or credential
operation was performed.

Reproduce the packet validation from the repository root:

```sh
python3 eik-work/toolkit/verify.py baseline eik-work/baselines/current-rv32im
```

A passing packet verifier means that unavailability is documented consistently
with the manifest. It does not mean that any kernel measurement passed.
