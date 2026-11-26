"""Check table derivation and trace the scored Thumb ELF on representative inputs."""
import argparse
import re
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import sys

from elftools.elf.elffile import ELFFile
import unicorn as uc

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "eik-work/toolkit/kit"))
from eik.emu import Core  # noqa: E402

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("base_image", type=Path)
parser.add_argument("candidate_image", type=Path)
parser.add_argument("--rv-images", nargs=2, type=Path, metavar=("BASE", "CANDIDATE"))
args = parser.parse_args()
base = (ROOT / "eik-work/baselines/former-50/entry.c").read_text()
candidate = Path(__file__).with_name("entry.c").read_text()


def rows(source, declaration):
    table = source.split(declaration, 1)[1].split("};", 1)[0]
    return [tuple(map(int, re.findall(r"(\d+)u", row))) for row in re.findall(r"{([^{}]+)}", table)]


packed = rows(base, "static const struct t_ep t_eps[]={")
assert rows(candidate, "static const struct t_ep t_eps[]={") == packed
narrow = rows(candidate, "static const struct t_sigmoid_cell t_sigmoid_negative[91] = {")
assert narrow == [(q, v, p, p & 65535, q & 255) for q, v, p, aux in packed[384:475]]
print("All 91 narrow rows match id50. All shared rows are byte-for-byte equivalent as integer fields.")


def intermediate(w):
    q, v, p, _ = packed[384 + ((w >> 16) & 127)]
    f = w & 65535
    mask = (1 << 32) - 1
    b = ((p - (q & 255) * f) & mask) >> 15
    rem = ((q - b * f) & mask) >> 15
    return (v + (p & 65535) * f + ((rem * f & mask) >> 15)) & mask


def midpoint_witness(upper):
    start = 0xc0000000 if upper else 0xc05a0000
    for w in range(start, start + 65536):
        y = intermediate(w)
        m6 = ((y << 1) - 135) & 0xffffffff
        if upper and m6 < 0x80000000 and (m6 & 255) >= 249:
            return w
        if not upper and m6 >= 0x80000000 and (((y << 2) - 128) & 255) <= 19:
            if 0x4c7fffff - ((0x17fffff8 + (y >> 5)) >> 1) != 0x3d708b74:
                return w
    raise AssertionError("expected to find a midpoint refinement witness")


def trace(image, bank, w):
    core = Core(image, "thumbv6m")
    start = core.sym[bank]
    bound = start + (91 * 16 if bank == "t_sigmoid_negative" else len(packed) * 16)
    instructions = []
    row_accesses = []

    def instruction(u, addr, size, _):
        (_, _, mnemonic, operands), = core.dis.disasm_lite(bytes(u.mem_read(addr, size)), addr)
        instructions.append((addr, mnemonic, operands))

    def read(u, access, address, size, value, _):
        if start <= address < bound:
            row_accesses.append((len(instructions) - 1, address - start, size))

    core.u.hook_add(uc.UC_HOOK_CODE, instruction)
    core.u.hook_add(uc.UC_HOOK_MEM_READ, read)
    output, count = core.call("sigmoid", w)
    print(f"  {bank}: {count} retired, result {output:08x}")
    if row_accesses:
        cell_base = ((w >> 16) & 127) * 16
        if bank == "t_eps":
            cell_base += 384 * 16
        accesses = defaultdict(list)
        for i, offset, size in row_accesses:
            accesses[i].append((offset - cell_base, size))
        first = row_accesses[0][0]
        for i in range(max(0, first - 7), min(len(instructions), first + 22)):
            addr, mnemonic, operands = instructions[i]
            note = ""
            if i in accesses:
                note = "  [" + ", ".join(f"row offset {offset:+d}, {size} bytes"
                                        for offset, size in accesses[i]) + "]"
            print(f"    {addr:08x}  {mnemonic:8} {operands}{note}")
    return output


for w in (0xbfffffff, 0xc0000000, 0xc0123456, 0xc05affff, 0xc05b0000,
          midpoint_witness(True), midpoint_witness(False)):
    print(f"input {w:08x}")
    a = trace(args.base_image, "t_eps", w)
    b = trace(args.candidate_image, "t_sigmoid_negative", w)
    assert a == b


if args.rv_images:
    def allocated_sections(image):
        with image.open("rb") as stream:
            elf = ELFFile(stream)
            return {section.name: (section["sh_addr"], sha256(section.data()).hexdigest())
                    for section in elf.iter_sections() if section["sh_flags"] & 2}

    before, after = map(allocated_sections, args.rv_images)
    print("RV32IM allocated section (address, SHA-256), before -> after")
    for name in sorted(before.keys() | after.keys()):
        print(f"  {name}: {before.get(name)} -> {after.get(name)}")
