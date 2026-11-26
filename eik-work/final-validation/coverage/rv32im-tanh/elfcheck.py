"""Standard-library ELF32 little-endian summary used by collect.py and verify.py.

summary() describes what is loaded and executed (PT_LOAD segments, SHF_ALLOC sections, entry
point, entry/kernel symbols, relocation and dynamic sections) separately from non-loaded
metadata, so two linked images can be compared for executable equivalence while path-only
differences in non-alloc sections (debug info, symbol/string tables, comments) are listed.
"""
from hashlib import sha256
import struct

EM_RISCV = 243
SHF_ALLOC = 0x2
SHT_NOBITS = 8
SHT_SYMTAB = 2
SHT_RELA = 4
SHT_REL = 9
SHT_DYNAMIC = 6
PT_LOAD = 1
PT_INTERP = 3
PT_DYNAMIC = 2
SYMBOLS = ("_start", "eik_sigmoid", "eik_tanh", "eik_exp")


class ElfError(ValueError):
    pass


def _cstr(blob, offset):
    end = blob.index(b"\0", offset)
    return blob[offset:end].decode("utf-8", "replace")


def summary(data: bytes) -> dict:
    if data[:4] != b"\x7fELF":
        raise ElfError("not an ELF file")
    if data[4] != 1 or data[5] != 1:
        raise ElfError("not ELF32 little-endian")
    (e_type, e_machine, _ver, e_entry, e_phoff, e_shoff, e_flags, _ehsize, e_phentsize, e_phnum,
     e_shentsize, e_shnum, e_shstrndx) = struct.unpack_from("<HHIIIIIHHHHHH", data, 16)
    if e_shentsize != 40 or (e_phnum and e_phentsize != 32):
        raise ElfError("unexpected header entry sizes")
    sections = []
    for i in range(e_shnum):
        sections.append(struct.unpack_from("<IIIIIIIIII", data, e_shoff + 40 * i))
    shstr = sections[e_shstrndx]
    names = data[shstr[4]:shstr[4] + shstr[5]]

    def content(sh):
        if sh[1] == SHT_NOBITS:
            return b""
        return data[sh[4]:sh[4] + sh[5]]

    alloc, nonalloc, relocs, dynamic = [], [], [], False
    symbols = {}
    for sh in sections[1:]:
        name = _cstr(names, sh[0])
        record = {"name": name, "type": sh[1], "flags": sh[2], "addr": sh[3], "size": sh[5],
                  "sha256": None if sh[1] == SHT_NOBITS else sha256(content(sh)).hexdigest()}
        if sh[1] in (SHT_REL, SHT_RELA):
            target = sections[sh[7]] if 0 < sh[7] < len(sections) else None
            relocs.append({"name": name, "type": sh[1], "size": sh[5], "sha256": record["sha256"],
                           "applies_to": _cstr(names, target[0]) if target else None,
                           "applies_to_alloc": bool(target and target[2] & SHF_ALLOC)})
        if sh[1] == SHT_DYNAMIC:
            dynamic = True
        (alloc if sh[2] & SHF_ALLOC else nonalloc).append(record)
        if sh[1] == SHT_SYMTAB:
            strtab = sections[sh[6]]
            strs = data[strtab[4]:strtab[4] + strtab[5]]
            body = content(sh)
            for off in range(0, len(body), 16):
                st_name, value, size, info, _other, shndx = struct.unpack_from("<IIIBBH", body, off)
                sym = _cstr(strs, st_name) if st_name else ""
                if sym in SYMBOLS and shndx != 0:
                    symbols[sym] = {"value": value, "size": size, "bind": info >> 4, "type": info & 15}
    # The first PT_LOAD normally maps the ELF header itself. e_shoff, e_shnum and e_shstrndx only
    # locate the (non-loaded) section header table, so they are masked in the load digests.
    masked = bytearray(data)
    masked[32:36] = b"\0" * 4
    masked[48:52] = b"\0" * 4
    # Non-PT_LOAD program headers (e.g. RISCV_ATTRIBUTES) may point at non-loaded bytes whose
    # file offset moves with debug-info size; their p_offset is masked and their other fields
    # and content digests are recorded in "other_segments".
    other = []
    for i in range(e_phnum):
        base = e_phoff + 32 * i
        p_type, p_offset, p_vaddr, _pa, p_filesz, p_memsz, p_flags, _al = struct.unpack_from("<IIIIIIII", data, base)
        if p_type != PT_LOAD:
            masked[base + 4:base + 8] = b"\0" * 4
            other.append({"type": p_type, "vaddr": p_vaddr, "filesz": p_filesz, "memsz": p_memsz,
                          "flags": p_flags, "range": (p_offset, p_offset + p_filesz)})
    for seg in other:
        lo, hi = seg.pop("range")
        seg["sha256_masked"] = sha256(bytes(masked[lo:hi])).hexdigest()
    loads, interp = [], False
    for i in range(e_phnum):
        p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack_from(
            "<IIIIIIII", data, e_phoff + 32 * i)
        if p_type == PT_LOAD:
            loads.append({"vaddr": p_vaddr, "paddr": p_paddr, "filesz": p_filesz, "memsz": p_memsz,
                          "flags": p_flags, "align": p_align,
                          "sha256": sha256(data[p_offset:p_offset + p_filesz]).hexdigest(),
                          "sha256_masked_shdr_fields": sha256(bytes(masked[p_offset:p_offset + p_filesz])).hexdigest()})
        if p_type == PT_INTERP:
            interp = True
        if p_type == PT_DYNAMIC:
            dynamic = True
    return {"e_type": e_type, "machine": e_machine, "elf_flags": e_flags, "entry": e_entry,
            "symbols": symbols, "loads": loads, "other_segments": other, "alloc_sections": alloc,
            "relocation_sections": relocs, "dynamic": dynamic, "interp": interp,
            "nonalloc_sections": nonalloc}


def executable_view(s: dict) -> dict:
    """The part of a summary that determines execution: everything except non-alloc metadata."""
    view = {k: v for k, v in s.items() if k not in ("nonalloc_sections", "loads", "relocation_sections")}
    view["loads"] = [{k: v for k, v in load.items() if k != "sha256"} for load in s["loads"]]
    view["relocation_sections"] = [r for r in s["relocation_sections"] if r["applies_to_alloc"]]
    return view


def metadata_differences(a: dict, b: dict) -> list:
    """Names of non-alloc sections whose presence, size or content differ."""
    left = {s["name"]: (s["size"], s["sha256"]) for s in a["nonalloc_sections"]}
    right = {s["name"]: (s["size"], s["sha256"]) for s in b["nonalloc_sections"]}
    names = sorted(n for n in set(left) | set(right) if left.get(n) != right.get(n))
    if [l["sha256"] for l in a["loads"]] != [l["sha256"] for l in b["loads"]]:
        names.append("ELF header e_shoff/e_shnum/e_shstrndx (section header table location)")
    return names
