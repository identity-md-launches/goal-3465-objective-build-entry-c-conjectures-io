# Exhaustive coverage and kit merge

Frozen `entry.c` SHA256: `593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b`. Kit rules SHA256: `d9a56849153fff88e3873f3550035e426b88d6fbcbe064e42c4456819b08352e`.
Verifier fingerprint: `ebbf9d5cac596a718532b34798dc452e4050d6940594005c44f9a729c699c5a8`; measurement fingerprint: `2c8fd1f3a6711f0639685319fb25262b02bfecf4c6589c52cb58928270a46322`.
Pinned kit, references, target flags, populations and checks were unchanged. Python 3.12.3, GCC 13.3.0, Zig 0.17.1/Clang 22.1.8 and pinned QEMU 7.2.22 appear in the retained fingerprint and packet evidence. Every selected report has the same source and fingerprint.

| Runtime | Function | Packet | Selected | Chunks | Inputs | Wrong / sanitizer failures | Raw report SHA256 |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| host | sigmoid | pass | rerun | 4096 | 4294967296 | 0 / 0 | `92412ffe579d985ad25b59a6f207927c914df81dc92b37d315d6552d0341b566` |
| host | tanh | pass | rerun | 4096 | 4294967296 | 0 / 0 | `ac1f2a0101af24a127a02235ac9a24fe45e2a4a3032d01c763e91ea4e00efa31` |
| host | exp | pass | reused | 4096 | 4294967296 | 0 / 0 | `b83b0e0906ee6f0d9b25da40716ef958c373d9abd533cc9f5f465fe598837419` |
| rv32im | sigmoid | pass | rerun | 4096 | 4294967296 | 0 / 0 | `4effa9c942df36068775c851ebf100289d3e049d1e9e41d6198d70a243cc2f7c` |
| rv32im | tanh | pass | rerun | 4096 | 4294967296 | 0 / 0 | `07a8f30902b29f914775b2a72d29e440e8ba1023f36a48603b0ef8c943aa0469` |
| rv32im | exp | incomplete | rerun | 4096 | 4294967296 | 0 / 0 | `7ee303913bb804a71be725d359a32792b0c3c81053ca34306cf20f3e5b4a735f` |
| thumbv6m | sigmoid | incomplete | rerun | 4096 | 4294967296 | 0 / 0 | `4c7f26b18d03ffcda40c91fab24a12d970dbfbc5de2d198d08b4ca2c51a8e629` |
| thumbv6m | tanh | pass | rerun | 4096 | 4294967296 | 0 / 0 | `2d86626a7bfadb917e9f4ec586576469ed01455c1a4acdc15232cac6e9ab0934` |
| thumbv6m | exp | pass | rerun | 4096 | 4294967296 | 0 / 0 | `d48315a8c33657f5be4bc0632b895f56074ad76b3a56451bb0ee8b90e756571f` |
| thumbv7em | sigmoid | pass | rerun | 4096 | 4294967296 | 0 / 0 | `aa25282cb06ff79e23d4a814dad8435cd5aec8dbceb5757560f4a4db92b90b4c` |
| thumbv7em | tanh | pass | rerun | 4096 | 4294967296 | 0 / 0 | `ae671f190d05b1de33d58dba70c2b418f5120343fdf864e996dbc94d47afceec` |
| thumbv7em | exp | pass | rerun | 4096 | 4294967296 | 0 / 0 | `abd7e5222256cecc0863c3ed550e6ec234a6bf2472f9b2147b38894139f13b6c` |

The selected half-open range is `[0,4096)` in each cell. It contains 4,294,967,296 unique inputs. The 12 cells contain 49,152 unique cell/chunk pairs and 51,539,607,552 checked inputs; no selected ranges overlap. Full paths and SHA256 values for packets, records, stdout, stderr, target checker images, objects and fingerprint evidence are in `coverage-matrix.json`.

## Merge

Ran the unchanged pinned kit `eik merge` through `eik-work/toolkit/run.py` with the twelve raw selected reports and `--require-targets rv32im,thumbv6m,thumbv7em`. Exit `0`, stderr empty, raw stdout verdict `passed`; all twelve merger cells report 4096 chunks and 4294967296 words. The exact argv, exit and stream hashes are retained in `merger/selected.json`; `merger/selected.stdout` is the unmodified kit result.

## Evidence selection and limits

- RV32IM exp and Thumbv6-M sigmoid packets were originally incomplete: their historical 2^32-word reports name checker ELF hashes whose images were not retained. Those historical reports are excluded. Fresh unchanged-kit targetchecks on frozen root `entry.c` exited 0 with zero mismatches. Their raw reports, records, linked checker ELFs and candidate objects are retained under `rerun/` and are the selected evidence.
- Host exp reuses the landed historical fullcheck. Its record binds the frozen source, entire range, exit 0 and empty stderr. The original host checker binary and sanitizer library hashes were not retained; that provenance limit remains disclosed by its packet. The other eleven cells use fresh reruns.
- Host tanh alternate shards, RV32IM sigmoid/tanh chunk-0 probes and the Thumbv7em exp smoke probe overlap selected whole-domain reports and are excluded from coverage sums.
- The eight excluded overlap reports and their full hashes are listed under `excluded_overlaps` in the matrix; they are checked but never passed to the merger.
- No uncovered selected chunks, mismatches, sanitizer failures or unresolved cross-source/fingerprint conflicts remain. This is a correctness coverage verdict; it makes no current-champion score or takeover claim.
