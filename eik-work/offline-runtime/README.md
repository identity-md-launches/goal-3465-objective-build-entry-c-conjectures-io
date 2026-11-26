# Offline evaluator runtime evidence

**Export status is incomplete.** The original complete bundle passed a cold
offline replay. The upload check reported 143,261,515 bytes of new work
against its 8,388,608-byte limit. The original upload also exceeds the combined
limit of twelve 8 MiB pieces. The reduced export retains both exact QEMU
executables, Debian patches, capstone, pyelftools, pinned notices and the
historical replay evidence. The exact Zig and Unicorn wheels and the QEMU
upstream source archive remain required. Their pins and original slice hashes
are in `manifest.json`. The reduced export cannot bootstrap downstream checks.

Run the evidence verifier from the repository root with
`python3 eik-work/offline-runtime/verify.py`. It verifies both retained QEMU
executables after XZ decompression, all other retained parts and their
reconstructed digests, and the two sets of replay records. A zero exit on
this export confirms the evidence for the incomplete outcome.

`evidence/` records the original successful isolated run from empty scratch
with Python 3.12 and GCC. It passed toolkit bootstrap and setup, checked the
frozen root entry, and compared exp chunk 1016 (1,048,576 words) using GCC with
ASan and UBSan and each of the three QEMU targets. All four smoke checks
reported zero mismatches. `evidence/reduced-export/` records a second isolated
run from empty scratch that stopped at preparation with exit 1. Bootstrap,
setup, the entry check and smoke checks were consequently unavailable for the
reduced export.

## Replaying with the complete payload set

An export with room for the remaining exact bytes can restore the three
omitted files as ordinary raw slices at the paths and sizes in the manifest.
The retained QEMU binaries are deterministic XZ streams. The original
raw split hashes still apply to their decompressed bytes. Preparation
validates every payload against the toolkit pins and uses no network or
external cache.

On Linux x86-64 with Python 3.12, standard venv support, GCC with ASan and UBSan,
GNU build tools and libc development headers, run from the repository root.
These host prerequisites were installed before the original replay.

```sh
deps=test/scratch/my-eik-dependencies
work=test/scratch/my-eik-work

python3 eik-work/offline-runtime/prepare.py "$deps"
python3 eik-work/toolkit/verify.py bootstrap --offline --dependencies "$deps"
python3 eik-work/toolkit/run.py --dependencies "$deps" "$work" frozen setup setup
python3 eik-work/toolkit/run.py --dependencies "$deps" "$work" frozen check check entry.c
```

Use a new or empty dependency directory. Pass the same
`toolkit/run.py --dependencies DIRECTORY` option before the work directory
for additional commands. The toolkit README documents coverage sharding and
score seeds. With the complete payload set, repeat the cold smoke run using
`python3 eik-work/offline-runtime/replay.py test/scratch/my-cold-replay`.
This command requires unprivileged user and network namespaces.
