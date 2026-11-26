#!/usr/bin/env python3
"""Run this bounded paired trial through the unmodified pinned runner; use only scratch builds."""
import json
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
TRIAL = Path(__file__).resolve().parent
WORK = 'test/scratch/rv-exp-interval'
SOURCE = 'eik-work/trials/rv-exp-interval/entry.c'

def run(label, args, timeout=None):
    cmd = ['python3', 'eik-work/toolkit/run.py', WORK, 'rv-exp-interval', label, *args]
    record = ROOT / WORK / 'cases/rv-exp-interval/logs' / f'{label}.json'
    if record.exists():
        previous = json.loads(record.read_text())
        recorded_args = [a.replace('$REPO/', '') for a in previous['argv'][3:]]
        assert recorded_args == args, (label, recorded_args, args)
        assert previous['exit_code'] == 0, (label, previous['exit_code'])
        if previous['source_sha256'] is not None:
            assert previous['source_sha256'] == hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest()
        print('REUSE successful recorded command ' + label, flush=True)
        return 0
    start = time.monotonic()
    print('RUN ' + ' '.join(cmd), flush=True)
    p = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    timed_out = False
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(p.pid, signal.SIGKILL)
        out, err = p.communicate()
    print(f'EXIT {p.returncode}, {time.monotonic()-start:.1f}s; {out[-180:]} {err[-180:]}', flush=True)
    if timed_out:
        (TRIAL / f'{label}.stdout').write_text(out)
        (TRIAL / f'{label}.stderr').write_text(err)
        (TRIAL / f'{label}.attempt.json').write_text(json.dumps(dict(command=cmd, timeout_seconds=timeout,
            exit_code=p.returncode, timed_out=True, seconds=round(time.monotonic()-start,3),
            reason='Local incumbent remeasurement did not finish within the trial budget; use unchanged measure/fullcheck stages for absolute S and paired id50 ratios.'), indent=2)+'\n')
    return p.returncode

if __name__ == '__main__':
    for label, args in [('setup',['setup']), ('fingerprint',['fingerprint','--details']), ('check',['check',SOURCE]), ('gate',['gate',SOURCE])]:
        if run(label,args): raise SystemExit(1)
    for seed in (1874435642,1947282751):
        if run(f'measure-{seed}', ['measure',SOURCE,'--seed',str(seed)]): raise SystemExit(1)
        for fn in ('sigmoid','tanh','exp'):
            if run(f'fullcheck-{seed}-{fn}', ['fullcheck',SOURCE,'--function',fn,'--quick','--seed',str(seed)]): raise SystemExit(1)
    for target in ('rv32im','thumbv6m','thumbv7em'):
        if run(f'targetcheck-{target}-exp-3063-3082', ['targetcheck',SOURCE,'--function','exp','--target',target,'--chunks','3063:3082','--jobs','2']): raise SystemExit(1)
    for fn in ('sigmoid','tanh','exp'):
        if run(f'fullcheck-all-{fn}', ['fullcheck',SOURCE,'--function',fn]): raise SystemExit(1)
    for seed in (1874435642,1947282751):
        run(f'evaluate-attempt-{seed}', ['evaluate',SOURCE,'--quick','--json','--seed',str(seed)],timeout=180)
