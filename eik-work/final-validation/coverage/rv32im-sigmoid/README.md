# rv32im / sigmoid exhaustive target coverage packet

Status: **pass**. A fresh run of `targetcheck` covered `entry.c`
(sha256 `593e2420…0c5f6b`) for `eik_sigmoid` on rv32im over chunks `[0,4096)`.
That is 4,294,967,296 words, 0 mismatches and verdict `passed`, with `complete`
and `range_complete` both true. The run took 121.1 s in the report and exited 0.

- `coverage.json`: the selected range set, its provenance, the image and ELF
  identity, the audit of the prior evidence, and the path-only reproduction.
- `result.json`: the status, source and toolkit identities, the hash of every
  artifact, the commands with their exits, and the measured facts.
- `rerun/`: the kit command logs, the raw report, and the linked image
  `target-check-rv32im.elf`, whose sha256 equals the report's `image_sha256`.
  It also holds the rv32im objects that were built.
- `path-reproduction/`: the same source rebuilt under a different case directory
  (chunk 0:1, passed). The whole-file hash differs and the first LOAD segment
  differs only inside the ELF file header. The cause is absolute build paths in
  the DWARF data. `.text`, `.rodata`, load addresses, entry, symbols and
  relocations are identical.

Prior evidence in `eik-work/trials/m0-tanh-refine/targetcheck-rv32im-sigmoid-all.*`
was audited. The raw hashes match `packet.json`, and the source, fingerprint,
exit 0, passed verdict, flags, 0 mismatches and 2^32 words all check. It was
**not reused**, because the image it recorded (`4c46aa4f…`) was not retained.
The rerun set is the only selected set.

`eik-work/offline-runtime/prepare.py` cannot prepare a runtime from that export,
which omits the Zig and Unicorn wheels and the QEMU source. The same pinned
assets came from the unchanged `toolkit/provision.py --fetch`. That cache passed
`verify.py bootstrap --offline`, and the run used the unchanged `toolkit/run.py`.

Verify offline with `python3 eik-work/final-validation/coverage/rv32im-sigmoid/verify.py`.
