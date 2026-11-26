# thumbv6m / exp exhaustive coverage packet

Independently audited coverage of `eik_exp` on the Cortex-M0+ (`thumbv6m`) target
for the frozen root `entry.c`
(SHA-256 `593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b`).

Check: `python3 eik-work/final-validation/coverage/thumbv6m-exp/verify.py` (standard library only, offline).

## Outcome

`status: pass`. Every one of the 4294967296 binary32 bit patterns was run through the
entry's thumbv6m object code in QEMU user mode and matched the pinned reference
digests: chunks `[0,4096)` (half-open; chunk `c` is words `[c<<20, (c+1)<<20)`),
0 mismatches, exit 0, verdict `passed`, `complete` and `range_complete` true.

## What was audited (prior evidence)

`eik-work/trials/m0-tanh-refine/targetcheck-thumbv6m-exp-all.{json,stdout,stderr}`,
indexed by `packet.json` run `targetcheck-thumbv6m-exp-all`:

- raw file hashes match the packet index; stdout bytes match the run record;
- the record binds the frozen source and the command `targetcheck ... --function exp --target thumbv6m --jobs 1`;
- the report has the pinned fingerprint, exit 0, verdict passed, 0 mismatches, 4294967296 words, chunks [0,4096);
- **not bound**: `image_sha256 77bdc033…2bb29` is the whole-file hash of `target-check-thumbv6m.elf`
  from a scratch case that was never retained. No retained file has that hash. The frozen
  `guest-thumbv6m.elf` is a different link product (different harness, entry `eik_batch`),
  so it can never match; matching C-source hashes alone cannot prove image identity.

The prior report is therefore kept as a separate set (`sets.prior`), `counted: false`,
and contributes no coverage.

## What was rerun (selected set)

The reduced `eik-work/offline-runtime` export omits three payloads (ziglang and unicorn
wheels, QEMU upstream source). They were fetched from the pinned URLs in
`eik-work/toolkit/dependencies.json`, verified against the pinned SHA-256 values, sliced
into the 4 MiB parts recorded in `offline-runtime/manifest.json` (every part hash matched)
inside a scratch copy of the export, and `prepare.py` then reconstructed all 33 pinned
files (`logs/prepare.stdout`). `eik-work/toolkit/run.py` was used unchanged:

```
python3 eik-work/toolkit/run.py --dependencies test/scratch/eik-dependencies test/scratch/final-thumbv6m-exp cov fingerprint fingerprint
python3 eik-work/toolkit/run.py --dependencies test/scratch/eik-dependencies test/scratch/final-thumbv6m-exp cov targetcheck-thumbv6m-exp-0-4096 targetcheck entry.c --function exp --target thumbv6m --chunks 0:4096 --jobs 2
```

Retained in this directory:

- `reports/new/` the run records and raw reports (stdout is the kit report, bound by `stdout_sha256`);
- `objects/target-check-thumbv6m.elf` the linked image whose SHA-256 **is** the report's `image_sha256`;
- `objects/sub-thumbv6m.o` the entry object linked into it;
- `logs/` prepare output and the runtime install log (pinned wheel hashes, import probe).

Identity established before reuse/rerun: frozen source (root and trial `entry.c` identical),
pinned fingerprint (`verifier`/`measurement` equal to `eik-work/freeze/manifest.json`),
pinned `qemu-arm` 7.2.22 (hash in `dependencies.json`, checked by `run.py` before the run),
toolkit identity files hashed in `coverage.json`.

Image binding: `verify.py` parses the ELF itself, checks the entry point is the `_start`
symbol inside `.text`, that `eik_sigmoid`/`eik_tanh`/`eik_exp` are global functions in `.text`
with the same sizes as in the object, hashes every allocated section, and compares the
object's allocated sections (`.text`, `.rodata*`, `.ARM.exidx`) with the frozen build's
`sub-thumbv6m.o` recorded in `eik-work/freeze/manifest.json`: byte-identical. Whole-file
hashes differ only through non-allocated debug/metadata that embeds the build path.

## Files

- `result.json` status, identities, commands/exits, measured facts, gaps, artifact hashes
- `coverage.json` function/runtime, exact ranges/counts, reused/rerun provenance, identities, failures/gaps, hashed raw paths
- `verify.py` offline verifier (rejects gaps, overlaps, tampered evidence, unbound images, unsupported pass)
