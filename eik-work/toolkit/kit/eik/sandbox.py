"""Confinement for every process that reads or runs a miner's source: the compiler runs (clang AST
dump, preprocessing, target objects, guest images, the gcc sanitizer build) and the native full
check, which executes the entry on the host.

Modes (EIK_SANDBOX):

  bwrap      bubblewrap. No network and no other namespaces shared. The filesystem holds only
             /usr (read-only), the dynamic loader's cache, a private /tmp, and the paths each call
             binds: read-only inputs and one writable build folder. $HOME, /etc, the checkout's
             other files and any credentials are absent.
  container  the caller already runs inside a container that is the sandbox (started with no
             network, a read-only root and no capabilities). Docker's default seccomp profile refuses the user namespaces bwrap
             needs, so inside the image this mode is how confinement is declared.
  none       no confinement: development only. Production mode refuses it (eik/production.py).
  auto       bwrap when it works on this host, otherwise none. The default.

Every mode also applies resource limits to the child: no core dumps, a file-size cap, and on
request CPU-time and address-space caps. The wall-clock budget is the caller's `timeout`;
bwrap's --die-with-parent takes the whole tree down when the call is killed.
"""
from __future__ import annotations

import functools
import os
import resource
import shutil
import subprocess
import sys
from pathlib import Path

from . import config as K

MODES = ("auto", "bwrap", "container", "none")
FILE_SIZE_CAP = 2 << 30  # 2 GiB: an AST dump of a 256 KB source is far smaller


class SandboxUnavailable(Exception):
    """The configured sandbox cannot run here: an infrastructure fault, never the entry's."""


def requested() -> str:
    mode = os.environ.get("EIK_SANDBOX", "auto")
    if mode not in MODES:
        raise SandboxUnavailable(f"EIK_SANDBOX={mode!r}; expected one of {', '.join(MODES)}")
    return mode


@functools.lru_cache(maxsize=None)
def _bwrap_works() -> bool:
    exe = shutil.which("bwrap")
    if exe is None:
        return False
    p = subprocess.run([exe, *_base_args(), "--", "/usr/bin/true"], capture_output=True)
    return p.returncode == 0


def mode() -> str:
    """The effective mode: bwrap, container or none."""
    m = requested()
    if m == "auto":
        return "bwrap" if _bwrap_works() else "none"
    if m == "bwrap" and not _bwrap_works():
        raise SandboxUnavailable("EIK_SANDBOX=bwrap, but bubblewrap is missing or cannot create namespaces here")
    return m


def _base_args() -> list:
    args = ["--unshare-all", "--die-with-parent", "--new-session",
            "--ro-bind", "/usr", "/usr", "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp"]
    for name in ("bin", "lib", "lib32", "lib64", "sbin"):
        p = Path("/") / name
        if p.is_symlink():
            args += ["--symlink", os.readlink(p), str(p)]
        elif p.is_dir():
            args += ["--ro-bind", str(p), str(p)]
    # The dynamic loader finds multiarch libraries (libasan, libubsan) through its cache.
    for p in ("/etc/ld.so.cache", "/etc/ld.so.conf", "/etc/ld.so.conf.d"):
        if Path(p).exists():
            args += ["--ro-bind", p, p]
    return args


def _python_paths() -> list:
    """The interpreter and its packages (the pinned clang lives in the `ziglang` wheel)."""
    seen = []
    for p in (sys.prefix, sys.base_prefix, sys.exec_prefix):
        path = Path(p).resolve()
        if not str(path).startswith("/usr") and path not in seen:
            seen.append(path)
    return seen


def zig_cache() -> Path:
    d = K.BUILD / "zig-cache"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise SandboxUnavailable(f"the build folder {K.BUILD} is not writable ({e}); set EIK_BUILD_DIR "
                                 "or mount a volume there") from e
    return d


def _limits(cpu_seconds, memory_bytes):
    def apply():
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        resource.setrlimit(resource.RLIMIT_FSIZE, (FILE_SIZE_CAP, FILE_SIZE_CAP))
        if cpu_seconds:
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        if memory_bytes:
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    return apply


def command(cmd, *, ro=(), rw=(), env=None) -> tuple:
    """(argv, environment) for running `cmd` confined. `ro` paths are bound read-only and `rw` paths
    writable, each at its own location; anything else on the host is invisible."""
    cmd = [str(c) for c in cmd]
    base_env = {"PATH": "/usr/bin:/bin", "HOME": "/tmp", "LANG": "C.UTF-8", "TMPDIR": "/tmp",
                "ZIG_GLOBAL_CACHE_DIR": str(zig_cache()), "ZIG_LOCAL_CACHE_DIR": str(zig_cache())}
    base_env.update(env or {})
    m = mode()
    if m != "bwrap":
        # Outside bwrap the child still gets a clean environment, so nothing (credentials included)
        # leaks from the caller's.
        return cmd, base_env
    args = ["bwrap", *_base_args()]
    binds = [(p, "--ro-bind") for p in [*_python_paths(), *ro]] + [(p, "--bind") for p in [*rw, zig_cache()]]
    for path, flag in binds:
        path = Path(path).resolve()
        if path.exists():
            args += [flag, str(path), str(path)]
    args += ["--clearenv"]
    for k, v in base_env.items():
        args += ["--setenv", k, v]
    return args + ["--", *cmd], {}


def run(cmd, *, ro=(), rw=(), env=None, timeout=None, cpu_seconds=None, memory_bytes=None) -> subprocess.CompletedProcess:
    """Runs `cmd` confined, capturing text output. Raises subprocess.TimeoutExpired past `timeout`."""
    argv, child_env = command(cmd, ro=ro, rw=rw, env=env)
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout,
                          env=child_env or None, preexec_fn=_limits(cpu_seconds, memory_bytes))
