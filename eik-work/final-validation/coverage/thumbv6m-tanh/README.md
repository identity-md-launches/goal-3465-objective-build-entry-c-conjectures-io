# Exhaustive Cortex-M0+ tanh audit

The fresh run checked chunks `[0, 4096)`, each containing 1,048,576 consecutive
binary32 input words. The unchanged kit compared the SHA-256 digest of each
chunk of outputs against the pinned tanh reference. The run reported 4,294,967,296
words, zero mismatches, full range completion, and exit 0. The QEMU check
took 149.6 seconds with two workers. The frozen root `entry.c` supplied the
code for the entire run.

## Prior evidence

The prior trial's packet index, command record, stdout and stderr all agree.
Their source hash, fingerprint, exit, verdict, completion flags, range,
mismatch count and word count pass the audit. Its recorded checker hash is
`5b1450e24c8ce9713297edded657f39e10acef465ced58b40e514cdd9f523928`.
The original checker ELF is absent. The retained freeze guest is the scoring
guest, with entry point `eik_batch`, while the exhaustive QEMU harness links
a separate static checker with entry point `_start`. The prior checker hash
differs from both the freeze guest and the rebuilt checker, so the packet
claims zero reused chunks.

## Replay and binary binding

The offline-runtime export omitted two wheels and the QEMU upstream source
archive. The three assets were downloaded from their pinned provenance URLs
into scratch and restored after checking each whole-file and part hash.
The first preparation attempt used a symlink to the toolkit and exited 1
because the preparer requires ordinary files. Preparation succeeded with an
ordinary scratch copy. The command records preserve both exits. It used the
unchanged `prepare.py`, pinned kit and wheel versions, Python 3.12.3, GCC
13.3.0, and the pinned x86-64 QEMU 7.2.22 executable. The replay's evaluator
fingerprints match the trial and freeze fingerprints as emitted.

From the repository root, with the restored bundle at
`test/scratch/thumbv6m-tanh/offline-runtime` and its ordinary toolkit sibling:

```sh
scratch=test/scratch/thumbv6m-tanh
python3.12 "$scratch/offline-runtime/prepare.py" "$scratch/dependencies"
python3.12 eik-work/toolkit/run.py --dependencies "$scratch/dependencies" \
  "$scratch/work" exhaustive targetcheck targetcheck entry.c \
  --function tanh --target thumbv6m --chunks 0:4096 --jobs 2
```

The exact linked checker from that run is retained in
`raw/target-check-thumbv6m.elf`. Its whole-file hash matches the report's
`image_sha256`. The packet also retains the compiled submission object and
a scoring guest linked from that same build cache using the kit's
`guest_image` function. Compared with the freeze object and scoring guest,
the rebuilt files have equal program headers, entry addresses and section
inventories. All section data and attributes agree outside DWARF metadata,
including allocatable and executable sections, symbol tables and runtime
relocations. The differing sections carry debug path strings, line tables
and associated DWARF metadata for the rebuilt paths. This comparison
concerns the object and scoring guest. The exact checker hash provides the
binding for the fresh exhaustive run.

`coverage.json` selects the single rerun report. `result.json` records
commands, exits, identities and artifact hashes. Run the offline integrity
check from the repository root:

```sh
python3 eik-work/final-validation/coverage/thumbv6m-tanh/verify.py
```

The integrity check audits retained evidence with the Python standard library.
The exhaustive computation requires the prepared runtime. This packet covers
only the thumbv6m object-code execution of tanh.
