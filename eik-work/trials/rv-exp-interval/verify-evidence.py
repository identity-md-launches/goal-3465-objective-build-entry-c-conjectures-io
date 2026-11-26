#!/usr/bin/env python3
"""Validate the supplemental evidence in addition to paired-control/verify.py.
Checks recorded claims and hashes, not a replacement for rerunning the numerical checks.
"""
import difflib
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def load(name):return json.loads((HERE/name).read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    packet=load('packet.json'); sha=packet['source']['sha256']
    assert digest(HERE/'entry.c')==sha
    base=ROOT/packet['base']['path']; assert digest(base)==packet['base']['sha256']
    assert (HERE/'id50.diff').read_text()==''.join(difflib.unified_diff(base.read_text().splitlines(True), (HERE/'entry.c').read_text().splitlines(True),fromfile='id50/entry.c',tofile='rv-exp-interval/entry.c'))
    for name,h in load('offline-inputs.json')['files'].items():assert digest(ROOT/name)==h,name
    assert (HERE/'dispatch-proof.stdout').read_text().strip()=='words=4294967296 selected=16777216 mismatches=0'
    control=json.loads((ROOT/'eik-work/trials/paired-control/packet.json').read_text())
    branches=load('branch-counts.json'); assert branches['source_sha256']['candidate']==sha
    assert digest(HERE/'boundary-midpoint-inputs.txt')==branches['boundary_midpoint']['inputs_sha256']
    assert branches['boundary_midpoint']['count']==1098
    for target,tr in branches['targets'].items():
        assert all(s['boundary_midpoint_mismatches']==0 for s in tr['sources'].values())
        for seed,sr in tr['seeds'].items():
            report=load(f'measure-{seed}.stdout')
            assert report['images'][target]==load('compiled-image-metadata.json')[target]['candidate']['guest_elf_sha256']
            for cls,cr in sr.items():
                assert cr['sources']['candidate']['mean_instructions']==report['targets'][target]['functions']['exp'][cls]['mean']
                assert cr['sources']['id50']['mean_instructions']==control['index']['rows'][seed]['targets'][target]['functions']['exp']['means'][cls]
        r=load(f'targetcheck-{target}-exp-3063-3082.stdout')
        metadata=load('compiled-image-metadata.json')[target]
        assert metadata['candidate']['targetcheck_elf_sha256']==r['image_sha256']
        for kind in ('id50','candidate'):
            assert metadata[kind]['entry_object_sha256']==tr['sources'][kind]['object_sha256']
            assert metadata[kind]['guest_elf_sha256']==tr['sources'][kind]['guest_image_sha256']
        assert r['sha256']==sha and r['function']=='exp' and r['target']==target
        assert r['verdict']=='passed' and r['range_complete'] is True and r['complete'] is False
        assert r['words_checked']==19*(1<<20) and r['mismatches']==0
        assert (r['chunk_lo'],r['chunk_hi'])==(3063,3082)
    for fn in ('sigmoid','tanh','exp'):
        r=load(f'fullcheck-all-{fn}.stdout'); rec=load(f'fullcheck-all-{fn}.json')
        assert rec['exit_code']==0 and rec['source_sha256']==sha
        assert r['sha256']==sha and r['function']==fn and r['verdict']=='passed'
        assert r['complete'] is True and r['range_complete'] is True and r['quick'] is False
        assert r['words_checked']==1<<32 and r['mismatches']==0 and not r.get('sanitizer')
    for seed in packet['seeds']:
        label=f'evaluate-attempt-{seed}'
        attempt=HERE/(label+'.attempt.json')
        if attempt.exists():
            a=json.loads(attempt.read_text())
            assert a['command'][5:]==['evaluate',packet['source']['path'],'--quick','--json','--seed',str(seed)]
            assert a['timed_out'] is True and a['exit_code']<0 and a['timeout_seconds']==180
            assert a['source_sha256']==sha and a['scores'] is None and a['kit_verdict'] is None
            for stream in ('stdout','stderr'):assert digest(HERE/(label+'.'+stream))==a[stream+'_sha256']
        else:
            a=load(label+'.json'); r=load(label+'.stdout')
            assert a['exit_code']==0 and a['source_sha256']==sha and r['seed']==seed and r['sha256']==sha
    sections=load('loaded-section-hashes.json')
    assert sections['rv32im']['identical_allocated_sections'] is False
    assert sections['thumbv6m']['identical_allocated_sections'] is True
    assert sections['thumbv7em']['identical_allocated_sections'] is True
    print('PASS supplemental: exact diff; offline input hashes; all-word dispatch proof; guest boundary/midpoint outputs and branch means; 19 target chunks on each ISA; all 2^32 host inputs for all three functions under ASan+UBSan; Thumb code identity; both required bounded evaluate commands.')

if __name__=='__main__':main()
