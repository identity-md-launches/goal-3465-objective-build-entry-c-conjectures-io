#!/usr/bin/env python3
"""Offline audit of the retained, explicitly incomplete coverage packet.

A successful invocation validates evidence integrity, not a kernel pass. There
is deliberately no route to a pass using the unbound historical image.
"""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = '593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b'
FINGERPRINT = {
    'measurement': '2c8fd1f3a6711f0639685319fb25262b02bfecf4c6589c52cb58928270a46322',
    'verifier': 'ebbf9d5cac596a718532b34798dc452e4050d6940594005c44f9a729c699c5a8',
    'sandbox': 'none',
}


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    require(path.is_file() and not path.is_symlink(), f'missing/nonordinary evidence: {path}')
    return path.read_bytes()


def digest(path):
    return hashlib.sha256(read(path)).hexdigest()


def load(path):
    return json.loads(read(path))


def child(base, name):
    path = base / name
    require(not Path(name).is_absolute() and '..' not in Path(name).parts,
            f'unsafe evidence path: {name}')
    require(path.resolve() == path, f'symlink evidence path: {name}')
    return path


def main():
    r = load(HERE / 'result.json')
    require(r['schema'] == 'eik-coverage-result-1', 'unknown result schema')
    require(r['status'] == 'incomplete', 'unsupported success: historical image not bound')
    require((r['function'], r['runtime']) == ('sigmoid', 'thumbv6m'), 'wrong target')
    for name, item in r['artifacts'].items():
        path = child(HERE, name)
        require(len(read(path)) == item['bytes'] and digest(path) == item['sha256'],
                f'tampered artifact: {name}')
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file()}
    require(actual == set(r['artifacts']) | {'result.json', 'verify.py'}, 'artifact inventory differs')
    for name, expected in r['source_tool_identities'].items():
        require(digest(child(ROOT, name)) == expected, f'changed source/tool identity: {name}')
    require(digest(ROOT / 'entry.c') == SOURCE, 'root source changed')
    require(digest(ROOT / 'eik-work/trials/m0-tanh-refine/entry.c') == SOURCE, 'trial source changed')
    c = load(HERE / r['coverage'])
    require(c['status'] == 'incomplete' and c['function'] == 'sigmoid'
            and c['runtime'] == 'thumbv6m', 'unsupported coverage status')
    require(c['source'] == {'path': 'entry.c', 'sha256': SOURCE}, 'source binding differs')
    require(c['required_chunks'] == [0, 4096] and c['chunk_words'] == 1 << 20
            and c['required_words'] == 1 << 32, 'domain differs')
    require(c['accepted_ranges'] == [] and c['selected_reports'] == []
            and c['accepted_words'] == 0 and c['gaps'] == [[0, 4096]]
            and r['gaps'] == c['gaps'], 'unbound report credited as coverage')
    require(c['provenance']['reused'] == [] and c['provenance']['rerun'] == [], 'unsupported reuse/rerun')
    prior = HERE / 'prior'
    packet = load(prior / 'packet.json')
    label = 'targetcheck-thumbv6m-sigmoid-all'
    for run in (label, 'fingerprint'):
        record = load(prior / f'{run}.json')
        require(record['exit_code'] == 0, 'historical command failed')
        for suffix in ('json', 'stdout', 'stderr'):
            name = f'{run}.{suffix}'
            require(digest(prior / name) == packet['runs'][run]['files'][name], 'packet raw hash mismatch')
        for suffix in ('stdout', 'stderr'):
            require(digest(prior / f'{run}.{suffix}') == record[f'{suffix}_sha256'], 'raw stream mismatch')
    record = load(prior / f'{label}.json')
    require(record['source_sha256'] == SOURCE and packet['source']['sha256'] == SOURCE, 'command source differs')
    require(record['argv'][1:] == ['-m', 'eik', 'targetcheck',
            '$REPO/eik-work/trials/m0-tanh-refine/entry.c', '--function', 'sigmoid',
            '--target', 'thumbv6m', '--jobs', '1'], 'historical command binding differs')
    rep = load(prior / f'{label}.stdout')
    require(rep['schema'] == 'eik-report-1' and rep['kind'] == 'targetcheck', 'wrong report type')
    require(rep['function'] == 'sigmoid' and rep['target'] == 'thumbv6m', 'wrong historical target')
    require(rep['sha256'] == SOURCE and rep['fingerprint'] == FINGERPRINT, 'historical identity differs')
    require(rep['verdict'] == 'passed' and rep['stage'] is None and rep['reasons'] == []
            and rep['complete'] is True and rep['range_complete'] is True
            and rep['mismatches'] == 0 and rep['chunk_lo'] == 0 and rep['chunk_hi'] == 4096
            and rep['words_checked'] == 1 << 32, 'historical claim not exhaustive/clean')
    fp = load(prior / 'fingerprint.stdout')
    for key, expected in FINGERPRINT.items():
        require(fp[key] == expected, 'fingerprint mismatch')
    for key in ('measurement', 'verifier'):
        details = fp['details'][key]
        require(hashlib.sha256(json.dumps(details, sort_keys=True, default=list).encode()).hexdigest()
                == FINGERPRINT[key], 'fingerprint details do not hash to claimed identity')
        for name, expected in details['files'].items():
            require(digest(child(ROOT / 'eik-work/toolkit/kit', name)) == expected, 'pinned kit/reference differs')
    require(c['historical_claim'] == {key: rep[key] for key in c['historical_claim']}, 'historical summary differs')
    binding = c['image_binding']
    require(binding['status'] == 'unproven' and binding['recorded_sha256'] == rep['image_sha256'], 'binding differs')
    require(binding['retained_freeze_sha256'] == digest(HERE / 'objects/guest-thumbv6m.elf')
            != rep['image_sha256'], 'image mismatch evidence differs')
    require(binding['recorded_image_available'] is False
            and binding['executable_equivalence_proven'] is False
            and binding['path_only_differences_proven'] is False, 'unproven equivalence asserted')
    prep = load(HERE / 'prepare.json')
    require(prep['exit_code'] == 1 and prep['argv'] == ['python3', 'eik-work/offline-runtime/prepare.py',
            'test/scratch/thumbv6m-sigmoid/dependencies'], 'preparation command differs')
    require(b'required payloads absent from export:' in read(HERE / 'prepare.stderr'), 'missing preparation failure')
    probe = load(HERE / 'host-probe.json')
    require(probe['exit_code'] == 127 and probe['system'] == 'Linux' and probe['machine'] == 'x86_64'
            and probe['python'].startswith('3.12.') and b'command not found' in read(HERE / 'host-probe.stderr'),
            'host prerequisite evidence differs')
    require(r['commands'] == [prep, probe], 'command summaries differ')
    require({f['stage'] for f in c['failures']} == {'image-binding', 'runtime-prepare', 'host-prerequisite'}, 'failures missing')
    require(r['measured_facts'] == {'historical_words': 4294967296, 'historical_mismatches': 0,
            'credited_words': 0, 'image_binding': 'unproven'}, 'measured facts differ')
    print('Evidence verified: INCOMPLETE thumbv6m/sigmoid; 0 credited words; gap [0,4096).')
    print('Historical full-domain pass is unbound to retained image; runtime preparation exited 1; GCC absent.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'evidence rejected: {exc}', file=sys.stderr)
        sys.exit(1)
