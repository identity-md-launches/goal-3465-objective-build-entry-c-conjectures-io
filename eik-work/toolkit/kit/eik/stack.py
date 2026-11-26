"""Conservative stack bound for the linked guest, independent of test inputs.

Source policy excludes recursion, indirect calls, assembly and dynamic allocation.
Sum every fixed compiler frame, including disjoint paths, once. Trusted runtime
functions lacking metadata are checked for bounded stack adjustments and an
acyclic call graph. Unknown adjustments fail closed.
"""
import io

import capstone as CS
from elftools.common.utils import struct_parse
from elftools.elf.elffile import ELFFile


class UnboundedStack(ValueError):
    pass


def _functions(elf):
    functions = {}
    for symbol in elf.get_section_by_name('.symtab').iter_symbols():
        if symbol['st_info']['type'] == 'STT_FUNC' and isinstance(symbol['st_shndx'], int):
            address = symbol['st_value'] & ~1
            functions.setdefault(address, symbol)
    return functions


def _frames(elf):
    section = elf.get_section_by_name('.stack_sizes')
    if section is None:
        raise UnboundedStack('compiler stack-size metadata is missing')
    stream = io.BytesIO(section.data())
    frames = {}
    while stream.tell() < section['sh_size']:
        address = struct_parse(elf.structs.Elf_addr(''), stream) & ~1
        value = struct_parse(elf.structs.Elf_uleb128(''), stream)
        if address in frames and frames[address] != value:
            raise UnboundedStack('conflicting stack-size metadata')
        frames[address] = value
    return frames


def _mapping(elf):
    """ARM mapping symbols: (address, kind) sorted, kind 't' for Thumb code and 'd' for data.

    Runtime routines keep literal pools between their instructions; only `$t` ranges are code."""
    marks = []
    for symbol in elf.get_section_by_name('.symtab').iter_symbols():
        name = symbol.name
        if name in ('$t', '$d', '$a') or name.startswith(('$t.', '$d.', '$a.')):
            marks.append((symbol['st_value'], name[1]))
    return sorted(marks)


def _code_ranges(start, end, marks):
    """The [lo, hi) code ranges of a Thumb routine at [start, end), from the mapping symbols."""
    kind = 't'
    for address, k in marks:  # the mark in force at `start`
        if address <= start:
            kind = k
        else:
            break
    cuts = [(a, k) for a, k in marks if start < a < end]
    ranges, lo = [], start
    for address, k in cuts + [(end, None)]:
        if kind == 't' and address > lo:
            ranges.append((lo, address))
        if kind == 'a':
            raise UnboundedStack('ARM-state runtime code')
        lo, kind = address, k
    return ranges


def _auipc_jalr(auipc, offset):
    """The target of `auipc r, hi; jalr .., r, lo`. Capstone gives the 20-bit `hi` unsigned."""
    hi = auipc.operands[1].imm & 0xFFFFF
    if hi & 0x80000:
        hi -= 1 << 20
    return (auipc.address + (hi << 12) + offset) & 0xFFFFFFFF


def _runtime_frame(elf, symbol, target, runtime_addresses, marks=()):
    arm = target != 'rv32im'
    dis = (CS.Cs(CS.CS_ARCH_ARM, CS.CS_MODE_THUMB | CS.CS_MODE_MCLASS) if arm
           else CS.Cs(CS.CS_ARCH_RISCV, CS.CS_MODE_RISCV32))
    dis.detail = True
    address = symbol['st_value'] & ~1
    section = elf.get_section(symbol['st_shndx'])
    offset = address - section['sh_addr']
    code = section.data()[offset:offset + symbol['st_size']]
    if not code:
        raise UnboundedStack(f'cannot decode runtime {symbol.name}')
    # Thumb: decode the code ranges only, skipping literal pools; RISC-V routines have none.
    ranges = _code_ranges(address, address + len(code), marks) if arm else [(address, address + len(code))]
    instructions = []
    for lo, hi in ranges:
        part = list(dis.disasm(code[lo - address:hi - address], lo))
        if sum(i.size for i in part) != hi - lo:
            raise UnboundedStack(f'cannot decode runtime {symbol.name}')
        instructions += part
    allocated, allocations, branches, calls = 0, [], [], set()
    previous = None
    for ins in instructions:
        mnemonic, operands = ins.mnemonic, ins.operands
        immediate = CS.arm.ARM_OP_IMM if arm else CS.riscv.RISCV_OP_IMM
        delta = 0
        if arm:
            writes_sp = CS.arm.ARM_REG_SP in ins.regs_access()[1]
            if ins.id == CS.arm.ARM_INS_PUSH:
                delta = 4 * len(operands)
            elif ins.id == CS.arm.ARM_INS_POP:
                if any(op.reg == CS.arm.ARM_REG_SP for op in operands):
                    raise UnboundedStack('runtime pop writes an unknown stack pointer')
            elif writes_sp:
                # sub/add sp, #imm (Thumb) or sub.w/add.w sp, sp, #imm (Thumb-2)
                if (ins.id in (CS.arm.ARM_INS_SUB, CS.arm.ARM_INS_ADD) and operands[0].reg == CS.arm.ARM_REG_SP
                        and operands[-1].type == immediate
                        and (len(operands) == 2 or operands[1].reg == CS.arm.ARM_REG_SP)):
                    delta = operands[-1].imm if ins.id == CS.arm.ARM_INS_SUB else 0
                else:
                    raise UnboundedStack(f'unknown runtime stack adjustment: {mnemonic} {ins.op_str}')
            if ins.group(CS.CS_GRP_JUMP) or ins.group(CS.CS_GRP_CALL):
                if operands[-1].type == immediate:
                    branches.append((ins.address, operands[-1].imm & ~1))
                elif ins.id != CS.arm.ARM_INS_BX or ins.op_str != 'lr':
                    raise UnboundedStack('indirect runtime branch')
        else:
            # RISC-V stores read their first operand; all other explicit writes to sp
            # must be a fixed addi. Compressed instructions are disabled for RV32IM.
            if operands and operands[0].type == CS.riscv.RISCV_OP_REG and operands[0].reg == CS.riscv.RISCV_REG_SP:
                if mnemonic == 'addi' and operands[1].reg == CS.riscv.RISCV_REG_SP:
                    delta = max(0, -operands[2].imm)
                elif mnemonic not in ('sw', 'sh', 'sb'):
                    raise UnboundedStack(f'unknown runtime stack adjustment: {mnemonic} {ins.op_str}')
            if mnemonic == 'jalr':
                if (previous is None or previous.mnemonic != 'auipc' or len(operands) != 3
                        or previous.operands[0].reg != operands[1].reg):
                    raise UnboundedStack('unresolved runtime jalr')
                dest = _auipc_jalr(previous, operands[2].imm)
                branches.append((ins.address, dest & ~1))
            elif mnemonic == 'jr':
                if ins.op_str != 'ra':
                    raise UnboundedStack('indirect runtime branch')
            elif mnemonic.startswith('b') or mnemonic in ('j', 'jal'):
                if operands[-1].type != immediate:
                    raise UnboundedStack('unresolved runtime branch')
                branches.append((ins.address, ins.address + operands[-1].imm))
        if delta:
            allocated += delta
            allocations.append(ins.address)
        previous = ins
    end = address + len(code)
    for origin, destination in branches:
        if address <= destination < end:
            if not any(lo <= destination < hi for lo, hi in ranges):
                raise UnboundedStack('runtime branch into data')
            if any(destination <= allocation <= origin for allocation in allocations):
                raise UnboundedStack('runtime loop can repeat a stack allocation')
        elif destination in runtime_addresses:
            calls.add(destination)  # any function start: its frame is in the sum too
        else:
            raise UnboundedStack('runtime branches outside the certified runtime')
    return allocated, calls


def _calls(elf, symbol, target, starts, marks=()):
    """The functions a compiled submission function calls or tail-calls, from its machine code.

    The source policy forbids function pointers, indirect calls and recursion; this is the same
    rule on the code that runs, where calls into compiler helpers and back (a miner's memset that
    the compiler lowers to __aeabi_memclr, which calls memset) are visible. Every control transfer
    must be a direct branch inside the function, a direct call to a function start, or a return;
    anything else fails closed. -fno-jump-tables keeps `switch` from compiling to an indirect jump."""
    arm = target != 'rv32im'
    dis = (CS.Cs(CS.CS_ARCH_ARM, CS.CS_MODE_THUMB | CS.CS_MODE_MCLASS) if arm
           else CS.Cs(CS.CS_ARCH_RISCV, CS.CS_MODE_RISCV32))
    dis.detail = True
    address = symbol['st_value'] & ~1
    section = elf.get_section(symbol['st_shndx'])
    code = section.data()[address - section['sh_addr']:address - section['sh_addr'] + symbol['st_size']]
    end = address + len(code)
    ranges = _code_ranges(address, end, marks) if arm else [(address, end)]
    calls, previous = set(), None
    for lo, hi in ranges:
        part = list(dis.disasm(code[lo - address:hi - address], lo))
        if sum(i.size for i in part) != hi - lo:
            raise UnboundedStack(f'cannot decode {symbol.name}')
        for ins in part:
            dest = None
            if arm:
                writes_pc = CS.arm.ARM_REG_PC in ins.regs_access()[1]
                branch = ins.group(CS.CS_GRP_JUMP) or ins.group(CS.CS_GRP_CALL) or writes_pc
                if not branch:
                    continue
                last = ins.operands[-1] if ins.operands else None
                if (ins.id == CS.arm.ARM_INS_BX and ins.op_str == 'lr') or ins.id == CS.arm.ARM_INS_POP:
                    continue  # a return, conditional or not
                if last is None or last.type != CS.arm.ARM_OP_IMM or ins.id in (
                        CS.arm.ARM_INS_TBB, CS.arm.ARM_INS_TBH, CS.arm.ARM_INS_LDR, CS.arm.ARM_INS_MOV,
                        CS.arm.ARM_INS_BLX):
                    raise UnboundedStack(f'indirect control transfer in {symbol.name}: {ins.mnemonic} {ins.op_str}')
                dest = last.imm & ~1
            else:
                m, ops = ins.mnemonic, ins.operands
                if m in ('ret',) or (m == 'jr' and ins.op_str == 'ra'):
                    pass
                elif m == 'jalr':
                    if (previous is None or previous.mnemonic != 'auipc' or len(ops) != 3
                            or previous.operands[0].reg != ops[1].reg):
                        raise UnboundedStack(f'indirect call in {symbol.name}')
                    dest = _auipc_jalr(previous, ops[2].imm)
                elif m in ('jr', 'c.jr', 'c.jalr'):
                    raise UnboundedStack(f'indirect jump in {symbol.name}: {m} {ins.op_str}')
                elif m.startswith('b') or m in ('j', 'jal'):
                    if not ops or ops[-1].type != CS.riscv.RISCV_OP_IMM:
                        raise UnboundedStack(f'unresolved branch in {symbol.name}')
                    dest = ins.address + ops[-1].imm
                previous = ins
            if dest is None:
                continue
            if address <= dest < end:
                if not any(lo2 <= dest < hi2 for lo2, hi2 in ranges):
                    raise UnboundedStack(f'branch into data in {symbol.name}')
            elif dest in starts:
                calls.add(dest)
            else:
                raise UnboundedStack(f'{symbol.name} branches outside every function')
    return calls


def bound(image, obj, target):
    with open(obj, 'rb') as stream:
        source_names = {s.name for s in ELFFile(stream).get_section_by_name('.symtab').iter_symbols()
                        if s['st_info']['type'] == 'STT_FUNC' and isinstance(s['st_shndx'], int)}
    with open(image, 'rb') as stream:
        elf = ELFFile(stream)
        functions, frames = _functions(elf), _frames(elf)
        marks = _mapping(elf) if target != 'rv32im' else []
        runtime = set(functions) - set(frames)
        graph = {}
        for address in runtime:
            symbol = functions[address]
            if symbol.name in source_names:
                raise UnboundedStack(f'no fixed stack bound for {symbol.name}')
            frames[address], graph[address] = _runtime_frame(elf, symbol, target, set(functions), marks)
        for address in set(frames) - runtime:
            if address not in functions:
                raise UnboundedStack('stack-size metadata for code without a function symbol')
            graph[address] = _calls(elf, functions[address], target, set(functions), marks)
        # No cycle through submission code or runtime routines: each frame is counted once.
        # Kahn's algorithm avoids Python recursion limits even on a maliciously large symbol table.
        pending = dict(graph)
        while pending:
            leaves = {node for node, edges in pending.items() if not edges & pending.keys()}
            if not leaves:
                raise UnboundedStack('recursive calls in the compiled code')
            for node in leaves:
                del pending[node]
        if not set(functions) <= frames.keys():
            raise UnboundedStack('incomplete function stack coverage')
        return sum(frames[address] for address in functions)
