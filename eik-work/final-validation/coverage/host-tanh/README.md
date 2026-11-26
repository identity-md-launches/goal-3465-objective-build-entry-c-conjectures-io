# host/tanh exhaustive coverage packet

Status: **pass**. The frozen root `entry.c`
(sha256 `593e2420…0c5f6b`) was checked with the pinned kit's GCC ASan+UBSan `fullcheck`
for `tanh` on every binary32 word: half-open chunks [0,4096), 4294967296 words, zero mismatches,
zero sanitizer errors, no `--quick`. The selected set is `rerun-whole` (one run of
`toolkit/run.py … fullcheck entry.c --function tanh --chunks 0:4096 --threads 2`, exit 0, 257 s).

- `coverage.json` lists the ranges, counts, provenance, identities, failures/gaps and hashed raw reports.
- `result.json` summarises the status, tool identities, commands with their exits, and the measured facts.
- `verify.py` re-validates everything offline: `python3 eik-work/final-validation/coverage/host-tanh/verify.py`.
- `rerun/whole/` holds the selected run's record, its stdout report and stderr, and the check binary and sanitizer object.
- `rerun/session/` holds setup, fingerprint (verifier `ebbf9d5c…`, measurement `2c8fd1f3…`, matching the
  toolkit manifest pins), the static check and the runtime install log.
- `alt-shards/` holds a separate, non-selected corroborating set: four disjoint 1024-chunk shards, all passed.
- `negative-controls/` holds copies of the entry with an injected signed overflow (UBSan) and an out-of-bounds
  table read. The fullcheck rejected both at `fullcheck:sanitizer`, which shows that the sanitizer pipeline reports errors.
- Prior evidence (`eik-work/trials/m0-tanh-refine/exhaustive-tanh.*`) was audited: its hashes match
  packet.json, it uses the same source and fingerprint, and it is complete with zero mismatches. It is not
  selected, because it persists no compiler/sanitizer-runtime binding.

Host notes: this host had no GCC. The pinned Ubuntu gcc-13 13.3.0-6ubuntu2~24.04.1 packages
(`toolchain/gcc-debs.sha256`) were unpacked into scratch. They were selected through the kit's own
`EIK_HOST_CC` setting, which a `.pth` file in the scratch runtime sets, using a wrapper that adds an rpath
for the sanitizer runtimes (`toolchain/`). `run.py`, the kit, the flags and the populations are unchanged.
`offline-runtime/prepare.py` fails because the landed export lacks three payloads, so dependencies came from
`toolkit/provision.py --fetch` with pin verification. `toolkit/verify.py bootstrap` exits 1 on this host
because its fresh venv cannot find gcc. The pinned identity is shown instead by the fingerprint log.
