# rv32im / tanh exhaustive target coverage

**Status: pass.** All 2^32 binary32 inputs of `eik_tanh` from the frozen root `entry.c`
(SHA-256 `593e2420…0c5f6b`) were checked on rv32im object code under QEMU user mode against the
pinned reference digests. Chunks `[0, 4096)` were covered, 4294967296 words, 0 mismatches,
verdict `passed`. The verifier fingerprint was `ebbf9d5c…`, the measurement fingerprint `2c8fd1f3…`
and the sandbox `none`. These match `eik-work/toolkit/manifest.json` exactly.

Verify offline from the repository root:

```sh
python3 eik-work/final-validation/coverage/rv32im-tanh/verify.py
```

## Prior evidence (audited, not reused)

The prior record is `eik-work/trials/m0-tanh-refine/targetcheck-rv32im-tanh-all.{json,stdout,stderr}`,
indexed by `packet.json`. The audit found the following:

- The raw hashes match the packet. Exit 0 and stderr is empty.
- The argv targets the frozen source: `targetcheck …/entry.c --function tanh --target rv32im --jobs 1`.
- The fingerprint is identical to the pin.
- The report says `complete`/`range_complete` true, `[0,4096)`, 4294967296 words, 0 mismatches,
  verdict passed.

It recorded `image_sha256 4c46aa4f…`. That image was linked under a deleted scratch directory and no
image, object or guest file was kept. It cannot be bound to bytes, and equivalence cannot be proven.
The prior coverage is therefore **not** counted. The rerun below is the only selected set. Old and
new reports stay in separate places.

## Rerun (selected set)

1. **Prepare.** `python3 eik-work/offline-runtime/prepare.py` exited 1 (`host/prepare.stderr`).
   The landed reduced export lacks the unicorn and ziglang wheels and the QEMU orig source. I used
   `python3 eik-work/toolkit/provision.py --fetch --dependencies test/scratch/deps` instead
   (`host/provision.stdout`). It verifies every payload against the toolkit pins.
2. **GCC.** This host had no `gcc`. The fingerprint hashes the host_cc `--version` line, so I
   unpacked the exact pinned Ubuntu `gcc-13 13.3.0-6ubuntu2~24.04.1` packages in scratch. Each was
   checked against the SHA-512 in the apt index (`host/gcc-debs-uris.txt`). They are reached as `gcc`
   through `host/gcc-wrapper.sh`, placed on the runner's PATH directory. Its `--version` line equals
   the pin, and the fingerprint details equal the manifest byte for byte. The rv32im targetcheck
   compiles only with zig/clang and runs QEMU.
3. **Targetcheck.** `python3 eik-work/toolkit/run.py --dependencies test/scratch/deps test/scratch/rvtanh rv32im-tanh targetcheck-rv32im-tanh-all targetcheck entry.c --function tanh --target rv32im --chunks 0:4096 --jobs 2`
   used the unchanged runner and exited 0 in 82 s (`rerun/logs/`).
4. **Image binding.** `rerun/objects/target-check-rv32im.elf` is the exact image that ran. Its
   SHA-256 equals the report's `image_sha256` (`06c856b3…`). The entry's object `sub-rv32im.o` is
   also kept, along with zig's `entry.o`, `guest.o` and `target_check.o`. `compiler_rt_zcu.o` is
   recorded by digest only.
5. **Reproduction probes.** Two more cases (`repro-root` with root `entry.c`, `repro-trials` with
   the trials copy) each ran chunk 0:1 and passed. They do not count toward coverage. Their image
   hashes differ (`61bd676b…`, `d9c6b392…`), but the differences are only path-bearing metadata:
   - `.debug_*`
   - `.symtab`
   - the ELF header fields that locate the section-header table
   - non-load program-header `p_offset`

   Everything that determines execution is equal: load segments (addresses, sizes, flags, bytes),
   alloc sections, the entry point (`_start`), the kernel symbol addresses and the alloc relocations.
   `elfcheck.py` computes this and `verify.py` recomputes it.

## Failures and limitations

- **`verify.py bootstrap --offline` and `run.py setup` both exited 1.** They compile with gcc under a
  fixed `/usr/bin:/bin` PATH, where this host has no gcc. Neither is used by `targetcheck`.
- **No gaps in the claimed range.**
