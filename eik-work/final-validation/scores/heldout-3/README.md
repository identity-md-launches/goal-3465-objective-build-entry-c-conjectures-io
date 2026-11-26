# Held-out comparison for seed 396172055

Run `python3 eik-work/final-validation/scores/heldout-3/verify.py` from the repository root. The verifier uses the Python standard library and reads pinned repository inputs and retained evidence. `scores.json` carries full-precision scores. `scores.md` presents the board comparison. `result.json` indexes the raw reports, input pools, command records and identities.

The offline runtime export omitted three pinned assets. The measurement restored those assets from their pinned URLs in scratch, validated the raw slices, reconstructed the offline runtime, and ran bootstrap and setup. `restore_payloads.py` reproduces the download and slice verification. The evaluator ran with Linux x86-64, Python 3.12, GCC, the complete configured input populations, fresh hard scans and 32,768 sampled words per function per target. The repository sources stayed frozen.

The local evaluate invocation used the unchanged module entry point via `runpy`. The wrapper observed the start and finish of the two kit incumbent scoring jobs and armed a 600-second cap for that phase. Separate measurements keep target samples enabled on both entries, and separate quick fullchecks cover the candidate's three functions. The status and measured outcome of each stage are recorded in the packet.

The completed board snapshot shows three HTTP 403 source responses. The current-board columns and eligibility reflect that missing evidence. Former id50 is the historical denominator for the paired results. An overall ratio uses each source's own two scored targets.

For a fresh replay, use an empty `test/scratch/heldout-3` and run these commands from the repository root. Collection writes into this packet's raw directory, so replay in a separate checkout to preserve the recorded evidence.

```sh
s=test/scratch/heldout-3
raw=eik-work/final-validation/scores/heldout-3/raw
mkdir -p "$s" "$raw"
cp -a eik-work/offline-runtime eik-work/toolkit "$s/"
python3 eik-work/final-validation/scores/heldout-3/restore_payloads.py
python3 "$s/offline-runtime/prepare.py" "$s/deps" > "$raw/prepare.stdout" 2> "$raw/prepare.stderr"
printf '%s\n' "$?" > "$raw/prepare.exit"
PYTHONDONTWRITEBYTECODE=1 python3 eik-work/toolkit/verify.py bootstrap --offline \
  --dependencies "$s/deps" > "$raw/bootstrap.stdout" 2> "$raw/bootstrap.stderr"
printf '%s\n' "$?" > "$raw/bootstrap.exit"
python3 eik-work/toolkit/run.py --dependencies "$s/deps" "$s/work" heldout setup setup
python3 eik-work/final-validation/scores/heldout-3/collect.py
```
