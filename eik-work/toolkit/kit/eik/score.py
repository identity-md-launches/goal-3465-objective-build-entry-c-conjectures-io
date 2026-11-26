"""Measurement on one target and the score formula."""
import math

from . import config as K
from . import inputs as I
from . import reference as R
from . import toolchain as T
from .emu import Core, Timeout


def _p(xs, q):
    s = sorted(xs)
    return s[min(len(s) - 1, max(0, math.ceil(q * len(s)) - 1))]


def measure(src, target, seed, sample=True):
    """Counts instructions on fresh inputs, checks every scored output, measures peak stack, and
    (if sample) batch-checks a stratified sample of all 2^32 words on this target."""
    core = Core(T.guest_image(src, target), target)
    out = {"target": target, "functions": {}, "wrong": [], "sample": None}
    try:
        for fn in K.FUNCTIONS:
            res = {}
            for name, words in I.draw(seed, fn).items():
                want = R.outputs(fn, words)
                counts = []
                for w, exp in zip(words, want):
                    got, n = core.call(fn, w)
                    counts.append(n)
                    if got != exp and len(out["wrong"]) < 8:
                        out["wrong"].append({"fn": fn, "input": f"{w:08x}", "got": f"{got:08x}", "want": f"{exp:08x}"})
                res[name] = {"n": len(counts), "mean": sum(counts) / len(counts), "median": _p(counts, 0.5),
                             "p999": _p(counts, 0.999), "max": max(counts)}
            out["functions"][fn] = res
        if sample:
            words = I.target_sample(seed, K.TARGET_SAMPLE)
            s = {"words": 0, "mismatches": 0, "examples": []}
            for fn in K.FUNCTIONS:
                got = core.batch(fn, words, direct=True)
                want = R.outputs(fn, words)
                s["words"] += len(words)
                for w, g, e in zip(words, got, want):
                    if g != e:
                        s["mismatches"] += 1
                        if len(s["examples"]) < 8:
                            s["examples"].append({"fn": fn, "input": f"{w:08x}", "got": f"{g:08x}", "want": f"{e:08x}"})
            out["sample"] = s
        out["stack"] = core.peak_stack()
    except Timeout as e:
        out["timeout"] = str(e)
    return out


def score(m, nbytes):
    """S for one target (lower is better) and its parts."""
    logs, parts = [], {}
    for fn in K.FUNCTIONS:
        d = m["functions"][fn]
        base = sum(w * math.log(d[s]["mean"]) for s, w in K.SETS.items())
        tail = (1 + max(0.0, d["hard"]["p999"] - K.TAIL_FACTOR * d["typical"]["mean"]) / K.TAIL_SCALE) ** K.TAIL_EXP
        logs.append(base + math.log(tail))
        parts[fn] = {"geo_mean_instr": math.exp(base), "tail_factor": tail}
    size = (1 + nbytes / K.SIZE_UNIT) ** K.SIZE_EXP
    return math.exp(sum(logs) / len(logs)) * size, {"functions": parts, "size_factor": size, "bytes": nbytes}
