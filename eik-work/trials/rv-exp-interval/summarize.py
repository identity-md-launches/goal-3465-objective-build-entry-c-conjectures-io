#!/usr/bin/env python3
"""Generate comparison tables from raw, unchanged pinned-runner records."""
import csv
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
CONTROL=ROOT/'eik-work/trials/paired-control'
SEEDS=(1874435642,1947282751)
TARGETS=('rv32im','thumbv6m','thumbv7em')
BOARDS=('rv32im','thumbv6m','overall')

def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    packet=read(OUT/'packet.json'); control=read(CONTROL/'packet.json')
    branches=read(OUT/'branch-counts.json')
    sections=read(OUT/'loaded-section-hashes.json')
    result={'experiment':'One early unsigned interval dispatch in eik_exp_r; all arithmetic and the selector are unchanged.',
            'source_sha256':packet['source']['sha256'], 'normalised_sha256':packet['index']['normalised_sha256'],
            'id50_sha256':control['source']['sha256'], 'id50_normalised_sha256':control['index']['normalised_sha256'],
            'status':'measured-regression', 'gate':'accepted', 'recommended_source':control['source'], 'duplicate_normalised_source':False,
            'current_champion_scores':{s:{b:None for b in BOARDS} for s in map(str,SEEDS)},
            'current_champion_ratios':{s:{b:None for b in BOARDS} for s in map(str,SEEDS)},
            'would_take_current_boards':None, 'would_beat_id50_by_three_percent':[],
            'rows':{}, 'correctness':{}, 'compiled_code':sections,
            'next':'Do not merge this optimisation into the best entry. A future dispatch experiment should preserve nx_cell_r inlining and shrink-wrapped rare-path stack frames, without altering selectors or arithmetic.'}
    scores=[]; metrics=[]
    for s in map(str,SEEDS):
        ca=packet['index']['rows'][s]; base=control['index']['rows'][s]
        row=result['rows'][s]={'inputs_sha256':ca['inputs_sha256'],'hard_pool_sizes':ca['hard_pool_sizes'],'boards':{},'targets':{}}
        for b in BOARDS:
            v={'id50_S':base['S'][b],'candidate_S':ca['S'][b],'candidate_over_id50':ca['S'][b]/base['S'][b]}
            row['boards'][b]=v; scores.append({'seed':s,'board':b,**v})
        for t in TARGETS:
            bt=base['targets'][t]; ct=ca['targets'][t]
            x=row['targets'][t]={'id50_bytes':bt['bytes'],'candidate_bytes':ct['bytes'],'id50_stack_bound':bt['stack_bound'],
                'candidate_stack_bound':ct['stack_bound'],'id50_peak_stack':bt['stack'],'candidate_peak_stack':ct['stack'],
                'id50_size_factor':bt['size_factor'],'candidate_size_factor':ct['size_factor'],'exp':{}}
            for c in ('typical','wide','hard','uniform'):
                v={'id50_mean':bt['functions']['exp']['means'][c],'candidate_mean':ct['functions']['exp']['means'][c],
                   'n':ct['functions']['exp']['n'][c], 'branches':branches['targets'][t]['seeds'][s][c]}
                x['exp'][c]=v
                metrics.append({'seed':s,'target':t,'function':'exp','class':c,'n':v['n'],'id50_mean':v['id50_mean'],
                    'candidate_mean':v['candidate_mean'],'ratio':v['candidate_mean']/v['id50_mean'],
                    'id50_branch_mean':v['branches']['sources']['id50']['mean_conditional_branches'],
                    'candidate_branch_mean':v['branches']['sources']['candidate']['mean_conditional_branches']})
            x['hard_tail']={'id50_p999':bt['functions']['exp']['hard_p999'],'candidate_p999':ct['functions']['exp']['hard_p999'],
                            'id50_factor':bt['functions']['exp']['tail_factor'],'candidate_factor':ct['functions']['exp']['tail_factor']}
            x['correctness']={k:ct[k] for k in ('sample_words','sample_mismatches','wrong')}
            x['sigmoid_tanh_means_unchanged']=all(ct['functions'][f]==bt['functions'][f] for f in ('sigmoid','tanh'))
    result['correctness']['quick_host_check']={s:packet['index']['rows'][s]['quick_host_check'] for s in map(str,SEEDS)}
    result['correctness']['boundary_midpoint']=branches['boundary_midpoint']
    result['correctness']['dispatch_predicate_exhaustive']=(OUT/'dispatch-proof.stdout').read_text().strip()
    result['correctness']['selected_target_chunks']={}
    for t in TARGETS:
        p=OUT/f'targetcheck-{t}-exp-3063-3082.stdout'
        if p.exists():
            a=read(p); result['correctness']['selected_target_chunks'][t]={k:a[k] for k in ('verdict','image_sha256','words_checked','mismatches','chunk_lo','chunk_hi','complete','range_complete')}
    result['correctness']['complete_host_checks']={}
    for f in ('sigmoid','tanh','exp'):
        p=OUT/f'fullcheck-all-{f}.stdout'
        result['correctness']['complete_host_checks'][f]=read(p) if p.exists() else None
    result['evaluate_attempts']={}
    for s in map(str,SEEDS):
        p=OUT/f'evaluate-attempt-{s}.attempt.json'
        result['evaluate_attempts'][s]=read(p) if p.exists() else (read(OUT/f'evaluate-attempt-{s}.json') if (OUT/f'evaluate-attempt-{s}.json').exists() else None)
    for name,data in [('scores.csv',scores),('exp-class-means.csv',metrics)]:
        with (OUT/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0])); writer.writeheader(); writer.writerows(data)
    (OUT/'comparison.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('summarized scores, class means, tails, sizes/stacks, branches and correctness')

if __name__=='__main__':main()
