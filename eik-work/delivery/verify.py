#!/usr/bin/env python3
"""Offline, read-only verification of the frozen negative-result delivery."""
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
from evidence import (ROOT, HERE, SOURCE, BASE, BOARDS, FUNCTIONS, PACKETS, VERIFIERS,
                      FINGERPRINT, GAPS, artifact, claims, csv_projection, digest, need,
                      path, raw_report, read, score_projection)

# Independently pinned evidence roots prevent rewritten inventories from blessing
# substituted score packets, kit/reference data or a different source review.
PINS = {
    'entry.c': SOURCE,
    'eik-work/baselines/former-50/entry.c': BASE,
    'eik-work/final-validation/review/result.json': '4127ba3e3a9da2a271a6e5eafbd8bf5b765187e56d5952d8d669688592500154',
    'eik-work/final-validation/review/ledger.json': '1a270a443283db6d9d3d538d4cd5e48e6f1d9707d81cec61154d212381c331b4',
    'eik-work/final-validation/merged/coverage-matrix.json': '0fd8e44963885fb2f6acf8252b820e0ec3ef9a71b3f57370258632ad694849ac',
    'eik-work/toolkit/manifest.json': 'c22729dc9c28b9e54740e639a2cad1bcf58b5665aaf9ba32ccf2abea08b1cb3a',
    'eik-work/final-validation/scores/heldout-1/scores.json': 'f8a021b39c873d14359bed1c7cd54b15827cfcabbd73a03dcfe92e5e311fc9bd',
    'eik-work/final-validation/scores/heldout-2/scores.json': 'e67793a3bd3be12651a2c099aea4da596561e1809b158a9f999c64235e3e2437',
    'eik-work/final-validation/scores/heldout-3/scores.json': '67edb09fff3ba22d4c5186530153812d4541b47066f9f11652bb720498a31606',
}
REQUIRED = {
    'entry.c', 'REPORT.md', 'scores.json', 'scores.csv', 'experiments.json', 'experiment-log.md',
    'change-note.md', 'next-steps.md', 'CHECKS.md', 'PROVENANCE.md', 'REPLAY.md', 'result.json',
    'manifest.json', 'verify.py', 'evidence.py', 'assemble.py', 'refresh.py', 'selftest.py',
    'logs/verification.json', 'logs/environment.json', 'public-refresh/snapshot.json', 'logs/negative-tests.json',
}


def inventory():
    manifest = read('eik-work/delivery/manifest.json')
    need(manifest['schema'] == 1 and manifest['hash'] == 'sha256'
         and manifest['source_sha256'] == SOURCE, 'manifest identity')
    for name in REQUIRED:
        path('eik-work/delivery/' + name)
    need((ROOT / 'entry.c').read_bytes() == (HERE / 'entry.c').read_bytes(), 'source copies differ')
    files = manifest['files']
    actual = {str(p.relative_to(ROOT)) for p in (ROOT / 'eik-work').rglob('*')
              if p.is_file() and '__pycache__' not in p.parts and p != HERE / 'manifest.json'} | {'entry.c'}
    need(set(files) == actual, 'incomplete inventory or unexpected evidence files')
    for name, record in files.items():
        need(record == artifact(name), 'missing/tampered evidence: ' + name)
    for name, expected in PINS.items():
        need(digest(path(name)) == expected, 'authoritative evidence pin changed: ' + name)
    return files


def check_citations(files):
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            target = target.split('#', 1)[0]
            if not target or target.startswith(('https://', 'http://')):
                continue
            resolved = (p.parent / target).resolve()
            need(resolved.is_relative_to(ROOT) and resolved.exists(), 'missing document citation: ' + target)
            if resolved.is_file():
                need(str(resolved.relative_to(ROOT)) in files or resolved == HERE / 'manifest.json',
                     'unhashed document citation: ' + target)
    # Every structured raw-report citation is validated independently as well.
    for row in read('eik-work/delivery/scores.json')['rows']:
        for key in ('candidate_report', 'id50_report'):
            raw_report(row[key])
            need(row[key].split('#')[0] in files, 'unhashed raw score report')


def check_coverage():
    matrix = read('eik-work/final-validation/merged/coverage-matrix.json')
    need(matrix['status'] == 'pass' and matrix['fingerprint'] == FINGERPRINT, 'coverage identity')
    expected_cells = {(r, f) for r in ('host', 'rv32im', 'thumbv6m', 'thumbv7em') for f in FUNCTIONS}
    need(len(matrix['cells']) == 12 and {(c['runtime'], c['function']) for c in matrix['cells']} == expected_cells,
         'coverage cell set')
    for cell in matrix['cells']:
        covered = set()
        for selected in cell['selected']:
            raw = read(selected['report']['path'])
            need(raw['sha256'] == SOURCE and raw['fingerprint'] == FINGERPRINT and raw['function'] == cell['function']
                 and raw['verdict'] == 'passed' and raw['mismatches'] == 0
                 and raw['range_complete'] is True, 'failed coverage report')
            lo, hi = raw['chunk_lo'], raw['chunk_hi']
            need(type(lo) is int and type(hi) is int and 0 <= lo < hi <= 4096, 'coverage interval')
            chunks = set(range(lo, hi))
            need(not covered.intersection(chunks) and raw['words_checked'] == len(chunks) * (1 << 20),
                 'overlap or false coverage count')
            covered.update(chunks)
            if cell['runtime'] == 'host':
                need(raw['kind'] == 'fullcheck' and raw['quick'] is False and raw['exit'] == 0,
                     'host sample counted as exhaustive')
            else:
                need(raw['target'] == cell['runtime'] and raw['kind'] == 'targetcheck'
                     and digest(path(selected['image']['path'])) == raw['image_sha256'],
                     'target image unbound')
        need(covered == set(range(4096)) and cell['gaps'] == [] and cell['words_checked'] == (1 << 32)
             and cell['status'] == 'pass' and cell['mismatches'] == 0 and cell['sanitizer_failures'] == 0,
             'incomplete/overclaimed coverage')
    return read('eik-work/final-validation/merged/result.json')['measured_facts']


def check_refresh():
    fresh = read('eik-work/delivery/public-refresh/snapshot.json')
    requests = fresh['requests']
    need(len(requests) == 10 and len({r['url'] for r in requests}) == 10, 'refresh request completeness')
    base = 'https://conjectures.io/v1/competitions/exact-integer-kernels/'
    by_url = {r['url']: r for r in requests}
    expected = {base + 'boards': 'boards.json'}
    for board in BOARDS:
        ref = fresh['references'][board]
        expected[base + 'leaderboard?board=' + board] = 'leaderboard-' + board + '.json'
        sid = str(ref['submission'])
        expected[base + 'submissions/' + sid] = 'submission-' + sid + '.json'
        expected[base + 'submissions/' + sid + '/source'] = 'source-' + sid + '.json'
    need(set(expected) == set(by_url), 'refresh endpoints differ')
    for url, filename in expected.items():
        request = by_url[url]
        need(request['path'] == 'eik-work/delivery/public-refresh/' + filename,
             'refresh URL mapped to wrong body')
        if url.endswith('/source'):
            body = read(request['path'])
            # Public response may wrap the error under detail; require its
            # literal error code without asserting downloaded source bytes.
            need(request['http_status'] == 403 and 'SOURCE_WITHHELD' in json.dumps(body),
                 'refresh source withholding claim unsupported')
        else:
            need(request['http_status'] == 200, 'refresh failed')


def check_result(scores, coverage):
    result = read('eik-work/delivery/result.json')
    review = read('eik-work/final-validation/review/result.json')
    need(result['schema'] == 1 and result['status'] == 'incomplete' and result['package_status'] == 'pass'
         and result['outcome'] == 'evidenced negative fallback; live objective undetermined', 'unsupported result success')
    need(result['claims'] == claims() and result['gaps'] == GAPS, 'unsupported claims or suppressed gaps')
    need(result['tools'] == review['tools'], 'tool provenance differs')
    need(result['source'] == {'root': artifact('entry.c'), 'delivered': artifact('eik-work/delivery/entry.c'),
                             'normalised_sha256': review['source']['normalised_sha256'],
                             'base': artifact('eik-work/baselines/former-50/entry.c')}, 'source identities differ')
    facts = result['measured_facts']
    need(facts == {'coverage': coverage, 'heldout_rows': scores['rows'],
                   'code_table_bytes': review['static']['bytes'],
                   'static_stack_bound_bytes': review['static']['stack_bound'],
                   'board_refresh': scores['board_refresh']}, 'measured facts differ from evidence')
    need(result['manifest'] == 'eik-work/delivery/manifest.json', 'missing manifest citation')
    need(len(result['artifacts']) == 15, 'incomplete result artifact list')
    for name, item in result['artifacts'].items():
        need(item == artifact('eik-work/delivery/' + name), 'result artifact hash differs')
    ledger = read('eik-work/delivery/logs/verification.json')
    need(len(ledger) == len(VERIFIERS), 'missing verifier command records')
    for expected, record in zip(VERIFIERS, ledger):
        need(record['argv'] == ['python3', '-B', expected] and record['exit_code'] == 0
             and record['stdout'] and record['stderr'] == '', 'failed/unbound verification record')
    environment = read('eik-work/delivery/logs/environment.json')
    need(environment['system'] == 'Linux' and environment['machine'] == 'x86_64'
         and environment['python'].startswith('3.12.'), 'packaging platform differs')
    need(result['commands'][:len(ledger)] == ledger and result['commands'][-1] == environment['gcc_probe'],
         'command/exit record conflict')
    need(result['commands'][len(ledger)]['argv'] == ['python3', '-B', 'eik-work/delivery/refresh.py']
         and result['commands'][len(ledger)]['exit_code'] == 0, 'refresh command conflict')
    for relative in result['original_commands'].values():
        path(relative)
    need(result['evidence_verification'] == {'command': 'python3 eik-work/delivery/verify.py',
                                            'offline': True, 'does_not_rerun_kernels': True},
         'verification scope misrepresented')
    tests = read('eik-work/delivery/logs/negative-tests.json')
    need(tests['schema'] == 1 and tests['clean_accepted'] is True and tests['mutations_rejected'] == 11
         and len(tests['records']) == 12, 'missing negative-test record')
    need(tests['records'][0]['exit_code'] == 0 and all(
        row['exit_code'] != 0 and 'verify: FAIL:' in row['stderr'] for row in tests['records'][1:]),
         'negative tests accepted an altered package')
    need(result['self_tests'] == {'command': 'python3 -B eik-work/delivery/selftest.py', 'exit_code': 0,
                                  'clean_accepted': True, 'mutations_rejected': 11,
                                  'log': artifact('eik-work/delivery/logs/negative-tests.json')},
         'self-test summary overclaims')


def main():
    files = inventory()
    check_citations(files)
    check_refresh()
    scores = score_projection()
    need(read('eik-work/delivery/scores.json') == scores, 'scores projection differs from raw arithmetic')
    need((HERE / 'scores.csv').read_text() == csv_projection(scores), 'CSV differs from JSON/raw scores')
    need(len(scores['rows']) == 9 and len({(r['seed'], r['board']) for r in scores['rows']}) == 9,
         'missing/duplicate heldout board row')
    for row in scores['rows']:
        need(all(key in row and row[key] is None for key in ('current_S', 'candidate_over_current', 'current_le_0_970'))
             and row['eligibility'] == 'undetermined' and row['historical_le_0_970'] is False,
             'unsupported live or historical success')
        need(row['candidate_over_id50'] == 1 if row['board'] == 'rv32im' else row['candidate_over_id50'] > 1,
             'historical regression statement unsupported')
    need(read('eik-work/delivery/experiments.json') == read('eik-work/final-validation/review/ledger.json'),
         'incomplete experiment ledger')
    coverage = check_coverage()
    check_result(scores, coverage)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    for verifier in VERIFIERS:
        run = subprocess.run([sys.executable, '-B', str(path(verifier))], cwd=ROOT, env=env,
                             text=True, capture_output=True, timeout=90)
        need(run.returncode == 0, 'landed verifier rejected evidence: ' + verifier + '\n' + run.stdout + run.stderr)
    print(f'verify: PASS: {len(files)} files hash-verified; exact frozen source copies; 9 held-out score rows; 12 complete coverage cells.')
    print('Historical result: ties id50 on RV32IM; slightly regresses on Thumbv6-M and overall.')
    print('Competition status: incomplete; current-champion S/ratios null, eligibility undetermined; no 3% gain claimed.')
    print('Gaps retained: reduced runtime omits 3 payloads; host-exp binary provenance; cross-ABI/C11 review; private-source novelty; evaluate timeouts.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError, IndexError, subprocess.TimeoutExpired) as error:
        print('verify: FAIL: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
