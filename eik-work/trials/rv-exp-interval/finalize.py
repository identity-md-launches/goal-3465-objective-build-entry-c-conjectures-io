#!/usr/bin/env python3
"""Assemble completed pinned logs, verify both evidence layers, write the item result."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REL=str(HERE.relative_to(ROOT))
SOURCE=REL+'/entry.c'
NOTE=('Single early unsigned word-range check in eik_exp_r for [0xBF800001,0xC0800000], jumping to the identical original cubic cell and refinement arithmetic. '
      'RV32 regresses by about 15.2%; Thumb allocated sections and scores are unchanged under the preserved id50 selector. '
      'No takeover recommendation. Full-population stage scores paired with unchanged id50, two-seed quick sanitizer checks, '
      'complete all-input host checks and selected object checks retained; bounded evaluate attempts documented separately.')

def run(label,command):
    r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    (HERE/f'{label}.stdout').write_text(r.stdout)
    (HERE/f'{label}.stderr').write_text(r.stderr)
    (HERE/f'{label}.record.json').write_text(json.dumps({'command':command,'exit_code':r.returncode},indent=2)+'\n')
    print(label,r.returncode,r.stdout[-2000:],r.stderr[-2000:],flush=True)
    return r

def main():
    for seed in (1874435642,1947282751):
        attempt=HERE/f'evaluate-attempt-{seed}.attempt.json'
        if attempt.exists():
            value=json.loads(attempt.read_text())
            value['source_sha256']=hashlib.sha256((HERE/'entry.c').read_bytes()).hexdigest()
            for stream in ('stdout','stderr'):
                value[stream+'_sha256']=hashlib.sha256((HERE/f'evaluate-attempt-{seed}.{stream}').read_bytes()).hexdigest()
            value.update(completed_evaluate_report=False, scores=None, kit_verdict=None,
                observation='The wrapper terminated the run group at its stated cap without a completed evaluator report; the pinned compare stage includes slow local incumbent remeasurement. This is a timeout observation, not a source rejection.')
            attempt.write_text(json.dumps(value,indent=2)+'\n')
    old=HERE/'packet.json'
    if old.exists():old.unlink()
    r=run('assemble',['python3','eik-work/trials/paired-control/verify.py','assemble',REL,'--source',SOURCE,
        '--logs','test/scratch/rv-exp-interval/cases/rv-exp-interval/logs','--status','measured','--note',NOTE])
    if r.returncode:raise SystemExit(r.returncode)
    r=run('summarize',['python3',REL+'/summarize.py'])
    if r.returncode:raise SystemExit(r.returncode)
    extra=run('verify-evidence',['python3',REL+'/verify-evidence.py'])
    checked=run('verify',['python3','eik-work/trials/paired-control/verify.py',REL])
    notes=('Tested exactly the requested early unsigned exp dispatch from id50. Source SHA-256 '
        '259751b6c7fd5072a081211b8a11f4e27a5d0e8bda9aaab666ae067dd20a0ea9. '
        'Gate accepted; normalised source and RV32 code differ; both Thumb loaded code/table sections are identical. '
        'Seeds 1874435642/1947282751: RV32 S 32.896202280/32.836443114 vs id50 28.522714242/28.517414314; '
        'ratios 1.1533335152/1.1514523285. Thumbv6M ratios 1/1; overall 1.0739336642/1.0730574675. '
        'Regression: keep id50 for integration. Affected calls save two conditional branches but cost +10 instructions; '
        'disassembly shows outlined nx_cell_r and an unconditional stack frame. Typical branch means improve; wide regress. '
        'All 2^32 inputs of each function passed GCC ASan+UBSan, zero mismatches. '
        'Targetcheck passed 19,922,944 exp words on each ISA, covering the full changed interval plus neighbors. '
        'Both quick seeds, scored/sample outputs, all-word dispatch proof and 1,098 guest boundary/midpoint cases pass. '
        'Both required evaluate commands hit the documented 180s local-incumbent remeasurement cap; '
        'unchanged measure/fullcheck stages provide full-population paired S. Current champion ratios null (HTTP 403 SOURCE_WITHHELD). '
        'Evidence in eik-work/trials/rv-exp-interval: entry.c, id50.diff, packet.json, comparison.json, EXPERIMENT.md, '
        'branch-counts.json, disassemblies, raw run logs, verify.stdout and verify-evidence.stdout. '
        'No hotkey registration, signing, submission or TAO spending. Next: separately test block placement that preserves inlining and the rare-path frame.')
    passed=checked.returncode==0 and extra.returncode==0
    if not passed:notes='Supplemental or packet verification failed; see raw verify*.stderr. Do not infer complete correctness from this packet until the failing verification is resolved. Scores and the one-change source are retained in packet.json; see comparison.json for observed coverage.'
    assert len(notes)<=2000
    result={'status':'done' if passed else 'stuck','check':{'exitCode':checked.returncode,
        'tail':(checked.stdout+checked.stderr)[-2000:]},'notes':notes}
    dest=ROOT/'artifacts/goal/batches/e03-kernel-trials/items/rv-exp-interval/result.json'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2)+'\n')
    paths=sorted(p for p in HERE.rglob('*') if p.is_file() and p.name!='evidence.sha256' and '__pycache__' not in p.parts)
    (HERE/'evidence.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(ROOT))+'\n' for p in paths))
    raise SystemExit(0 if passed else 1)

if __name__=='__main__':main()
