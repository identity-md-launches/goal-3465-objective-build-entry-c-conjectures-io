#!/usr/bin/env python3
"""Compare loaded sections and disassemble code with ARM mapping-symbol literal pools."""
import hashlib
import json
import capstone as cs
from pathlib import Path
from elftools.elf.elffile import ELFFile

root=Path(__file__).resolve().parents[3]
trial=Path(__file__).resolve().parent
build=root/'test/scratch/rv-exp-interval/cases/rv-exp-interval/build'
sources={'id50':root/'eik-work/baselines/former-50/entry.c','candidate':trial/'entry.c'}
out={}
image_sizes={}
for target in ('rv32im','thumbv6m','thumbv7em'):
    tr=out[target]={}
    sizes=image_sizes[target]={}
    for kind,source in sources.items():
        prefix=hashlib.sha256(source.read_bytes()).hexdigest()[:16]
        image=next(build.glob(f'{prefix}-*/guest-{target}.elf'))
        with image.open('rb') as f:
            elf=ELFFile(f)
            tr[kind]={s.name:{'bytes':s['sh_size'],'sha256':hashlib.sha256(s.data()).hexdigest()}
                      for s in elf.iter_sections() if s['sh_flags'] & 2 and s['sh_type']!='SHT_NOBITS'}
            sizes[kind]={'guest_elf_file_bytes':image.stat().st_size,
                'guest_elf_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),
                'guest_allocated_section_bytes':sum(v['bytes'] for v in tr[kind].values()),
                'entry_object_file_bytes':(image.parent/f'sub-{target}.o').stat().st_size,
                'entry_object_sha256':hashlib.sha256((image.parent/f'sub-{target}.o').read_bytes()).hexdigest()}
            checker=image.parent/f'target-check-{target}.elf'
            if checker.exists():
                sizes[kind]['targetcheck_elf_file_bytes']=checker.stat().st_size
                sizes[kind]['targetcheck_elf_sha256']=hashlib.sha256(checker.read_bytes()).hexdigest()
            # ARM $t/$d mapping symbols separate instructions from embedded literal pools.
            symbols=list(elf.get_section_by_name('.symtab').iter_symbols())
            funcs={s['st_value'] & ~1:s.name for s in symbols if s['st_info']['type']=='STT_FUNC'}
            dis=cs.Cs(cs.CS_ARCH_RISCV,cs.CS_MODE_RISCV32|cs.CS_MODE_RISCVC) if target=='rv32im' else cs.Cs(cs.CS_ARCH_ARM,cs.CS_MODE_THUMB|cs.CS_MODE_MCLASS)
            lines=['; Allocated executable sections; ARM mapping-symbol literal pools are data.']
            for ix,section in enumerate(elf.iter_sections()):
                if not (section['sh_flags'] & 4) or not section['sh_size']:continue
                start=section['sh_addr']; stop=start+section['sh_size']; data=section.data()
                cuts={start:'code',stop:'end'}
                for sym in symbols:
                    if sym['st_shndx']==ix and sym.name.startswith(('$t','$d','$x')):
                        cuts[sym['st_value']]='data' if sym.name.startswith('$d') else 'code'
                points=sorted(cuts)
                for lo,hi in zip(points,points[1:]):
                    if cuts[lo]=='code':
                        decoded=list(dis.disasm_lite(data[lo-start:hi-start],lo))
                        for addr,n,mn,ops in decoded:
                            if addr in funcs:lines.append('\n'+funcs[addr]+':')
                            lines.append(f'{addr:08x}: {mn:10s} {ops}')
                        lo=decoded[-1][0]+decoded[-1][1] if decoded else lo
                    while lo<hi:
                        width=min(4,hi-lo)
                        value=int.from_bytes(data[lo-start:lo-start+width],'little')
                        name={4:'.word',3:'.3byte',2:'.hword',1:'.byte'}[width]
                        lines.append(f'{lo:08x}: {name:10s} 0x{value:0{width*2}x}')
                        lo+=width
            (trial/f'{kind}-{target}.asm').write_text('\n'.join(lines)+'\n')
    tr['identical_allocated_sections']=tr['id50']==tr['candidate']
(trial/'loaded-section-hashes.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
(trial/'compiled-image-metadata.json').write_text(json.dumps(image_sizes,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
