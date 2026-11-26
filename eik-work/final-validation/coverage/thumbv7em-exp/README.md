# thumbv7em / exp exhaustive targetcheck coverage

Status: **pass**, from a fresh rerun. The prior run was audited but not reused.

- Source: root `entry.c`, sha256 `593e2420…c5f6b`, the frozen source.
- Selected set: `reports/rerun/targetcheck-thumbv7em-exp-all.*`. This is the unchanged `toolkit/run.py`
  running `targetcheck entry.c --function exp --target thumbv7em --chunks 0:4096 --jobs 2`.
  It exited 0 with verdict `passed`, complete and range_complete, 4294967296 words and 0 mismatches.
  The fingerprint has measurement `2c8fd1f3…` and verifier `ebbf9d5c…`. Its `--details` content is identical to the prior packet's fingerprint.
- Image binding: `image_sha256` e58cc8f3… is the sha256 of the retained `objects/target-check-thumbv7em.elf`.
  `objects/sub-thumbv7em.o` is retained next to it. Both embed absolute build paths from this machine.
- Prior evidence: `eik-work/trials/m0-tanh-refine/targetcheck-thumbv7em-exp-all.*` matches its packet.json
  hashes, command, source, fingerprint, exit, verdict and flags, with 0 mismatches over 2^32 words in [0,4096).
  Its image 1636778c… is not retained. It differs from the frozen `guest-thumbv7em.elf` and from the rerun image.
  No coverage is credited from it.
- Runtime: running `offline-runtime/prepare.py` on the export exits 1 because three payloads are omitted.
  Those three files were downloaded from their pinned URLs and matched the pinned sha256. They were restored as raw
  slices into a byte-identical scratch copy of offline-runtime and toolkit, and the unchanged prepare.py then
  reconstructed and verified all 33 pinned files.
- Host GCC: this host has no system gcc and `/usr` is read-only. The pinned Ubuntu gcc-13 13.3.0-6ubuntu2~24.04.1 was
  extracted from .debs (`host-gcc/`) and put on the runner PATH through the dependency `qemu/bin` directory.
  The kit's confined policy-preprocessing step uses PATH=/usr/bin:/bin, so `bootstrap` and `setup` exit 1 at that step.
  targetcheck does not use that step. It compares the target image against the pinned `exp.digest`.

Verify offline with `python3 eik-work/final-validation/coverage/thumbv7em-exp/verify.py`.
