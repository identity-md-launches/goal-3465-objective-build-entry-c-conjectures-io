"""Production mode (EIK_MODE=production): refuse every setting under which a verdict could differ
from the published rules, or miner code could run unconfined. A refusal is an infrastructure error
(exit 3), never a verdict on the entry."""
from __future__ import annotations

import platform
import re
from importlib import metadata

from . import config as K
from . import sandbox as SB


class InfraError(Exception):
    """Not the entry's fault: configuration, the host, or the harness itself."""


def pinned_versions() -> dict:
    """name -> version from requirements.txt."""
    out = {}
    path = K.ROOT / "requirements.txt"
    if path.exists():
        for line in path.read_text().splitlines():
            m = re.match(r"^([A-Za-z0-9_.-]+)==([^\s;\\]+)", line.strip())
            if m:
                out[m.group(1).lower()] = m.group(2)
    return out


def problems(stage: str) -> list:
    from . import fingerprint as FP
    from . import inputs as I
    if K.MODE not in ("development", "production"):
        return [f"EIK_MODE={K.MODE!r}; expected development or production"]
    if K.MODE != "production":
        return []
    out = []
    try:
        mode = SB.mode()
        if mode not in ("bwrap", "container"):
            out.append(f"sandbox is {mode!r}; production needs EIK_SANDBOX=bwrap, or container inside the image")
    except SB.SandboxUnavailable as e:
        out.append(str(e))
    if K.SCALE != 1:
        out.append(f"EIK_SCALE={K.SCALE}; the published input set sizes need 1")
    if K.EXACT_C.resolve() != K.EXACT_C_VENDORED.resolve():
        out.append(f"EIK_EXACT_C points at {K.EXACT_C}; production uses the vendored reference only")
    for name, want in pinned_versions().items():
        try:
            have = metadata.version(name)
        except metadata.PackageNotFoundError:
            have = None
        if have != want:
            out.append(f"{name} {have} is installed; requirements.txt pins {want}")
    if stage in ("measure", "compare"):
        if not I.FRESH:
            out.append("EIK_HARD_FRESH=0; production draws a fresh hard pool for every seed")
        if platform.machine() not in ("x86_64", "AMD64"):
            out.append(f"measurement on {platform.machine()}: the hard-input scanner uses x87 long double, so "
                       "pools are reproducible on x86-64 only")
    if stage == "fullcheck":
        out += FP.reference_problems()
    return out


def enforce(stage: str):
    p = problems(stage)
    if p:
        raise InfraError("production mode refuses this configuration: " + "; ".join(p))
