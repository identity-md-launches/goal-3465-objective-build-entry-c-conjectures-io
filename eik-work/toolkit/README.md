# Offline Exact Integer Kernels baseline toolkit

Run from the repository root on Linux x86-64 with Python 3.12 and pip/venv,
GCC plus libasan/libubsan, and the usual GCC linker and libc headers. Match the
GCC version line in the manifest when reproducing the pinned fingerprints.
[dependencies.json](dependencies.json) records package versions, licenses, and
origins. [files.json](files.json) lists the uploaded toolkit files and their SHA-256
digests, excluding its own digest.
[manifest.json](manifest.json) records the upstream commit and tree, competition
snapshot, verified sources, shared seeds and their exact input digests, and evaluator identities.

The 8 MiB source upload includes the Capstone and pyelftools wheels. The exact
Zig and Unicorn wheels, static QEMU executables, and corresponding QEMU source
archives are staged separately. The default cache is
`test/scratch/eik-dependencies`. Use `--dependencies /path/to/cache` on
`provision.py`, on `verify.py bootstrap`, and before the work directory on
`run.py` to select a reusable cache. Copy that cache and the toolkit to an offline
machine. The QEMU executables are statically linked.

Run provisioning once on a connected machine with `dpkg-deb`. Every downloaded
asset and both extracted QEMU executables are verified against the manifest.
The mandatory `bootstrap` check can also provision on a cold cache.

```sh
python3 eik-work/toolkit/provision.py --fetch
python3 eik-work/toolkit/verify.py bootstrap --offline
```

The pinned evaluator, reference code, full-domain digests, and hard pools are
under `kit/`. The API responses and request timestamps preserve the distinction
between published S and a challenger-to-reference S ratio. Absolute published S
was absent for the eight manifest entries. Published decisions retained in
`published_ratios` describe their historical references. The live reference
promotions 59, 60, and 61 correspond to submissions 52, 53, and 56. Their source
requests returned HTTP 403, so direct same-seed comparisons to these references
are unavailable from this snapshot.

```sh
t=eik-work/toolkit
w=test/scratch/eik-baseline
c=former-50
src=$t/sources/id50.c

python3 "$t/verify.py" bootstrap --offline
python3 "$t/run.py" "$w" "$c" setup setup
python3 "$t/run.py" "$w" "$c" check check "$src"
```

The runner installs from local, hash-pinned wheels with pip's index disabled and uses a shared
runtime per work directory. Each case gets its own build cache, linked images,
fresh hard pools, local incumbent state, evaluation results, and command logs.
Use separate cases for parallel shards and unique labels within a case. The
runner uses the upstream development mode, which uses bubblewrap if usable.
This environment reported sandbox `none`. Native execution here is intended
for reviewed sources or a suitably isolated environment. The setup command
creates the upstream local incumbent state needed by `evaluate`.

## Two shared-seed baseline evaluations

After a successful static check, run both commands on the shared seeds stored
in the manifest. `--quick` limits any host correctness test triggered by the
evaluation. The scoring input sizes and all-target stratified samples remain
at their pinned full scale. A quick-host result provides sample coverage.

```sh
for seed in $(python3 -c 'import json; print(*json.load(open("eik-work/toolkit/manifest.json"))["shared_seeds"])'); do
  python3 "$t/run.py" "$w" "$c" "evaluate-$seed" evaluate "$src" --quick --json --seed "$seed" || break
done

dir=eik-work/baselines/former-50
python3 "$t/packet.py" id50 "$dir" --logs "$w/cases/$c/logs" \
  --techniques "$techniques"
python3 "$t/verify.py" baseline "$dir"
```

Set `techniques` to the source analysis before assembling the packet. Cover
tables, polynomial degree, range reduction, fast paths, and any target-dependent
preprocessing. The packet keeps the exact S rows and evaluator stdout/stderr,
along with command, exit, elapsed time, and digest records.

For a static rejection, retain the failed `check` and run
`python3 "$t/run.py" "$w" "$c" gate gate "$src"`. Assemble as above with
`--logs`. The verifier requires corroborating gate and static check evidence.
For manifest sources with recorded HTTP failures, run
`python3 "$t/packet.py" current-rv32im eik-work/baselines/current-rv32im`.
No measurements are represented in those packets. Infrastructure errors,
missing seeds, and partial evaluations fail packet verification.

## Same-seed comparison

Set `seed` to one of the manifest seeds. Use each `--champion BOARD=FILE` only
when the corresponding reference bytes are available. The upstream stage
treats omitted boards as unheld. Discard comparison decisions for omitted
boards. For practice, the command below compares against a published former
source and labels the output as a historical comparison.

```sh
python3 "$t/run.py" "$w" "$c" historical-compare compare "$src" --seed "$seed" \
  --champion rv32im="$t/sources/id48.c"
```

## Full sanitizer and target shards

The range is half-open. Chunk `c` covers words `c << 20` through
`((c + 1) << 20) - 1`. Use disjoint ranges spanning `0:4096` for each of
`sigmoid`, `tanh`, and `exp` on the host and each of the three targets. The
sample commands run one chunk on the host and one on each target.

```sh
reports="$w/reports"
mkdir -p "$reports"
python3 "$t/run.py" "$w" host-exp-1016 shard fullcheck "$src" \
  --function exp --chunks 1016:1017 --threads 1 --out "$reports/host-exp-1016.json"
for target in rv32im thumbv6m thumbv7em; do
  python3 "$t/run.py" "$w" "$target-exp-1016" shard targetcheck "$src" \
    --function exp --target "$target" --chunks 1016:1017 --jobs 1 \
    --out "$reports/$target-exp-1016.json"
done
python3 "$t/run.py" "$w" merged verdict merge "$reports"/*.json \
  --require-targets rv32im,thumbv6m,thumbv7em
```

The illustrated merge returns 1 for incomplete coverage. Run the same merge
against the full set of shard reports to get a complete verdict. See
[evidence/throughput.json](evidence/throughput.json) for measured smoke-shard
times. Throughput varies with function, input region, entry, core contention,
and cache state. Allow margin and split longer work into independent shards.

The upstream kit and published former sources are available under MIT or
Apache-2.0 terms, as described in [the rules](kit/RULES.md). For individual
dependency obligations and source distribution details see
[dependencies.json](dependencies.json).
