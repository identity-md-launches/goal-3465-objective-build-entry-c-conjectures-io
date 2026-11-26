import sys
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32
from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection

for path in sys.argv[1:]:
    with open(path,'rb') as file:
        elf = ELFFile(file)
        symtab = elf.get_section_by_name('.symtab')
        (fn,) = symtab.get_symbol_by_name('eik_exp')
        sec = elf.get_section(fn['st_shndx'])
        off = fn['st_value'] - sec['sh_addr']
        rels = {}
        for relocations in elf.iter_sections():
            if isinstance(relocations, RelocationSection) and relocations['sh_info'] == fn['st_shndx']:
                for r in relocations.iter_relocations():
                    sym = symtab.get_symbol(r['r_info_sym'])
                    name = sym.name or str(sym['st_shndx'])
                    rels.setdefault(r['r_offset'], []).append(f"{r['r_info_type']}:{name}+{r.entry.get('r_addend',0)}")
        print(f"eik_exp: {fn['st_size']} bytes")
        decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32)
        for i in decoder.disasm(sec.data()[off:off+fn['st_size']], fn['st_value']):
            print(f"{i.address:05x} {i.mnemonic:6} {i.op_str:28} {', '.join(rels.get(i.address, []))}".rstrip())
