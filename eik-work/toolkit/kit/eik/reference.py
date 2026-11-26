"""The reference outputs: exact-c's er_sigmoid / er_tanh / er_exp on the host (ctypes). exact-c is tested
bit for bit against the proved Lean runtime; the full check compares against SHA-256 digests of
its outputs over all 2^32 inputs (reference/<fn>.digest)."""
import ctypes

from . import config as K
from . import toolchain as T

_lib = None


def _load():
    global _lib
    if _lib is None:
        _lib = ctypes.CDLL(str(T.reference_lib()))
        for f in (f"er_{fn}" for fn in K.FUNCTIONS):
            getattr(_lib, f).argtypes = [ctypes.c_uint32]
            getattr(_lib, f).restype = ctypes.c_uint32
    return _lib


def outputs(fn: str, words):
    f = getattr(_load(), f"er_{fn}")
    return [f(w) for w in words]
