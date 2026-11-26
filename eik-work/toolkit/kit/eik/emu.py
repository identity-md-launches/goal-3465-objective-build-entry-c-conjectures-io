"""Emulated bare-metal cores (Unicorn): count retired instructions per call, run batches at full
speed for the target-side correctness sample, and measure peak stack use.

Counting: a block hook adds the number of instructions in each translated block (disassembled once
with capstone). The same image and input always give the same count."""
import struct

import capstone as cs
import unicorn as uc
from elftools.elf.elffile import ELFFile
from unicorn import arm_const as A
from unicorn import riscv_const as R

from . import config as K

RAM, RAM_SIZE, MAGIC = 0x2000_0000, 0x0100_0000, 0x0FFF_F000
STACK_TOP = RAM + 0x00FF_FF00
STACK_PROBE = 64 * 1024        # bytes below the stack top filled with a pattern to find peak use
PATTERN = b"\xa5" * STACK_PROBE
BUF_IN, BUF_OUT = RAM + 0x0010_0000, RAM + 0x0060_0000  # batch buffers, up to 1M words each


class Timeout(Exception):
    pass


class Core:
    def __init__(self, image, target):
        self.target = target
        with open(image, "rb") as f:
            elf = ELFFile(f)
            self.sym = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols() if s.name}
            if target == "rv32im":
                self.u = uc.Uc(uc.UC_ARCH_RISCV, uc.UC_MODE_RISCV32)
                self.dis = cs.Cs(cs.CS_ARCH_RISCV, cs.CS_MODE_RISCV32 | cs.CS_MODE_RISCVC)
            else:
                self.u = uc.Uc(uc.UC_ARCH_ARM, uc.UC_MODE_THUMB | uc.UC_MODE_MCLASS)
                self.u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M0 if target == "thumbv6m" else A.UC_CPU_ARM_CORTEX_M4)
                self.dis = cs.Cs(cs.CS_ARCH_ARM, cs.CS_MODE_THUMB | cs.CS_MODE_MCLASS)
            for seg in elf.iter_segments():
                if seg["p_type"] != "PT_LOAD" or seg["p_memsz"] == 0:
                    continue
                lo = seg["p_vaddr"] & ~0xFFF
                hi = (seg["p_vaddr"] + seg["p_memsz"] + 0xFFF) & ~0xFFF
                for page in range(lo, hi, 0x1000):
                    try:
                        self.u.mem_map(page, 0x1000)
                    except uc.UcError:
                        pass  # already mapped by a neighbouring segment
                self.u.mem_write(seg["p_vaddr"], seg.data())
        self.u.mem_map(RAM, RAM_SIZE)
        self.u.mem_map(MAGIC, 0x1000)
        self.u.mem_write(STACK_TOP - STACK_PROBE, PATTERN)
        self.blocks, self.count, self.hook = {}, 0, None

    # -- counting ---------------------------------------------------------------------------
    def _block(self, u, addr, size, _):
        n = self.blocks.get((addr, size))
        if n is None:
            n = sum(1 for _ in self.dis.disasm_lite(bytes(u.mem_read(addr, size)), addr))
            self.blocks[(addr, size)] = n
        self.count += n
        if self.count > K.CAP_INSTR_PER_CALL:
            u.emu_stop()

    def _counting(self, on):
        # Unicorn keeps the blocks it has translated, with the hooks they were translated under, so
        # the cache is flushed whenever the hook changes: otherwise blocks translated during a batch
        # (no hook) would count 0 instructions in a later call.
        if on and self.hook is None:
            self.hook = self.u.hook_add(uc.UC_HOOK_BLOCK, self._block)
            self.u.ctl_flush_tb()
        elif not on and self.hook is not None:
            self.u.hook_del(self.hook)
            self.hook = None
            self.u.ctl_flush_tb()

    def _call(self, addr, args, limit=0):
        u = self.u
        if self.target == "rv32im":
            for i, v in enumerate(args):
                u.reg_write(R.UC_RISCV_REG_A0 + i, v & 0xFFFFFFFF)
            u.reg_write(R.UC_RISCV_REG_SP, STACK_TOP)
            u.reg_write(R.UC_RISCV_REG_RA, MAGIC)
            start, ret = addr, R.UC_RISCV_REG_A0
            pc = R.UC_RISCV_REG_PC
        else:
            for r, v in zip([A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2, A.UC_ARM_REG_R3], args):
                u.reg_write(r, v & 0xFFFFFFFF)
            u.reg_write(A.UC_ARM_REG_SP, STACK_TOP)
            u.reg_write(A.UC_ARM_REG_LR, MAGIC | 1)
            start, ret = addr | 1, A.UC_ARM_REG_R0
            pc = A.UC_ARM_REG_PC
        u.emu_start(start, MAGIC, count=limit)
        if (u.reg_read(pc) & ~1) != MAGIC:
            raise Timeout(f"did not return within {K.CAP_INSTR_PER_CALL} instructions")
        return u.reg_read(ret) & 0xFFFFFFFF

    def call(self, fn, x):
        """(result, retired instructions) of eik_<fn>(x)."""
        self._counting(True)
        self.count = 0
        r = self._call(self.sym[f"eik_{fn}"], [x])
        return r, self.count

    def batch(self, fn, words, *, direct=False):
        """Outputs without instruction counting. Direct calls exclude the batch wrapper's stack
        when measuring a submission's stack use on the correctness sample."""
        self._counting(False)
        if direct:
            return [self._call(self.sym[f"eik_{fn}"], [w], limit=K.CAP_INSTR_PER_CALL) for w in words]
        out = []
        for i in range(0, len(words), 1 << 20):
            part = words[i:i + (1 << 20)]
            self.u.mem_write(BUF_IN, struct.pack(f"<{len(part)}I", *part))
            self._call(self.sym["eik_batch"], [K.FUNCTIONS.index(fn), BUF_IN, BUF_OUT, len(part)])
            out += struct.unpack(f"<{len(part)}I", self.u.mem_read(BUF_OUT, 4 * len(part)))
        return out

    def peak_stack(self):
        """Bytes of stack ever used since the core was created (pattern scan)."""
        mem = bytes(self.u.mem_read(STACK_TOP - STACK_PROBE, STACK_PROBE))
        i = 0
        while i < len(mem) and mem[i] == 0xA5:
            i += 1
        return STACK_PROBE - i
