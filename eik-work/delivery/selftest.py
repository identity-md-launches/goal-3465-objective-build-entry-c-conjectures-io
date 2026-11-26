#!/usr/bin/env python3
"""Exercise clean replay and rejection of tampered evidence in disposable scratch."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]


def main():
    scratch = ROOT / 'test/scratch/delivery-package-negative'
    if scratch.exists():
        raise ValueError('self-test scratch already exists; use a clean test workspace')
    scratch.mkdir(parents=True)
    clone = scratch / 'repo'
    clone.mkdir()
    records = []
    try:
        shutil.copy2(ROOT / 'entry.c', clone / 'entry.c')
        shutil.copytree(ROOT / 'eik-work', clone / 'eik-work', ignore=shutil.ignore_patterns('__pycache__'))
        manifest_path = clone / 'eik-work/delivery/manifest.json'
        original_manifest = manifest_path.read_bytes()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')

        def check(label, wanted):
            argv = [sys.executable, '-B', 'eik-work/delivery/verify.py']
            result = subprocess.run(argv, cwd=clone, env=env, capture_output=True, text=True, timeout=90)
            records.append({'case': label, 'argv': ['python3', '-B', 'eik-work/delivery/verify.py'],
                            'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
            if (result.returncode == 0) != wanted:
                raise ValueError('unexpected self-test verdict: ' + label + '\n' + result.stdout + result.stderr)

        check('clean repository-local evidence replay', True)

        def mutate(label, filename, transform, rehash=False):
            target = clone / filename
            original = target.read_bytes()
            changed = transform(original)
            if changed is None:
                target.unlink()
            else:
                target.write_bytes(changed)
            if rehash:
                manifest = json.loads(original_manifest)
                manifest['files'][filename]['sha256'] = hashlib.sha256(changed).hexdigest()
                manifest['files'][filename]['bytes'] = len(changed)
                manifest_path.write_text(json.dumps(manifest))
            try:
                check(label, False)
            finally:
                target.write_bytes(original)
                manifest_path.write_bytes(original_manifest)

        def edit_json(operation):
            def apply(raw):
                data = json.loads(raw)
                operation(data)
                return (json.dumps(data, indent=2, sort_keys=True) + '\n').encode()
            return apply

        mutate('delivered source changed, inventory refreshed', 'eik-work/delivery/entry.c', lambda b: b + b'\n', True)
        raw = 'eik-work/final-validation/scores/heldout-3/raw/candidate.stdout'
        mutate('missing raw score evidence', raw, lambda b: None)
        mutate('tampered raw score evidence', raw, lambda b: b + b'\n')
        mutate('fabricated candidate score, inventory refreshed', 'eik-work/delivery/scores.json',
               edit_json(lambda d: d['rows'][0].update(candidate_S=1.0)), True)
        mutate('fabricated current denominator, inventory refreshed', 'eik-work/delivery/scores.json',
               edit_json(lambda d: d['rows'][0].update(current_S=100.0, candidate_over_current=.2)), True)
        mutate('unsupported success status, inventory refreshed', 'eik-work/delivery/result.json',
               edit_json(lambda d: d.update(status='pass')), True)
        mutate('unsupported 3 percent gain, inventory refreshed', 'eik-work/delivery/result.json',
               edit_json(lambda d: d['claims'].update(three_percent_current_gain_demonstrated=True)), True)
        mutate('suppressed gaps, inventory refreshed', 'eik-work/delivery/result.json',
               edit_json(lambda d: d.update(gaps=[])), True)
        mutate('coverage missing a cell, inventory refreshed', 'eik-work/final-validation/merged/coverage-matrix.json',
               edit_json(lambda d: d['cells'].pop()), True)
        mutate('report falsified without inventory update', 'eik-work/delivery/REPORT.md',
               lambda b: b.replace(b'No 3% gain', b'A verified 3% gain'))
        # The evidence roots also prevent a changed raw report plus a refreshed
        # delivery inventory from passing the landed packet's independent pins.
        mutate('raw score falsified, delivery inventory refreshed', raw,
               edit_json(lambda d: d['scores']['rv32im'].update(S=1.0)), True)
        print(json.dumps({'schema': 1, 'clean_accepted': True, 'mutations_rejected': len(records) - 1,
                          'records': records}, indent=2))
    finally:
        shutil.rmtree(scratch)


if __name__ == '__main__':
    main()
