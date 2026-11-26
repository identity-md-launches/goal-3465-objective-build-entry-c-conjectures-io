#!/usr/bin/env python3
"""Supplemental branch counts, disassembly and boundary checks using the kit's compiled guest code.
Run with scratch runtime, PYTHONPATH=the unmodified scratch kit, EIK_BUILD_DIR=its build.
This instrumentation does not feed S; unmodified run.py provides all scored evidence.
"""
import hashlib
import json
from pathlib import Path
import sys
from elftools.elf.elffile import ELFFile
from eik import config as K, toolchain as T, inputs as I, reference as R
from eik.emu import Core

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCES = {'id50': ROOT/'eik-work/baselines/former-50/entry.c', 'candidate': OUT/'entry.c'}
SEEDS = (1874435642,1947282751)

class BranchCore(Core):
    def __init__(self, *a):
        super().__init__(*a)
        self.branch_blocks = {}
        self.branches = 0
    def _block(self,u,addr,size,data):
        super()._block(u,addr,size,data)
        key = (addr,size)
        if key not in self.branch_blocks:
            ins = list(self.dis.disasm_lite(bytes(u.mem_read(addr,size)),addr))
            names = {'beq','bne','blt','bge','bltu','bgeu','beqz','bnez','blez','bgez','bltz','bgtz'} if self.target == 'rv32im' else {'beq','bne','bhs','blo','bmi','bpl','bvs','bvc','bhi','bls','bge','blt','bgt','ble','cbz','cbnz'}
            self.branch_blocks[key] = sum(m.split('.')[0] in names or (self.target != 'rv32im' and m.startswith('bx') and m[2:] in {'eq','ne','hs','lo','mi','pl','vs','vc','hi','ls','ge','lt','gt','le'}) for _,_,m,_ in ins)
        self.branches += self.branch_blocks[key]
    def call_with_branches(self, fn, word):
        self.branches = 0
        value, instructions = self.call(fn,word)
        return value,instructions,self.branches

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def affected(w): return 0xbf800001 <= w <= 0xc0800000

def main():
    report = {'source_sha256':{k:sha(v) for k,v in SOURCES.items()}, 'branch_definition':'Conditional branch instructions in executed translated blocks for the entire eik_exp call, including refinements, matching the kit block accounting. Width suffixes are ignored and conditional BX is counted; unconditional jumps/calls/returns excluded.', 'targets':{}, 'seeds':SEEDS}
    # Cell boundaries, endpoints and immediate neighbors; fractions inside each cell.
    words = set([0,0x80000000,0x7f800000,0xff800000,0x7f800001,0xff800001])
    for edge in range(0xbf800000,0xc0800001,1<<17):
        for off in (-2,-1,0,1,2,0xffff,0x10000,0x10001):
            words.add(edge+off)
    # All fresh near-midpoints in the changed range plus neighbors; retain exact list.
    midpoint_counts = {}
    for seed in SEEDS:
        I.prepare_fresh_pools(seed)
        hard = [w for w in I.hard_pool('exp',seed) if affected(w)]
        midpoint_counts[str(seed)] = len(hard)
        for w in hard:
            words.update([w-1,w,w+1])
    words = sorted(words)
    (OUT/'boundary-midpoint-inputs.txt').write_text(''.join(f'{w:08x}\n' for w in words))
    want = R.outputs('exp',words)
    report['boundary_midpoint'] = {'count':len(words),'affected_fresh_hard_pool_words':midpoint_counts,'inputs_sha256':sha(OUT/'boundary-midpoint-inputs.txt')}
    for target in K.TARGETS:
        tr = report['targets'][target] = {'sources':{},'seeds':{}}
        cores = {}
        for kind,src in SOURCES.items():
            image = T.guest_image(src,target)
            core = cores[kind] = BranchCore(image,target)
            with image.open('rb') as f:
                elf = ELFFile(f)
                symbols = elf.get_section_by_name('.symtab')
                sym = symbols.get_symbol_by_name('eik_exp')[0]
                address = sym['st_value'] & ~1
                size = sym['st_size']
                code = bytes(core.u.mem_read(address,size))
                # RV's selected r helper may be outlined. Keep all executable sections for inspection.
                lines = []
                funcs = {s['st_value'] & ~1:s.name for s in symbols.iter_symbols() if s['st_info']['type']=='STT_FUNC'}
                for section in elf.iter_sections():
                    if section['sh_flags'] & 4 and section['sh_size']:
                        for addr,n,mn,ops in core.dis.disasm_lite(section.data(),section['sh_addr']):
                            if addr in funcs: lines.append('\n'+funcs[addr]+':')
                            lines.append(f'{addr:08x}: {mn:10s} {ops}')
            (OUT/f'{kind}-{target}.asm').write_text('\n'.join(lines)+'\n')
            got = core.batch('exp',words)
            errors = [dict(input=f'{w:08x}',got=f'{g:08x}',want=f'{e:08x}') for w,g,e in zip(words,got,want) if g!=e]
            tr['sources'][kind] = {'guest_image_sha256':sha(image),'object_sha256':sha(T.object_file(src,target)), 'eik_exp_machine_code_sha256':hashlib.sha256(code).hexdigest(),'eik_exp_bytes':size,'boundary_midpoint_mismatches':len(errors),'examples':errors[:8]}
            assert not errors
        for seed in SEEDS:
            sr = tr['seeds'][str(seed)] = {}
            for cls, ws in I.draw(seed,'exp').items():
                cr = sr[cls] = {'n':len(ws),'affected_n':sum(affected(w) for w in ws),'sources':{}}
                expected = R.outputs('exp',ws)
                for kind,core in cores.items():
                    data = [core.call_with_branches('exp',w) for w in ws]
                    assert [v[0] for v in data] == expected
                    aff = [v for w,v in zip(ws,data) if affected(w)]
                    cr['sources'][kind] = {'conditional_branch_sum':sum(v[2] for v in data),'mean_conditional_branches':sum(v[2] for v in data)/len(ws),'mean_instructions':sum(v[1] for v in data)/len(ws),'affected_mean_conditional_branches':sum(v[2] for v in aff)/len(aff) if aff else None,'affected_mean_instructions':sum(v[1] for v in aff)/len(aff) if aff else None}
        tr['identical_guest_image'] = tr['sources']['id50']['guest_image_sha256']==tr['sources']['candidate']['guest_image_sha256']
        print(target,json.dumps(tr['sources']),flush=True)
    (OUT/'branch-counts.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('PASS boundaries, near-midpoints, outputs and branch instrumentation',flush=True)

if __name__ == '__main__': main()
