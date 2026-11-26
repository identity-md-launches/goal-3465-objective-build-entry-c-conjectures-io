"""What decided a verdict, as hashes.

Every stage report carries two identities:

  verifier     everything that decides whether an entry is *correct*: the rules (eik/policy.py,
               the prelude), the reference (vendored exact-c and the digests over all 2^32 inputs),
               the full check, both compilers and their flags, the caps.
  measurement  everything that decides an entry's *score*: the guest harness, the emulator and its
               packages, the input generators and the hard-input scanner, the score formula and its
               constants, the target compiler and flags, and the machine architecture (the scanner
               uses x87 long double, so its pools are reproducible on x86-64 only).

Two measurements may be compared only when their measurement identities are equal; the validator
pins both and refuses work from a worker whose identities differ. `details` lists every component,
so a changed identity can be explained.
"""
from __future__ import annotations

import functools
import hashlib
import json
import platform
import subprocess
import sys
from importlib import metadata
from pathlib import Path

from . import config as K

PACKAGES = ("unicorn", "capstone", "pyelftools", "ziglang")


def _file_hashes(paths) -> dict:
    out = {}
    for p in sorted(Path(x) for x in paths):
        rel = str(p.relative_to(K.ROOT)) if p.is_relative_to(K.ROOT) else str(p)
        out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def _first_line(cmd, env=None) -> str:
    """A tool's version line. A tool that does not run is an error, never an identity: hashing
    'unavailable' would give a broken worker a valid-looking identity of its own."""
    from .production import InfraError
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
        if p.returncode == 0:
            return (p.stdout or p.stderr).strip().splitlines()[0]
        detail = p.stderr.strip()[-500:]
    except (OSError, subprocess.SubprocessError, IndexError) as e:
        detail = str(e)
    raise InfraError(f"{' '.join(map(str, cmd[-3:]))} did not run: {detail}")


@functools.lru_cache(maxsize=None)
def tools() -> dict:
    import os
    from . import sandbox as SB
    zig = [sys.executable, "-m", "ziglang"]
    zig_env = {**os.environ, "ZIG_GLOBAL_CACHE_DIR": str(SB.zig_cache()), "ZIG_LOCAL_CACHE_DIR": str(SB.zig_cache())}
    versions = {}
    for name in PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = None
    return {
        "zig": _first_line(zig + ["version"], zig_env),
        "clang": _first_line(zig + ["cc", "--version"], zig_env),
        "host_cc": _first_line([K.HOST_CC, "--version"]),
        "python": platform.python_version(),
        "machine": platform.machine(),
        "packages": versions,
    }


def _eik(*names) -> list:
    return [K.ROOT / "eik" / n for n in names]


def _exact_c() -> list:
    return sorted(p for p in K.EXACT_C.rglob("*") if p.suffix in (".c", ".h"))


def _digests() -> list:
    return [K.REFERENCE / f"{fn}.digest" for fn in K.FUNCTIONS]


@functools.lru_cache(maxsize=None)
def details() -> dict:
    t = tools()
    verifier = {
        "files": _file_hashes([K.HARNESS / "eik.h", K.HARNESS / "check.c", K.HARNESS / "target_check.c",
                               K.HARNESS / "guest.c", *_exact_c(), *_digests(),
                               *_eik("policy.py", "stack.py", "toolchain.py", "reference.py", "stages.py")]),
        "constants": {"functions": K.FUNCTIONS, "targets": K.TARGETS, "cflags": K.CFLAGS,
                      "host_sanitize": K.HOST_SANITIZE, "cap_source": K.CAP_SOURCE_BYTES,
                      "cap_code": K.CAP_CODE_BYTES, "cap_stack": K.CAP_STACK_BYTES,
                      "cap_instr": K.CAP_INSTR_PER_CALL, "target_sample": K.TARGET_SAMPLE,
                      "budget": [K.INCUMBENT_CORE_SECONDS_PER_CHUNK, K.BUDGET_FACTOR, K.BUDGET_FLOOR,
                                 K.FULLCHECK_SECONDS]},
        "tools": {"clang": t["clang"], "host_cc": t["host_cc"], "pyelftools": t["packages"]["pyelftools"],
                  "capstone": t["packages"]["capstone"]},
    }
    from . import inputs as I
    measurement = {
        "files": _file_hashes([K.HARNESS / "eik.h", K.HARNESS / "guest.c", K.HARNESS / "hardscan.c", *_exact_c(),
                               *_eik("emu.py", "inputs.py", "score.py", "stages.py")]),
        "constants": {"functions": K.FUNCTIONS, "targets": K.TARGETS, "cflags": K.CFLAGS, "sets": K.SETS,
                      "set_sizes": K.SET_SIZES, "target_sample": K.TARGET_SAMPLE,
                      "tail": [K.TAIL_FACTOR, K.TAIL_SCALE, K.TAIL_EXP], "size": [K.SIZE_UNIT, K.SIZE_EXP],
                      "takeover_ratio": K.TAKEOVER_RATIO, "cap_instr": K.CAP_INSTR_PER_CALL,
                      "hard_fresh": I.FRESH, "hard_samples": I.FRESH_SAMPLES, "hard_threshold": I.FRESH_THRESHOLD},
        "tools": {"clang": t["clang"], "host_cc": t["host_cc"], "machine": t["machine"],
                  **{k: t["packages"][k] for k in ("unicorn", "capstone", "pyelftools")}},
    }
    return {"verifier": verifier, "measurement": measurement, "tools": t}


def _id(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=list).encode()).hexdigest()


def ids() -> dict:
    """The two identities (and the sandbox mode, which is not part of either: it changes how an
    entry is confined, not what it is measured or checked against)."""
    from . import sandbox as SB
    d = details()
    try:
        mode = SB.mode()
    except SB.SandboxUnavailable:
        mode = "unavailable"
    return {"verifier": _id(d["verifier"]), "measurement": _id(d["measurement"]), "sandbox": mode}


def reference_problems() -> list:
    """Differences between the reference digests and reference/digests.sha256 (empty when sound)."""
    listed = {}
    path = K.REFERENCE / "digests.sha256"
    if not path.exists():
        return [f"{path.relative_to(K.ROOT)} is missing"]
    for line in path.read_text().splitlines():
        if line.strip():
            h, name = line.split()
            listed[name] = h
    problems = []
    for d in _digests():
        rel = str(d.relative_to(K.ROOT))
        if not d.exists():
            problems.append(f"{rel} is missing")
        elif listed.get(rel) != hashlib.sha256(d.read_bytes()).hexdigest():
            problems.append(f"{rel} does not match reference/digests.sha256")
    return problems
