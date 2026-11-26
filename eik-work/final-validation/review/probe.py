#!/usr/bin/env python3
"""Supplemental probes. Run with the pinned runtime from a scratch kit copy."""
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from elftools.elf.elffile import ELFFile

from eik import config as K, policy as P, reference as R, toolchain as T
from eik.emu import Core


def sections(path):
    with path.open("rb") as stream:
        return {s.name: s.data() for s in ELFFile(stream).iter_sections()
                if s.name == ".text" or s.name.startswith(".rodata")}


def selector_values(expression):
    values = {}
    with TemporaryDirectory(dir=K.BUILD) as work:
        src = Path(work) / "selector.c"
        obj = src.with_suffix(".o")
        src.write_text(f"const uint32_t review_selector = {expression};\n")
        commands = {t: T.ZIG + ["cc", *T.target_cc_args(t)] for t in K.TARGETS}
        commands["host"] = [K.HOST_CC, *T.host_cc_args()]
        for target, command in commands.items():
            subprocess.run([*command, "-c", src, "-o", obj], check=True, capture_output=True)
            with obj.open("rb") as stream:
                elf = ELFFile(stream)
                symbol, = elf.get_section_by_name(".symtab").get_symbol_by_name("review_selector")
                offset = symbol["st_value"]
                data = elf.get_section(symbol["st_shndx"]).data()[offset:offset + 4]
                values[target] = int.from_bytes(data, "little")
    return values


def main(repo):
    entry = repo / "entry.c"
    srcs = {"entry.c": entry}
    for submission in (37, 42, 46, 48, 50):
        srcs[f"id{submission}"] = repo / f"eik-work/toolkit/sources/id{submission}.c"
    for folder in sorted((repo / "eik-work/trials").iterdir()):
        if (folder / "entry.c").is_file():
            srcs[folder.name] = folder / "entry.c"
    normalised = {key: {"path": str(src.relative_to(repo)), "sha256": T.sha(src),
                        "normalised_sha256": P.normalised_hash(src)}
                  for key, src in srcs.items()}

    # ±zero, ±infinity, signaling and quiet NaNs of both signs, then exp thresholds.
    words = [0, 0x80000000, 0x7f800000, 0xff800000, 0x7f800001, 0xff923456,
             0x7fc00000, 0xffdabcde, 0x7fffffff, 0xffffffff, 0x42b17217, 0x42b17218,
             0xc2aeac4f, 0xc2aeac50, 0xc2cff1b4, 0xc2cff1b5]
    specials = {"sigmoid": [0x3f000000, 0x3f000000, 0x3f800000, 0],
                "tanh": [0, 0x80000000, 0x3f800000, 0xbf800000],
                "exp": [0x3f800000, 0x3f800000, 0x7f800000, 0]}
    expected = {fn: head + [w | 0x00400000 for w in words[4:10]]
                + list(R.outputs(fn, words[10:])) for fn, head in specials.items()}
    targets = {}
    for target in K.TARGETS:
        image = T.guest_image(entry, target)
        core = Core(image, target)
        outputs = {fn: core.batch(fn, words, direct=True) for fn in K.FUNCTIONS}
        if outputs != expected:
            raise ValueError(f"{target}: special or threshold mismatch")
        base_sections = sections(T.guest_image(srcs["id50"], target))
        current_sections = sections(image)
        targets[target] = {
            "scored_image_sha256": T.sha(image),
            "same_text_and_rodata_as_id50": current_sections == base_sections,
            "outputs": outputs,
        }
    expression = entry.read_text().splitlines()[1].removeprefix("#define EIK_SEL ")
    print(json.dumps({"normalised": normalised, "selector": selector_values(expression),
                      "expected": expected, "words": words, "targets": targets}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
