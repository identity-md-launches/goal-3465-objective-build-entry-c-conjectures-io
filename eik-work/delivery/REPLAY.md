# Offline verification and evaluator replay

From the repository root, Python 3.12 on Linux x86-64:

```sh
python3 -B eik-work/delivery/verify.py
```

This checks evidence entirely offline using the standard library. It never installs dependencies, reaches the network, compiles C, executes retained binaries or updates evidence. It independently recomputes raw-score arithmetic and validates the complete/null current fields, source equality, cited file hashes, coverage and claims. It also reruns the seven pinned landed evidence verifiers. A zero exit means this negative fallback package is internally consistent, not that the competition objective succeeded.

## Fresh evaluator replay: currently blocked by the reduced committed runtime

The exact three omitted payloads are listed with byte sizes, whole hashes and original slice hashes in [runtime manifest](../offline-runtime/manifest.json). The committed reduced export's prepare exits 1. The following commands are the pinned offline replay route **after those exact payloads have been restored as ordinary files** and Linux build tools, Python 3.12, GCC ASan/UBSan and libc development headers are available. They are not claimed to run successfully from the current export alone.

```sh
python3 -B eik-work/offline-runtime/prepare.py test/scratch/delivery-replay/deps
python3 -B eik-work/toolkit/verify.py bootstrap --offline --dependencies test/scratch/delivery-replay/deps
python3 -B eik-work/toolkit/run.py --dependencies test/scratch/delivery-replay/deps test/scratch/delivery-replay/work frozen setup setup
python3 -B eik-work/toolkit/run.py --dependencies test/scratch/delivery-replay/deps test/scratch/delivery-replay/work frozen check check entry.c
python3 -B eik-work/toolkit/run.py --dependencies test/scratch/delivery-replay/deps test/scratch/delivery-replay/work frozen fingerprint fingerprint --details
```

For each seed `849230117`, `2715043869`, `396172055`, use a fresh case with unchanged hardscan and score populations, pairing the two files:

```sh
for seed in 849230117 2715043869 396172055; do
  python3 -B eik-work/toolkit/run.py --dependencies test/scratch/delivery-replay/deps test/scratch/delivery-replay/work "pair-$seed" "candidate-$seed" measure entry.c --seed "$seed"
  python3 -B eik-work/toolkit/run.py --dependencies test/scratch/delivery-replay/deps test/scratch/delivery-replay/work "pair-$seed" "id50-$seed" measure eik-work/baselines/former-50/entry.c --seed "$seed"
  python3 -B eik-work/toolkit/run.py --dependencies test/scratch/delivery-replay/deps test/scratch/delivery-replay/work "pair-$seed" "evaluate-$seed" evaluate entry.c --quick --json --seed "$seed"
done
for fn in sigmoid tanh exp; do
  python3 -B eik-work/toolkit/run.py --dependencies test/scratch/delivery-replay/deps test/scratch/delivery-replay/work frozen "host-$fn" fullcheck entry.c --function "$fn" --chunks 0:4096 --jobs 2
  for target in rv32im thumbv6m thumbv7em; do
    python3 -B eik-work/toolkit/run.py --dependencies test/scratch/delivery-replay/deps test/scratch/delivery-replay/work frozen "$target-$fn" targetcheck entry.c --function "$fn" --target "$target" --chunks 0:4096 --jobs 2
  done
done
```

Default evaluate compares the kit incumbent, not a live champion. Preserve that label and any timeout. Remeasure current champions only if their exact bytes or an authoritative same-input measurement become available; do not substitute id50. Use the selected reports in [matrix](../final-validation/merged/coverage-matrix.json) and the exact `eik merge --require-targets rv32im,thumbv6m,thumbv7em` argv in [merge record](../final-validation/merged/merger/selected.json) to replay aggregation without rerunning kernels. The raw reports remain local and hash-bound.

To regenerate delivery projections only, run `python3 -B eik-work/delivery/assemble.py` (no network, no candidate/evidence edits). This intentionally rebuilds its own manifest after running evidence verifiers; ordinary verification never regenerates expected hashes. `refresh.py` is the separate explicit public GET utility and was run once during packaging. Do not rerun it when replaying the frozen evidence package.
