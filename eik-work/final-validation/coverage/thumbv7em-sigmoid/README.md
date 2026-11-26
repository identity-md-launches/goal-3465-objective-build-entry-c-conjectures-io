# Thumbv7em sigmoid exhaustive coverage

The fresh pinned-kit run covered chunks `[0,4096)` and unsigned input words
`[0,4294967296)` in QEMU with two jobs. It completed in 106.6 seconds with
zero mismatches against the pinned sigmoid digests. The selected report and
runner record are under `logs/exhaustive.*`. The report's image hash is the
SHA-256 of `objects/target-check-thumbv7em.elf`, the static QEMU checker with
entry `_start`. The same case cache supplied the retained submission object
to the checker link and to the separate scoring guest link.

The trial packet independently indexes the historical report, runner record
and stderr by SHA-256. The raw hashes, command, source, fingerprint, exit,
completion flags and counts agree. Its checker hash is
`1636778c87b4e1961744cd6456297b5daf81d090910398dab1cd15004b403e3a`.
The original checker and historical runtime are absent from the retained
evidence. The freeze guest has entry `eik_batch` and serves a different link
purpose. The historical report contributes zero chunks to this packet.

The rebuilt object and scoring guest match the frozen counterparts in
allocated section bytes and addresses, program headers and loaded bytes
(excluding the ELF header's section-table offset), function symbols and
non-debug relocations. Changed section payloads are limited to DWARF
`.debug_info`, `.debug_str`, `.debug_line` and the object's
`.rel.debug_line`. The DWARF string differences are workspace paths for
the source, compilation directory and guest harness. Path lengths change
debug string and line table offsets, as well as the ELF section-table offset.
The historical exhaustive report is separate from this frozen-guest comparison.

## Runtime and replay

The first invocation of the landed `offline-runtime/prepare.py` reported
three omitted payloads. A scratch copy of that bundle was restored from
the manifest URLs for the exact Zig and Unicorn wheels and QEMU source
archive, checking every part and aggregate hash. Unchanged `prepare.py`
then reconstructed and verified all 33 pinned files. The runner verified
the staged QEMU executables and installed the hash-pinned wheels. Linux
x86-64, Python 3.12.3, GCC 13.3.0, the QEMU executable hash and tool fingerprint
are recorded separately from the exhaustive report. Scratch downloads are
needed to replay the run from the reduced export. Packet verification uses
only the evidence in the repository and the Python standard library.

The working directory for outer commands was the repository root. The
command arrays and exits are in `result.json`. The scratch restoration used
copies of `eik-work/offline-runtime`, `eik-work/toolkit` and this packet's
`restore.py` in `test/scratch/thumbv7em-sigmoid/`. The nested runner records
contain the evaluated commands and raw stream hashes. The scoring guest
helper was run with the case environment recorded in `result.json`.

```sh
python3 eik-work/final-validation/coverage/thumbv7em-sigmoid/verify.py
```
