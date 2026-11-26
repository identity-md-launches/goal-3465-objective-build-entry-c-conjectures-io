# thumbv7em / tanh exhaustive target coverage

Status: **pass**. A fresh whole-domain run of `targetcheck` on the root `entry.c`
(sha256 `593e2420...c5f6b`) covered chunks `[0,4096)` (4294967296 words) with 0 mismatches.
It reported verdict `passed` and exited 0 in 47 s. Its `image_sha256` (`afcd03fa...`) equals the
sha256 of the retained linked image `new/objects/target-check-thumbv7em.elf`.

- `coverage.json`: ranges, counts, provenance, identities, the prior audit, gaps and failures (none), and hashes of every artifact.
- `result.json`: status, commands and exits, measured facts, identities and artifact hashes.
- `new/`: the logs from prepare, bootstrap, setup, fingerprint and targetcheck, plus `install.log`, the report, the linked image and the object.
- `prior/`: copies of `eik-work/trials/m0-tanh-refine/targetcheck-thumbv7em-all.*` and `packet.json`.
  The audit passed: hashes match the packet index, exit 0, verdict passed, the run was complete, 0 mismatches and 2^32 words.
  These files are **not credited** because their image `e1896022...` is not retained and the frozen guest ELF has a different hash.
- `verify.py`: an offline check that uses only the standard library. Run it with `python3 eik-work/final-validation/coverage/thumbv7em-tanh/verify.py`.

How the run was reproduced: the exported `offline-runtime` leaves out three pinned payloads: the QEMU orig tarball, the Unicorn wheel and the Zig wheel.
They were downloaded from the pinned URLs and each matched its pinned sha256.
They were split into the manifest's 4 MiB parts inside a scratch copy of `eik-work/offline-runtime`.
That copy's `prepare.py` is byte-identical to the original.
`verify.py bootstrap --offline` passed. `toolkit/run.py` was used unchanged with
`targetcheck entry.c --function tanh --target thumbv7em --chunks 0:4096 --jobs 2`.
