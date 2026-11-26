# Reproduction

Run from the repository root. Use a new scratch work directory so that no
compiled image, local incumbent state, result, or hard-pool file is inherited
from another source. The commands below show the paths used for this packet;
choose a new scratch directory when replaying them because labels are immutable.

```sh
python3 eik-work/toolkit/provision.py --fetch
python3 eik-work/toolkit/verify.py bootstrap --offline
python3 eik-work/toolkit/run.py test/scratch/former-42/work former-42 setup setup
python3 eik-work/toolkit/run.py test/scratch/former-42/work former-42 check check eik-work/baselines/former-42/entry.c
python3 eik-work/toolkit/run.py test/scratch/former-42/work former-42 fingerprint fingerprint --details
python3 eik-work/toolkit/run.py test/scratch/former-42/work former-42 evaluate-180434352 evaluate eik-work/baselines/former-42/entry.c --quick --json --seed 180434352
python3 eik-work/toolkit/run.py test/scratch/former-42/work former-42 evaluate-2851275305 evaluate eik-work/baselines/former-42/entry.c --quick --json --seed 2851275305
python3 eik-work/toolkit/verify.py baseline eik-work/baselines/former-42
```

`commands.json` contains evaluator argument vectors, exit codes, elapsed wall
seconds and stdout/stderr hashes. `workflow-commands.json` records the outer
provisioning, bootstrap, packet assembly and final verification steps. Empty
stderr files are intentional retained logs. `fingerprint.stdout` retains full
verifier and measurement component identities. `object-census.json` was read
from the exact entry object files built in the isolated case, using the runtime's
pinned pyelftools package. Its totals must equal the static gate's charged bytes.

The scoring settings were not overridden: 2,000 typical, 1,000 wide, 300 hard,
and 1,000 uniform inputs per function; 32,768 stratified target words per
function; fresh 2^26-sample hard scans at threshold -18. There are two distinct
seed input digests and six retained hard-pool files. `--quick` affects host
correctness coverage, not these scoring or target-sample sizes.

The isolated case uses the runner's default development execution mode. The
runtime/dependency cache remains ordinary files in `test/scratch`, with no
submodules. Source and report files are delivered in this directory; dependencies
and build outputs are not submitted. Replay requires the immutable toolkit plus
its staged offline dependencies. No registration, signing or submission command
was run.
