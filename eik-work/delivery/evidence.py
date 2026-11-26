"""Standard-library evidence readers and deterministic final-package projections."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = '593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b'
BASE = '88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3'
BOARDS = ('rv32im', 'thumbv6m', 'overall')
TARGETS = ('rv32im', 'thumbv6m', 'thumbv7em')
FUNCTIONS = ('sigmoid', 'tanh', 'exp')
POPULATIONS = {'typical': (2000, .55), 'wide': (1000, .30), 'hard': (300, .10), 'uniform': (1000, .05)}
FINGERPRINT = {
    'measurement': '2c8fd1f3a6711f0639685319fb25262b02bfecf4c6589c52cb58928270a46322',
    'verifier': 'ebbf9d5cac596a718532b34798dc452e4050d6940594005c44f9a729c699c5a8',
    'sandbox': 'none',
}
PACKETS = (
    (849230117, 'heldout-1', 'raw/cand/historical-compare-id50.stdout#/measure', 'raw/id50/measure-849230117.stdout'),
    (2715043869, 'heldout-2', 'raw/candidate.stdout', 'raw/id50.stdout'),
    (396172055, 'heldout-3', 'raw/candidate.stdout', 'raw/id50.stdout'),
)
VERIFIERS = [
    'eik-work/final-validation/boards/verify.py',
    'eik-work/final-validation/review/verify.py',
    'eik-work/final-validation/merged/verify.py',
    *['eik-work/final-validation/scores/' + p[1] + '/verify.py' for p in PACKETS],
    'eik-work/offline-runtime/verify.py',
]
GAPS = [
    'Current champions withhold their sources and publish no same-input absolute S. All nine current S/ratio/threshold fields are null; eligibility is undetermined. No 3% current-champion gain is demonstrated.',
    'Cold offline evaluator replay is incomplete: the committed runtime omits the pinned Zig wheel, Unicorn wheel and QEMU upstream source archive. Historical successful runs restored exact payloads in scratch. Offline evidence verification needs none of them.',
    'Host exp uses an audited historical exhaustive report; original host checker and sanitizer-library byte hashes were not retained. Host sigmoid and tanh have fresh reruns. No claim of complete binary/runtime provenance for all host cells is made.',
    'The inherited wide-character selector compiles to different host/RV32IM and Thumb arms. Host ASan/UBSan coverage does not exercise the Thumb arm; selected full target runs cover its outputs.',
    'Strict C11 table-subobject byte offsets and incompatible struct views remain source-review concerns. Empirical zero-mismatch checks and a local rounding certificate are not a general portability proof.',
    'Novelty is checked against five public former champions only; duplicate status against private sources is undetermined.',
    'Heldout-3 evaluate timed out (exit 124) at the 600-second incumbent-comparison cap. Standalone paired measurements and quick host checks completed. Heldout-2 retains earlier timeouts and fallback stages as well as its completed coordinator evaluate.',
    'Shared-small-sigmoid has 36 external target shards absent from its original packet index, with missing original report-output binding and unavailable shard executables. The review inventories these limits; including the supplement does not change the frozen choice.',
]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def path(relative):
    need(isinstance(relative, str) and relative and not Path(relative).is_absolute()
         and '..' not in Path(relative).parts, 'unsafe citation: ' + str(relative))
    p = ROOT / relative
    need(p.is_file() and p.resolve() == p, 'missing/nonordinary citation: ' + relative)
    return p


def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def read(relative):
    def unique(pairs):
        result = dict(pairs)
        need(len(result) == len(pairs), 'duplicate JSON keys: ' + relative)
        return result
    def invalid(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return json.loads(path(relative).read_bytes(), object_pairs_hook=unique, parse_constant=invalid)


def artifact(relative):
    p = path(relative)
    return {'path': relative, 'sha256': digest(p), 'bytes': p.stat().st_size}


def close(a, b):
    return isinstance(a, (int, float)) and not isinstance(a, bool) and math.isfinite(a) and math.isclose(a, b, rel_tol=3e-14, abs_tol=1e-13)


def raw_report(citation):
    filename, _, pointer = citation.partition('#')
    data = read(filename)
    for key in pointer.split('/'):
        if key:
            data = data[key]
    return data


def calculate(report, seed, source):
    need(report['kind'] == 'measure' and report['schema'] == 'eik-report-1'
         and report['competition'] == 'exact-integer-kernels' and report['sha256'] == source,
         'score report source/kind conflict')
    need(report['seed'] == seed and report['fingerprint'] == FINGERPRINT
         and report['verdict'] == 'passed' and report['reasons'] == [] and report['stage'] is None,
         'score report failure/identity conflict')
    need(report['hard_pool']['source'] == 'hardscan' and report['hard_pool']['samples'] == 67108864
         and report['hard_pool']['threshold_log2_ulps'] == -18, 'changed hard population')
    scores = {}
    for target in TARGETS:
        target_data = report['targets'][target]
        need(target_data['wrong'] == [] and target_data['sample']['mismatches'] == 0
             and target_data['sample']['words'] == 98304, 'wrong scored/sample outputs')
        products = []
        for fn in FUNCTIONS:
            classes = target_data['functions'][fn]
            product = 1.0
            for cls, (count, weight) in POPULATIONS.items():
                stats = classes[cls]
                need(stats['n'] == count and stats['mean'] > 0 and stats['max'] <= 20000000,
                     'wrong scoring population/cap')
                product *= stats['mean'] ** weight
            tail = (1 + max(0, classes['hard']['p999'] - 20 * classes['typical']['mean']) / 1000000) ** .1
            need(close(report['scores'][target]['functions'][fn]['geo_mean_instr'], product)
                 and close(report['scores'][target]['functions'][fn]['tail_factor'], tail),
                 'raw function arithmetic conflict')
            products.append(product * tail)
        size = report['bytes'][target]
        need(type(size) is int and 0 < size <= 65536, 'target size limit')
        scores[target] = math.prod(products) ** (1 / 3) * (1 + size / 65536) ** .5
        need(close(scores[target], report['scores'][target]['S']), 'raw S arithmetic conflict')
    scores['overall'] = math.sqrt(scores['rv32im'] * scores['thumbv6m'])
    need(close(scores['overall'], report['scores']['overall']['S']), 'overall arithmetic conflict')
    # Preserve raw full-precision printed S after independently validating its arithmetic.
    return {board: report['scores'][board]['S'] for board in (*BOARDS, 'thumbv7em')}


def refresh_comparison():
    old = read('eik-work/final-validation/boards/snapshot.json')
    fresh = read('eik-work/delivery/public-refresh/snapshot.json')
    board_body = read('eik-work/delivery/public-refresh/boards.json')
    rows = {row['id']: row for row in board_body['boards']}
    need(set(rows) == set(BOARDS), 'refresh board set')
    for request in fresh['requests']:
        file = artifact(request['path'])
        need(request['method'] == 'GET' and request['url'].startswith(
            'https://conjectures.io/v1/competitions/exact-integer-kernels/')
             and file['sha256'] == request['sha256'] and file['bytes'] == request['bytes'],
             'refresh request/response binding')
    comparisons = {}
    for board in BOARDS:
        ref = fresh['references'][board]
        leader = read('eik-work/delivery/public-refresh/leaderboard-' + board + '.json')
        metadata = read('eik-work/delivery/public-refresh/submission-' + str(ref['submission']) + '.json')
        need(leader['reference'] == ref and rows[board]['current_promotion_id'] == ref['promotion_id']
             and metadata['source_sha256'] == ref['source_sha256'], 'refresh reference conflict')
        changed = (ref != old['board_references'][board] or rows[board]['config_hash'] != old['boards'][board]['config_hash'])
        comparisons[board] = {
            'reference_at_packaging': ref, 'reference_at_measurement': old['board_references'][board],
            'stale': changed,
            'required_remeasurement': ('Remeasure candidate and new champion on each of the three identical held-out input populations with the pinned kit; redo novelty checks.' if changed else None),
        }
    return {'snapshot': 'eik-work/delivery/public-refresh/snapshot.json',
            'refreshed_utc': fresh['refreshed_utc'], 'boards': comparisons}


def score_projection():
    refresh = refresh_comparison()
    rows = []
    diagnostics = []
    for seed, packet, cand_name, base_name in PACKETS:
        prefix = 'eik-work/final-validation/scores/' + packet + '/'
        cand_cite, base_cite = prefix + cand_name, prefix + base_name
        candidate, base = raw_report(cand_cite), raw_report(base_cite)
        cs, bs = calculate(candidate, seed, SOURCE), calculate(base, seed, BASE)
        need(candidate['inputs_sha256'] == base['inputs_sha256']
             and candidate['hard_pool'] == base['hard_pool'], 'unpaired score inputs')
        for board in BOARDS:
            rows.append({
                'seed': seed, 'board': board, 'candidate_S': cs[board], 'id50_S': bs[board],
                'candidate_over_id50': cs[board] / bs[board],
                'historical_le_0_970': cs[board] <= .97 * bs[board],
                'current_reference': refresh['boards'][board]['reference_at_packaging'],
                'current_S': None, 'candidate_over_current': None, 'current_le_0_970': None,
                'eligibility': 'undetermined', 'reason': 'SOURCE_WITHHELD; no same-input current-champion S',
                'stale_current_comparison': refresh['boards'][board]['stale'],
                'inputs_sha256': candidate['inputs_sha256'],
                'candidate_report': cand_cite, 'id50_report': base_cite,
            })
        diagnostics.append({'seed': seed, 'target': 'thumbv7em', 'scored_board': False,
                            'candidate_S': cs['thumbv7em'], 'id50_S': bs['thumbv7em'],
                            'candidate_over_id50': cs['thumbv7em'] / bs['thumbv7em']})
    return {'schema': 1, 'takeover_ratio': .97, 'rows': rows,
            'reported_only': diagnostics, 'verified_current_takeovers': [],
            'current_takeover_status': 'undetermined', 'board_refresh': refresh,
            'historical_reference': artifact('eik-work/baselines/former-50/entry.c'),
            'note': 'The chosen entry slightly regresses against id50. Local-incumbent and historical ratios are not live takeover evidence.'}


def csv_projection(scores):
    fields = ['seed', 'board', 'candidate_S', 'id50_S', 'candidate_over_id50', 'historical_le_0_970',
              'current_submission', 'current_S', 'candidate_over_current', 'current_le_0_970',
              'eligibility', 'stale_current_comparison', 'inputs_sha256']
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for row in scores['rows']:
        result = {key: row.get(key) for key in fields}
        result['current_submission'] = row['current_reference']['submission']
        writer.writerow({key: ('null' if val is None else str(val).lower() if isinstance(val, bool) else val)
                         for key, val in result.items()})
    return stream.getvalue()


def claims():
    return {'three_percent_current_gain_demonstrated': False, 'verified_current_takeovers': [],
            'current_takeover_status': 'undetermined', 'selected_exhaustive_reports_complete': True,
            'cold_offline_evaluator_replay_complete': False, 'complete_host_binary_provenance': False,
            'strict_C11_portability_proven': False, 'private_source_duplicate_check_complete': False,
            'historical_result': 'ties id50 on rv32im; slightly regresses on thumbv6m and overall'}


def dump(p, data):
    p.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n')
