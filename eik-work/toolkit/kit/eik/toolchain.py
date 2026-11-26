"""Builds: AST dumps, target objects, guest images for the emulator, the host checker, and the
reference library. Target builds use the pinned clang inside the `ziglang` wheel; host builds use
gcc (a second, independent compiler for the full check).

Every step that reads the entry's source runs confined (eik/sandbox.py) under a wall-clock budget.
Outputs are written under a temporary name and renamed into place, so concurrent jobs that share the
build cache never see a half-written file."""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from . import config as K
from . import sandbox as SB

ZIG = [sys.executable, "-m", "ziglang"]
REF_SOURCES = ["act.c", "acc.c", "sha256.c", "scalar.c"]


class BuildError(Exception):
    """The entry did not build: its compile error, or its build exceeded the budget."""


def run(cmd, **kw):
    """A trusted build step (the reference, the hard-input scanner): not confined."""
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if p.returncode != 0:
        raise BuildError(f"{' '.join(map(str, cmd[:6]))} ...\n{p.stderr.strip()[-3000:]}")
    return p


def run_untrusted(cmd, src: Path, out_dir: Path = None, extra_ro=()):
    """A build step that reads the entry: confined, time- and memory-capped."""
    ro = [Path(src), K.HARNESS, *extra_ro]
    rw = [out_dir] if out_dir else []
    try:
        p = SB.run(cmd, ro=ro, rw=rw, timeout=K.BUILD_SECONDS, cpu_seconds=K.BUILD_SECONDS,
                   memory_bytes=K.BUILD_MEMORY_BYTES)
    except subprocess.TimeoutExpired:
        raise BuildError(f"build step took longer than {K.BUILD_SECONDS} s")
    if p.returncode != 0:
        raise BuildError(f"{' '.join(map(str, cmd[3:9]))} ...\n{p.stderr.strip()[-3000:]}")
    return p


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _ref_files() -> list:
    """exact-c's sources and headers that the reference and the host checker are built from."""
    return ([K.EXACT_C / "include" / "exact.h", K.EXACT_C / "src" / "internal.h"]
            + [K.EXACT_C / "src" / s for s in REF_SOURCES])


def build_key(*parts) -> str:
    """A short hash of files (their names and contents) and settings, so that a cached build is
    reused only while everything it was built from is unchanged."""
    h = hashlib.sha256()
    for part in parts:
        for item in part if isinstance(part, (list, tuple)) else [part]:
            if isinstance(item, Path):
                h.update(item.name.encode() + b"\0" + item.read_bytes())
            else:
                h.update(repr(item).encode())
            h.update(b"\0")
    return h.hexdigest()[:12]


def workdir(src: Path) -> Path:
    """A submission's build folder: its hash plus the harness, the reference and the build settings,
    so that changing any of them rebuilds it."""
    harness = [K.HARNESS / f for f in ("eik.h", "guest.c", "check.c")]
    d = K.BUILD / f"{sha(src)[:16]}-{build_key(harness, _ref_files(), K.CFLAGS, K.TARGETS, K.HOST_SANITIZE)}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _tmp(out: Path) -> Path:
    return out.with_name(f".{out.name}.tmp{os.getpid()}")


HOST_TRIPLE = "x86_64-unknown-linux-gnu"


def ast_json(src: Path, triple: str = "riscv32-unknown-unknown-elf") -> dict:
    """clang's AST as JSON, by default for the RV32 target (ILP32), with the prelude force-included.
    HOST_TRIPLE gives the LP64 view the host's full check compiles."""
    p = run_untrusted(ZIG + ["clang", "-cc1", "-triple", triple, "-std=c11", "-ffreestanding",
                             "-include", K.HARNESS / "eik.h", "-ast-dump=json", src], src)
    return json.loads(p.stdout)


def preprocess(src: Path) -> str:
    return run_untrusted(ZIG + ["cc", "-target", "riscv32-freestanding-none", "-std=c11", "-E", "-P",
                                "-include", K.HARNESS / "eik.h", src], src).stdout


def target_cc_args(target: str) -> list:
    """The flags of every target build of an entry."""
    return [*K.TARGETS[target]["cc"], *K.CFLAGS, "-include", K.HARNESS / "eik.h"]


def host_cc_args() -> list:
    """The flags of the host's sanitizer build of an entry (the full check)."""
    return [K.CFLAGS[0], "-O1", "-g", "-fno-builtin", "-ftrivial-auto-var-init=zero", "-Werror=vla",
            "-Werror=implicit-function-declaration", *K.HOST_SANITIZE, "-include", K.HARNESS / "eik.h"]


def preprocessed_builds(src: Path) -> dict:
    """The entry's own lines after preprocessing, as each real build sees them: every target (clang,
    its flags) and the host's sanitizer build (gcc, its flags). Lines from the prelude are dropped:
    they differ legitimately (size_t is 32 bits on the targets, 64 on the host)."""
    out = {}
    cmds = {t: ZIG + ["cc", *target_cc_args(t), "-E", src] for t in K.TARGETS}
    cmds["host"] = [K.HOST_CC, *host_cc_args(), "-E", src]
    for build, cmd in cmds.items():
        text = run_untrusted(cmd, src).stdout
        keep, mine = [], False
        for line in text.splitlines():
            m = re.match(r'#\s*(?:line\s+)?\d+\s+"((?:[^"\\]|\\.)*)"', line)
            if m:
                mine = m.group(1) == str(src)
            elif mine:
                keep.append(line)
        out[build] = "\n".join(keep)
    return out


def object_file(src: Path, target: str) -> Path:
    d = workdir(src)
    out = d / f"sub-{target}.o"
    if not out.exists():
        tmp = _tmp(out)
        run_untrusted(ZIG + ["cc", *target_cc_args(target), "-c", "-o", tmp, src], src, d)
        os.replace(tmp, out)
    return out


def guest_image(src: Path, target: str) -> Path:
    d = workdir(src)
    out = d / f"guest-{target}.elf"
    if not out.exists():
        obj = object_file(src, target)
        tmp = _tmp(out)
        run_untrusted(ZIG + ["cc", *K.TARGETS[target]["cc"], *K.CFLAGS, "-I", K.HARNESS, "-include", K.HARNESS / "eik.h",
                             "-Wl,--entry=eik_batch", "-o", tmp, K.HARNESS / "guest.c", obj], src, d)
        os.replace(tmp, out)
    return out


def target_checker(src: Path, target: str) -> Path:
    """The entry's target object file linked into a static Linux program for QEMU user mode
    (harness/target_check.c): the same object code the emulator scores, checked on every input."""
    d = workdir(src)
    out = d / f"target-check-{target}.elf"
    if not out.exists():
        obj = object_file(src, target)
        tmp = _tmp(out)
        run_untrusted(ZIG + ["cc", *K.TARGETS[target]["cc"], *K.CFLAGS, "-fomit-frame-pointer", "-I", K.HARNESS,
                             "-include", K.HARNESS / "eik.h", "-static", "-Wl,--entry=_start", "-o", tmp,
                             K.HARNESS / "target_check.c", K.HARNESS / "guest.c", obj], src, d)
        os.replace(tmp, out)
    return out


def host_checker(src: Path) -> Path:
    """The submission under UBSan + ASan (gcc), linked with the reference and check.c."""
    d = workdir(src)
    out = d / "check-host"
    if not out.exists():
        obj = d / "sub-host-san.o"
        tmp_obj, tmp = _tmp(obj), _tmp(out)
        run_untrusted([K.HOST_CC, *host_cc_args(), "-c", "-o", tmp_obj, src], src, d)
        os.replace(tmp_obj, obj)
        run_untrusted([K.HOST_CC, "-std=c11", "-O2", *K.HOST_SANITIZE, "-I", K.EXACT_C / "include",
                       "-I", K.EXACT_C / "src", K.HARNESS / "check.c", obj,
                       *[K.EXACT_C / "src" / s for s in REF_SOURCES], "-lpthread", "-o", tmp],
                      src, d, extra_ro=[K.EXACT_C])
        os.replace(tmp, out)
    return out


def reference_lib() -> Path:
    out = K.BUILD / f"libref-{build_key(_ref_files())}.so"
    if not out.exists():
        K.BUILD.mkdir(parents=True, exist_ok=True)
        tmp = _tmp(out)
        run([K.HOST_CC, "-std=c11", "-O2", "-fPIC", "-shared", "-I", K.EXACT_C / "include", "-I", K.EXACT_C / "src",
             *[K.EXACT_C / "src" / s for s in REF_SOURCES], "-o", tmp])
        os.replace(tmp, out)
    return out


def reference_digester() -> Path:
    out = K.BUILD / f"refdigest-{build_key(_ref_files(), K.HARNESS / 'check.c')}"
    if not out.exists():
        K.BUILD.mkdir(parents=True, exist_ok=True)
        tmp = _tmp(out)
        run([K.HOST_CC, "-std=c11", "-O2", "-DREF", "-I", K.EXACT_C / "include", "-I", K.EXACT_C / "src",
             K.HARNESS / "check.c", *[K.EXACT_C / "src" / s for s in REF_SOURCES], "-lpthread", "-o", tmp])
        os.replace(tmp, out)
    return out


def mpfr_reference() -> Path:
    """The independent MPFR reference (harness/mpfr_ref.c); needs libmpfr-dev."""
    sources = [K.HARNESS / "mpfr_ref.c", K.EXACT_C / "src" / "sha256.c"]
    out = K.BUILD / f"mpfr-ref-{build_key(sources, _ref_files())}"
    if not out.exists():
        K.BUILD.mkdir(parents=True, exist_ok=True)
        tmp = _tmp(out)
        run([K.HOST_CC, "-std=c11", "-O2", "-I", K.EXACT_C / "include", "-I", K.EXACT_C / "src", *sources,
             "-lmpfr", "-lgmp", "-lpthread", "-o", tmp])
        os.replace(tmp, out)
    return out


def hardscan() -> Path:
    out = K.BUILD / f"hardscan-{build_key(K.HARNESS / 'hardscan.c')}"
    if not out.exists():
        K.BUILD.mkdir(parents=True, exist_ok=True)
        tmp = _tmp(out)
        run([K.HOST_CC, "-std=c11", "-O2", K.HARNESS / "hardscan.c", "-lm", "-o", tmp])
        os.replace(tmp, out)
    return out
