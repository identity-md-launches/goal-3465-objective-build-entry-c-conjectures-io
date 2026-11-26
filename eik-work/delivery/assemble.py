#!/usr/bin/env python3
"""Assemble projections of immutable landed evidence; never runs a new experiment."""
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone

sys.dont_write_bytecode = True
from evidence import (ROOT, HERE, SOURCE, BOARDS, PACKETS, VERIFIERS, GAPS, artifact,
                      claims, csv_projection, dump, read, score_projection)


def experiments():
    ledger = read('eik-work/final-validation/review/ledger.json')
    dump(HERE / 'experiments.json', ledger)
    lines = ['# Experiment log', '',
             'No optimization or source edits were performed during packaging. This is the complete reviewed ledger, including losses and unscored attempts.', '',
             'Exact records: [experiments.json](experiments.json), copied from the [independent review ledger](../final-validation/review/ledger.json).', '',
             '## Paired control and all trials', '',
             '| Trial | Seed | RV32IM S | Thumbv6-M S | Overall S | RV32IM / id50 | Thumbv6-M / id50 | Overall / id50 |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    control = ledger['control']['rows']
    items = [('id50 paired control', ledger['control'])] + list(ledger['trials'].items())
    for name, item in items:
        for seed, row in item['rows'].items():
            scores = row['S']
            ratios = [scores[b] / control[seed]['S'][b] for b in BOARDS]
            lines.append('| ' + ' | '.join([name, seed] + [f'{scores[b]:.12f}' for b in BOARDS]
                                           + [f'{r:.12f}' for r in ratios]) + ' |')
    lines += ['', '## Techniques and disposition', '']
    for name, item in ledger['trials'].items():
        lines += ['### ' + name, '', item['change'], '',
                  'Original disposition: ' + item['original_disposition'] + '.', '',
                  'Packet: [' + item['packet']['path'] + '](../../' + item['packet']['path'] + ').', '']
    lines += ['## Additional measured variants', '']
    for name, row in ledger['additional_measured_variants'].items():
        lines += ['### shared-small-sigmoid ' + name, '', row['change'] + '.', '',
                  f"Seed {row['seed']}: " + '; '.join(f"{b} S={row['S'][b]:.12f}, ratio={row['ratio_vs_id50'][b]:.12f}" for b in BOARDS) + '.', '',
                  row['scope'] + '. Verdict: ' + row['verdict'] + '.', '']
    lines += ['## Unscored attempts and evidence discrepancies', '',
              'The following original attempt records include timeouts; an absent score is never converted to a gain. These records are preserved verbatim as JSON in the reviewed ledger.', '',
              '```json', __import__('json').dumps(ledger['recorded_evaluate_attempts_without_scores'], indent=2), '```', '',
              'The shared-small-sigmoid supplement has 36 external target reports omitted by its original packet. They do not change selection; missing original report bindings and checker executables remain disclosed in [review.md](../final-validation/review/review.md#shared-small-sigmoid-eligibility-discrepancy).', '',
              'Original selection minimizes the best-board worst-seed ratio, then worst-seed overall. All seven eligible trials have best-board ratio 1.0; m0-tanh-refine wins the tiebreak despite regressing. No combination was justified by two independent gains.', '',
              '## Original freeze narrative', '',
              'The complete original selection narrative remains unchanged in [freeze/experiments.md](../freeze/experiments.md). Its no-takeover statements refer to historical id50; live eligibility remains undetermined. The review ledger above incorporates the later evidence discrepancy and additional variants.']
    (HERE / 'experiment-log.md').write_text('\n'.join(lines) + '\n')


def documentation(scores):
    table = ['| Seed | Board | Candidate S | Historical id50 S | Candidate / id50 | Current S / ratio |',
             '| ---: | --- | ---: | ---: | ---: | --- |']
    for row in scores['rows']:
        table.append(f"| {row['seed']} | {row['board']} | {row['candidate_S']:.12f} | {row['id50_S']:.12f} | {row['candidate_over_id50']:.12f} | null / null |")
    text = '''# Frozen fallback delivery

The chosen entry slightly regresses against id50. It ties historical id50 on RV32IM and regresses on Thumbv6-M and overall on all three held-out seeds. No 3% gain against a current champion has been demonstrated. This is a completed fallback package with competition outcome **incomplete / undetermined**, not a winning entry.

The delivered [entry.c](entry.c) is an exact copy of [root entry.c](../../entry.c), SHA256 `593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b` (166,756 bytes). Root source was left unchanged. The manifest binds both copies.

## Held-out results

Lower is better; takeover requires candidate/current ≤ 0.970 on identical fresh inputs, followed by correctness checks. Historical id50 is a public former champion, not any current champion. The kit's local incumbent is also not a current champion. Neither comparison establishes a live takeover.

''' + '\n'.join(table) + '''

Exact values, raw-report citations, input hashes and explicit null fields are in [scores.json](scores.json) and [scores.csv](scores.csv). Thumbv7E-M is diagnostic only and is included in JSON. No board takeover is verified; which boards this entry would actually take remains undetermined.

## Packaging board refresh

Anonymous public GETs were made once at packaging; see [snapshot](public-refresh/snapshot.json) and its ten hash-bound request/response records. The references remain rv32im submission 52 / promotion 59, thumbv6m submission 53 / promotion 60, and overall submission 56 / promotion 61. None changed from the landed [board snapshot](../final-validation/boards/snapshot.json); no affected comparison is stale. Sources still return HTTP 403 SOURCE_WITHHELD and absolute current S is unpublished. Current S, candidate/current ratio and 0.970 predicate remain null for every board/seed, eligibility undetermined. Historical promotion ratios published by the service are not multiplied into a claimed same-input champion score.

## Correctness evidence and limits

The selected [merged coverage](../final-validation/merged/coverage-matrix.json) contains 12 complete runtime/function cells, each [0,4096) with 2^32 inputs and zero mismatches. Pinned eik merge exited 0 with verdict passed. Nine target cells bind the actual checker ELF. Host records report GCC ASan+UBSan. This is the retained reports' coverage result, not a claim of exhaustive success for every aspect of the competition or source portability. See [CHECKS.md](CHECKS.md) for selected runs, exclusions and missing provenance.

The [independent source review](../final-validation/review/review.md) supplies the rounding derivation and explains evidence discrepancies. The one-line Thumb tanh guard change is certified by an integer enclosure and target checks, but the host and Thumb compilation arms differ through the inherited wide-character selector. The review flags strict C11 subobject-offset/struct-view concerns. Novelty was checked against five public sources only; private-source duplicate status is unknown.

The committed evaluator runtime export is incomplete: three pinned payloads are missing. Historical fresh checks used exact restored bytes in scratch. Offline verification of the delivered evidence is available now; a new cold evaluator replay from committed files alone is not. No success is inferred from failed preparation, quick samples or evaluator timeouts.

## Review map

- [Manifest](manifest.json): complete repository-local log/source/tool inventory, SHA256 and size; files remain at their original repository paths.
- [Result](result.json): machine-readable identities, commands/exits, measured facts, explicit claims and gaps.
- [Experiment log](experiment-log.md) and [complete reviewed ledger](experiments.json): all eight trials, controls, two extra variants, regressions and unscored attempts.
- [Change note](change-note.md), [provenance](PROVENANCE.md), [offline replay](REPLAY.md) and [next steps](next-steps.md).

Run `python3 eik-work/delivery/verify.py` from the repository root. It uses Python's standard library, reads only local files, validates all inventory hashes, recomputes raw-score arithmetic and coverage, checks claims/nulls, and reruns the seven landed offline evidence verifiers. It does not rescore or rerun 2^32 inputs.
'''
    (HERE / 'REPORT.md').write_text(text)
    (HERE / 'change-note.md').write_text('''# Change versus public base

The frozen entry starts from former champion id50, source SHA256 `88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3`. Its only functional source edit is the exponent-119 tanh remainder guard in `t_l998689`:

```diff
- if (((t_z << 9) >> 27) != 0u)
+ if (((t_z << 9) >> 22) >= 31u)
```

The effective remainder cutoff falls from 262144 to 253952. It admits 5,632 new fast returns per sign without changing the quotient or refinement below the cutoff. The [review](../final-validation/review/review.md#exponent-119-tanh-change), [ROUNDING.md](../trials/m0-tanh-refine/ROUNDING.md), [certificate](../trials/m0-tanh-refine/prove-bound.py) and [fresh replay log](../final-validation/review/logs/prove-bound.stdout) explain the enclosure and strict rounding margins. The new strict interval avoids midpoint ties in newly fast cases.

RV32IM code sections remain equivalent to id50; the inherited selector chooses the other arm on Thumb. Thumbv6-M grows eight code/table bytes (20,500 to 20,508). Existing fast calls pay extra instructions, so this chosen entry slightly regresses against id50 despite locally cheaper refinement cases. It was frozen as the least-regressing eligible trial under the prior selection rule, not because it improved performance.

Packaging copied exact bytes and assembled evidence only. No candidate edits, evidence corrections or further optimization were made. [Original diff](../freeze/entry-vs-id50.diff).
''')
    (HERE / 'CHECKS.md').write_text('''# Checks and exact assurance limits

No new compiler, sanitizer, scoring or exhaustive evaluator runs were performed during packaging. Seven standard-library evidence verifiers were rerun successfully; their exact argv, exits and streams are in [verification.json](logs/verification.json). A clean scratch replay passed and eleven tampered packages were rejected, including altered source/raw evidence, fabricated scores/current denominators, unsupported success, suppressed gaps and missing coverage; see [negative-tests.json](logs/negative-tests.json) and [selftest.py](selftest.py). Several mutations refresh the delivery inventory to test semantic validation beyond hashing. The packaging environment is Linux x86-64 / Python 3.12.3; GCC is not available in this packaging container. Original runs record GCC 13.3.0, and their compiler identities are retained rather than represented as packaging runs.

The following is the landed merger's selected-coverage account (links in that account are relative to its original directory; use the [original CHECKS.md](../final-validation/merged/CHECKS.md) or [matrix](../final-validation/merged/coverage-matrix.json) to navigate raw records):

''' + (ROOT / 'eik-work/final-validation/merged/CHECKS.md').read_text() + '''

## Additional limits and scoring commands

Host exp is reused historical evidence without retained original host checker/sanitizer-library hashes. This missing provenance is not repaired by a report hash. Missing historical RV32IM-exp and Thumbv6-M-sigmoid target images were repaired by merger-owned fresh whole-domain reruns; only those fresh reports count. The original packets remain incomplete and unchanged.

Heldout-1 candidate and id50 quick evaluate both exited 0 (167.8 and 168.2 seconds). Heldout-2 includes earlier timeout attempts, fallback paired measures and quick checks, followed by a completed coordinator evaluate (exit 0, 287.730 seconds). Heldout-3 evaluate reached its 600-second local-incumbent cap (exit 124); standalone paired measures and quick fullchecks exited 0. All scored and stratified target outputs match; quick host runs check 134,217,728 words per function, not 2^32. Complete raw command records, stdout/stderr, pools and score reports remain in each packet and are inventoried by manifest.

The [source review](../final-validation/review/review.md) discusses the implementation-defined wide-character selector, strict-C11 portability concerns, public-only novelty checking and the shared-small-sigmoid packet-index discrepancy. Selected target output coverage does not make host sanitizers exercise Thumb-only code. The committed reduced runtime's prepare replay exited 1; a successful evidence verifier does not mean that export can bootstrap an evaluator.

No private credentials, registration, signing, submission or TAO spending were involved.
''')
    (HERE / 'next-steps.md').write_text('''# Next steps

1. Restore the exact three omitted runtime payloads at the pins in [runtime manifest](../offline-runtime/manifest.json), using a distribution channel with sufficient size allowance. Re-run cold isolated preparation, bootstrap and smoke replay; preserve ordinary committed bytes and licences. Until then, offline evaluator replay remains incomplete.
2. Repeat the historical host-exp exhaustive check while retaining checker, candidate object, GCC and sanitizer-library byte identities. This repairs its remaining provenance gap without changing the source.
3. Obtain an authoritative current-champion measurement on the same fresh inputs, or wait for public source release. Keep all current denominators null until measured. If board reference IDs/configuration change, repeat paired comparison and novelty checks for each affected board and seed.
4. Audit the inherited cross-ABI selector, subobject byte offsets and incompatible struct views for strict C11 portability. Host sanitizers alone cannot cover the Thumb arm. Keep target checks distinct.
5. In a separately authorized optimization phase, use id50 as the public base and inspect emitted instruction counts before spending fresh holdouts. Try a cheaper in-path Thumb typical multiply/sigmoid shortcut or a single-test tanh guard covered by the certificate. The current change's extra fast-path overhead outweighs its small refinement savings. Retain all negative results and raw report bindings.

Do not infer a 3% live gain from the local incumbent or historical id50. This delivery includes no optimization and no submission.
''')
    (HERE / 'PROVENANCE.md').write_text('''# Source, tool and reference provenance

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
''')
    (HERE / 'REPLAY.md').write_text('''# Offline verification and evaluator replay

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
''')


def main():
    need = __import__('evidence').need
    need(artifact('entry.c')['sha256'] == SOURCE, 'root source pin')
    (HERE / 'entry.c').write_bytes((ROOT / 'entry.c').read_bytes())
    scores = score_projection()
    dump(HERE / 'scores.json', scores)
    (HERE / 'scores.csv').write_text(csv_projection(scores))
    experiments()
    documentation(scores)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    checks = []
    for verifier in VERIFIERS:
        argv = ['python3', '-B', verifier]
        run = subprocess.run(argv, cwd=ROOT, env=env, text=True, capture_output=True, timeout=90)
        checks.append({'argv': argv, 'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr})
        need(run.returncode == 0, 'landed evidence verifier failed: ' + verifier + '\n' + run.stderr)
    dump(HERE / 'logs/verification.json', checks)
    try:
        gcc = subprocess.run(['gcc', '--version'], capture_output=True, text=True)
        gcc_record = {'argv': ['gcc', '--version'], 'exit_code': gcc.returncode, 'stdout': gcc.stdout, 'stderr': gcc.stderr}
    except FileNotFoundError:
        gcc_record = {'argv': ['gcc', '--version'], 'exit_code': 127, 'stdout': '', 'stderr': 'gcc not available in packaging container; no new compiler run'}
    dump(HERE / 'logs/environment.json', {'system': platform.system(), 'machine': platform.machine(),
         'python': platform.python_version(), 'gcc_probe': gcc_record})
    core = ['entry.c', 'REPORT.md', 'scores.json', 'scores.csv', 'experiments.json', 'experiment-log.md',
            'change-note.md', 'next-steps.md', 'CHECKS.md', 'PROVENANCE.md', 'REPLAY.md',
            'logs/verification.json', 'logs/environment.json', 'public-refresh/snapshot.json', 'logs/negative-tests.json']
    review = read('eik-work/final-validation/review/result.json')
    merged = read('eik-work/final-validation/merged/result.json')
    result = {
        'schema': 1, 'status': 'incomplete', 'package_status': 'pass',
        'outcome': 'evidenced negative fallback; live objective undetermined',
        'source': {'root': artifact('entry.c'), 'delivered': artifact('eik-work/delivery/entry.c'),
                   'normalised_sha256': review['source']['normalised_sha256'],
                   'base': artifact('eik-work/baselines/former-50/entry.c')},
        'tools': review['tools'], 'claims': claims(), 'gaps': GAPS,
        'artifacts': {name: artifact('eik-work/delivery/' + name) for name in core},
        'manifest': 'eik-work/delivery/manifest.json',
        'commands': checks + [{'argv': ['python3', '-B', 'eik-work/delivery/refresh.py'],
                               'exit_code': 0, 'evidence': 'eik-work/delivery/public-refresh/snapshot.json',
                               'purpose': 'one packaging refresh; 10 anonymous GETs; all board identities unchanged'}, gcc_record],
        'original_commands': {name: 'eik-work/final-validation/' + name + '/result.json'
                              for name in ['review', 'merged', 'scores/heldout-1', 'scores/heldout-2', 'scores/heldout-3']},
        'measured_facts': {'coverage': merged['measured_facts'], 'heldout_rows': scores['rows'],
                           'code_table_bytes': review['static']['bytes'],
                           'static_stack_bound_bytes': review['static']['stack_bound'],
                           'board_refresh': scores['board_refresh']},
        'evidence_verification': {'command': 'python3 eik-work/delivery/verify.py',
                                  'offline': True, 'does_not_rerun_kernels': True},
        'self_tests': {'command': 'python3 -B eik-work/delivery/selftest.py',
                       'exit_code': 0, 'clean_accepted': True, 'mutations_rejected': 11,
                       'log': artifact('eik-work/delivery/logs/negative-tests.json')},
    }
    dump(HERE / 'result.json', result)
    files = sorted(p for p in (ROOT / 'eik-work').rglob('*') if p.is_file()
                   and '__pycache__' not in p.parts and p != HERE / 'manifest.json')
    inventory = {str(p.relative_to(ROOT)): artifact(str(p.relative_to(ROOT))) for p in files}
    inventory['entry.c'] = artifact('entry.c')
    manifest = {'schema': 1, 'hash': 'sha256', 'source_sha256': SOURCE,
                'inventory_kind': 'complete repository-local eik-work evidence bundle plus frozen root source',
                'excluded': ['eik-work/delivery/manifest.json (self)', '**/__pycache__/** (non-evidence Python cache)'],
                'files': dict(sorted(inventory.items()))}
    dump(HERE / 'manifest.json', manifest)
    print(f'Assembled negative fallback: {len(inventory)} hash-bound files, nine held-out rows, seven evidence checks passed.')


if __name__ == '__main__':
    main()
