# Paired two-seed control: unchanged id50

Control for the e03 kernel trials: the unchanged former champion id50, linked in place at
[`eik-work/baselines/former-50/entry.c`](../../baselines/former-50/entry.c)
(SHA-256 `88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3`, verified; not copied),
measured with the pinned evaluator through `eik-work/toolkit/run.py` on the two trial seeds
**1874435642** and **1947282751**.

```sh
python3 eik-work/trials/paired-control/verify.py eik-work/trials/paired-control   # this control
python3 eik-work/trials/paired-control/verify.py eik-work/trials/<key>            # a trial
```

## Control scores (absolute S, lower is better)

| seed | inputs_sha256 | rv32im | thumbv6m | overall = √(rv·m0) | thumbv7em (reported only) |
|---|---|---|---|---|---|
| 1874435642 | `1b9ee17dc1c07a9a1364ae327f2c732ed1ae8d14b7ff6ea313d4bc3cb12d6b27` | 28.52271424241966 | 40.515260593492414 | 33.99419362722625 | 39.95633850332885 |
| 1947282751 | `7fe5c5af336d9931b2582e5acd0c08c3e4ee86c07045daa5772d761f0221aa77` | 28.517414314250885 | 40.30303897386101 | 33.90189464529962 | 39.74954420309734 |

These are **absolute S**. No incumbent ratio is printed by these runs (see below). Ratios published by the
API (`published_ratios` in the toolkit manifest) are challenger/reference ratios against other
references, not S.

- Source `sha256` 88617bb4…60c3, `normalised_sha256` `e8722042f89400f887e0e526338d22ae756c029c4646c49c4d290da1bda04db8`.
- Evaluator: verifier `ebbf9d5cac596a718532b34798dc452e4050d6940594005c44f9a729c699c5a8`,
  measurement `2c8fd1f3a6711f0639685319fb25262b02bfecf4c6589c52cb58928270a46322`, both the pinned
  manifest identities (bootstrap passed with no host-compiler note), sandbox `none`.
- Bytes rv32im 18960, thumbv6m 20500, thumbv7em 21254 (size factors 1.135476, 1.145777, 1.150787);
  static stack bound 176 / 312 / 280; measured peak stack rv32im 0 (seed 1874435642) or 8, thumbv6m 60, thumbv7em 40.
- Hard pools (hardscan, 67108864 samples, threshold 2^-18 ulp): seed 1874435642 sigmoid 560, tanh 186,
  exp 445; seed 1947282751 sigmoid 571, tanh 198, exp 408.
- Every target: 2000 typical, 1000 wide, 300 hard, 1000 uniform inputs per function, zero wrong outputs;
  target sample 98304 words (3 × 32768), 0 mismatches. Tail factor 1.0 for every function/target.
  Quick host check: 134217728 words per function per seed, 0 mismatches.
- Per-class means (typical/wide/hard/uniform) and hard p99.9 per target and function are in
  `packet.json` → `index.rows.<seed>.targets.<target>.functions.<fn>`.

## Why stage form instead of `eik evaluate`

`eik evaluate --quick --json --seed S` was run for both seeds and did not finish: it re-measures the
locally registered champion (the ~10^5-instruction incumbent) under a Python block hook, and that
alone exceeds the 10-minute cap on one command on this worker. The attempts are in
`evaluate-attempts.json`. The entry's own numbers come from the same kit stages `evaluate` calls
(`kit/eik/evaluate.py`): `eik measure SRC --seed S` (= the entry half of `compare`, every target, with
the stratified sample) and `eik fullcheck SRC --function FN --quick --seed S` (= `host_check` with the
evaluation seed). S is identical either way; only the printed incumbent ratio is missing.
Trials may use either form; a worker able to finish `evaluate` should use it.

## Packet layout (control and every trial)

One directory per target, `eik-work/trials/<key>/`, flat:

| File | What |
|---|---|
| `packet.json` | the index (below) |
| `<label>.json` | run.py's record: `argv`, `exit_code`, `source_sha256`, `stdout_sha256`, `stderr_sha256`, `seconds` |
| `<label>.stdout`, `<label>.stderr` | raw evaluator output (`$REPO` substituted for the checkout path, as run.py writes it) |
| `entry.c` | trials only: the candidate source (the control links id50 instead) |

Labels: `check`, `gate` (`eik gate SRC`, the static gate with normalised hash), `fingerprint`
(`eik fingerprint --details`), and per seed either `evaluate-<seed>` (`evaluate SRC --quick --json --seed <seed>`)
or `measure-<seed>` + `fullcheck-<seed>-{sigmoid,tanh,exp}`. `setup` and `LABEL@CASE` copies from a second
run.py case are extra evidence.

`packet.json` fields:

- `schema` `"eik-paired-1"`, `kind` `"control"` | `"trial"`, `target` = directory name,
  `status` `"measured"` | `"duplicate"` | `"rejected"` (the last two are negative trials only; the control must be measured).
- `source` `{path, sha256}` (repository-relative; a trial's source must be inside its directory),
  `seeds` `[1874435642, 1947282751]`, `note` (what changed versus id50 / what was learned).
- trials: `control` `"eik-work/trials/paired-control"`, `base` `{path, sha256}` of id50.
- `runs.<label>` `{command, exit_code, files: {name: sha256}}`: the actual run.py command with source and seed.
- `index`: recomputed by `verify.py` from the raw logs and required to be equal. Measured:
  `source_sha256`, `normalised_sha256`, `gate_stage`, `rows.<seed>` with `seed`, `inputs_sha256`,
  `sha256`, `normalised_sha256`, `status`, `form` (`evaluate`|`stages`), `verifier`, `measurement`, `sandbox`,
  `hard_pool_sizes`, `S` (rv32im/thumbv6m/overall), `S_thumbv7em_reported_only`, `printed_incumbent_ratio`
  (null in stage form), `quick_host_check`, and `targets.<t>` with `bytes`, `stack`, `stack_bound`,
  `sample_words`, `sample_mismatches`, `wrong`, `size_factor`, `functions.<fn>` `{means, n, hard_p999, tail_factor}`.
  Duplicate: `normalised_sha256`, `gate_stage`, `duplicate_of`. Rejected: `rejected_at` (`gate`|`evaluation`)
  with `stage`/`reasons` or `rejections.<seed>`.
- trials, measured: `ratio_vs_control.<seed>.<board>` = candidate S / control S, recomputed by `verify.py`.

Make a trial packet from run.py logs (it copies the logs, writes `packet.json`, then verifies):

```sh
t=eik-work/toolkit; w=test/scratch/eik; k=<key>; src=eik-work/trials/$k/entry.c
python3 $t/run.py $w $k setup setup
python3 $t/run.py $w $k fingerprint fingerprint --details
python3 $t/run.py $w $k check check $src
python3 $t/run.py $w $k gate gate $src
for s in 1874435642 1947282751; do
  python3 $t/run.py $w $k measure-$s measure $src --seed $s     # or: evaluate-$s evaluate $src --quick --json --seed $s
  for f in sigmoid tanh exp; do python3 $t/run.py $w $k fullcheck-$s-$f fullcheck $src --function $f --quick --seed $s; done
done
python3 eik-work/trials/paired-control/verify.py assemble eik-work/trials/$k --source $src \
  --logs $w/cases/$k/logs --status measured --note "what changed versus id50"
```

## What verify.py checks

Recomputes every file hash and the source SHA-256; binds each record's argv to `eik <command>` on the
packet's source path and bytes; requires the seeds, unaltered scorer arguments (no `--champion`,
`--force-check`, `--targets`, `--no-sample`), the pinned verifier/measurement identities (or a fingerprint
log differing only in the host GCC line) and exit codes. Measured rows: passing `check` and accepted
`gate`, no target/compiler probe macros, source ≤ 256 KiB, full scored sets (n = 2000/1000/300/1000), every
target with zero wrong outputs and 98304 sample words with 0 mismatches, bytes ≤ 64 KiB, stack ≤ 8 KiB,
pinned hard-pool parameters, per-function geometric means and tail factors, each board S recomputed from
the class means (rel 1e-12), overall = √(rv32im·thumbv6m), quick host check passed on all three functions.
Trials additionally: the control verifies first; inputs digests, hard-pool sizes and evaluator IDs equal the
control's per seed; normalised source differs from the control (else it is a duplicate); ratios recompute.
Negative trials: a duplicate needs gate evidence (stage `duplicate`, or the control's normalised hash);
a rejection needs the source and raw gate/check or evaluation logs with stage and reasons. Exit codes
other than 0/1 (infrastructure errors), missing seeds or missing logs fail.
