"""Auxiliary trace and binade split using the kit's instruction counter.

Run from the repository root with the runner's Python 3.12 after both measure
stages. This diagnostic leaves scoring populations and kit files untouched.
"""
import hashlib
import json
import os
import struct
import sys
from pathlib import Path

work = Path(sys.argv[1]).resolve()
case = work / "cases/trial"
os.environ["EIK_BUILD_DIR"] = str(case / "build")
os.environ["ZIG_GLOBAL_CACHE_DIR"] = str(case / "build/zig-cache")
os.environ["ZIG_LOCAL_CACHE_DIR"] = os.environ["ZIG_GLOBAL_CACHE_DIR"]
os.environ["TMPDIR"] = str(case / "tmp")
sys.path.insert(0, str(case / "kit"))

from eik import emu, inputs, toolchain
from elftools.elf.elffile import ELFFile

BASE = Path("eik-work/baselines/former-50/entry.c").resolve()
ENTRY = Path(__file__).with_name("entry.c").resolve()
SEEDS = (1874435642, 1947282751)


def affected(word):
    return word >> 23 == 0x180


class TraceCore(emu.Core):
    trace = None

    def _block(self, u, addr, size, data):
        super()._block(u, addr, size, data)
        if self.trace is None:
            return
        for address, _, mnemonic, operands in self.dis.disasm_lite(bytes(u.mem_read(addr, size)), addr):
            suffix = ""
            if mnemonic == "ldr" and "[pc, #" in operands:
                displacement = int(operands.split("[pc, #")[1].split("]")[0], 0)
                literal = struct.unpack("<I", u.mem_read(((address + 4) & ~3) + displacement, 4))[0]
                suffix = f"  [0x{literal:08x}]"
            self.trace.append(f"{address:08x}  {mnemonic:<7} {operands}{suffix}")


def text_hash(image):
    with image.open("rb") as fd:
        return hashlib.sha256(ELFFile(fd).get_section_by_name(".text").data()).hexdigest()


def compare(baseline, candidate, word):
    old, before = baseline.call("exp", word)
    new, after = candidate.call("exp", word)
    assert old == new, (hex(word), hex(old), hex(new))
    return f"{new:08x}", before, after


def report():
    images = {target: [toolchain.guest_image(src, target) for src in (BASE, ENTRY)]
              for target in ("rv32im", "thumbv6m", "thumbv7em")}
    baseline, candidate = [TraceCore(img, "thumbv6m") for img in images["thumbv6m"]]
    rows = {}
    for seed in SEEDS:
        groups = {}
        for name, words in inputs.draw(seed, "exp").items():
            costs = {True: [], False: []}
            for word in words:
                _, before, after = compare(baseline, candidate, word)
                costs[affected(word)].append((before, after))
            groups[name] = {}
            for hit, pairs in costs.items():
                groups[name]["row10" if hit else "other"] = {
                    "n": len(pairs),
                    "before": sum(p[0] for p in pairs) / len(pairs) if pairs else None,
                    "after": sum(p[1] for p in pairs) / len(pairs) if pairs else None,
                }
        pool, _ = inputs.fresh_pool_path(seed, "exp")
        midpoints = []
        for line in pool.read_text().splitlines():
            word_hex, distance = line.split()
            word = int(word_hex, 16)
            if affected(word):
                out, before, after = compare(baseline, candidate, word)
                midpoints.append({"input": word_hex, "distance_ulps": float(distance),
                                  "output": out, "before": before, "after": after})
        rows[seed] = {"class_split": groups, "near_midpoints": midpoints}
    boundaries = {}
    for word in (0xbfffffff, 0xc0000000, 0xc07fffff, 0xc0800000):
        out, before, after = compare(baseline, candidate, word)
        boundaries[f"{word:08x}"] = {"output": out, "before": before, "after": after}
    traces = []
    for core in (baseline, candidate):
        core.trace = []
        _, count = core.call("exp", 0xc0000000)
        assert count == len(core.trace)
        traces.append(core.trace)
    return {"text_sha256": {target: [text_hash(p) for p in pair] for target, pair in images.items()},
            "rows": rows, "boundaries": boundaries,
            "trace_word": "c0000000", "trace_id50": traces[0], "trace_candidate": traces[1]}


print(json.dumps(report(), indent=2))
