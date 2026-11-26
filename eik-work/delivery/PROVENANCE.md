# Source, tool and reference provenance

All cited files are repository-local and SHA256-inventoried in [manifest.json](manifest.json); no external download is required to inspect or verify this evidence. Existing raw files were not edited or substituted.

| Material | Repository source |
| --- | --- |
| Frozen source and original selection | `entry.c`, `eik-work/freeze/manifest.json`, `eik-work/freeze/experiments.md` |
| Exact delivered source | `eik-work/delivery/entry.c` (same SHA256 and bytes as root) |
| Public base id50 and older sources | `eik-work/baselines/former-50/entry.c`, `eik-work/final-validation/boards/references/`, `eik-work/toolkit/sources/` |
| Published metadata and withheld responses | `eik-work/final-validation/boards/raw/`, `eik-work/delivery/public-refresh/` |
| Competition kit | `eik-work/toolkit/manifest.json`, commit `5a32428ad4aa23bce737d50a738ace24ddeeed2e`, `files.json` |
| Fully read competition rules | `eik-work/toolkit/kit/RULES.md`, SHA256 `d9a56849153fff88e3873f3550035e426b88d6fbcbe064e42c4456819b08352e` |
| Measurement/verifier/compiler/reference pins | `eik-work/final-validation/review/logs/fingerprint.stdout`, `eik-work/toolkit/dependencies.json` |
| Independent source and rounding review | `eik-work/final-validation/review/review.md`, `result.json`, `ledger.json`, `logs/` |
| Selected exhaustive reports and actual target checker ELFs | `eik-work/final-validation/merged/coverage-matrix.json` and its cited paths |
| All three fresh score packets | `eik-work/final-validation/scores/heldout-{1,2,3}/` |
| Reduced committed runtime and licences | `eik-work/offline-runtime/manifest.json`, `parts/`, `README.md` |

Kit origin: https://github.com/conjectures-io/exact-integer-kernels-miner . Public board API: https://conjectures.io/v1/competitions/exact-integer-kernels/boards . Former sources: `/submissions/{37,42,46,48,50}/source` under the same competition API. The landed board snapshot validates published bytes against declared source digests. Current sources 52, 53, 56 are withheld; their declared hashes are not treated as downloaded source bytes.

Recorded evaluator platform: Linux x86-64, Python 3.12.3, GCC 13.3.0, Zig 0.17.1 / Clang 22.1.8, QEMU 7.2.22. The exact measurement fingerprint is `2c8fd1f3a6711f0639685319fb25262b02bfecf4c6589c52cb58928270a46322`; verifier fingerprint `ebbf9d5cac596a718532b34798dc452e4050d6940594005c44f9a729c699c5a8`. Flags, target triples, compiler helpers, reference digests, hardscan threshold, set sizes and score weights are unchanged and retained in that fingerprint. The manifest inventories ordinary retained payload parts; it does not assert that the omitted wheels/source archive exist.

The inventory deliberately references the full repository-local evidence tree rather than copying raw logs. It includes all trials and variants, failed/timeout command logs, runtime notices, pinned kit and reference data. Only the delivery directory is new. `manifest.json` does not hash itself; the verifier hashes every listed file and pins the authoritative evidence roots independently. The named goal result is an upload output outside this inventory and makes no additional competition claim.
