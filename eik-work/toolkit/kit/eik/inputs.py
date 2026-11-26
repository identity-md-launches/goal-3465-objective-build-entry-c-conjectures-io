"""Input sets, drawn fresh for every evaluation from a recorded seed.

- typical: sigmoid and tanh get what a recurrent model feeds its gates: N(0, 3) pre-activations
           (80%) and N(0, 1) (20%). exp gets what softmax feeds it, x - max <= 0: -|N(0, 3)| (80%),
           and N(0, 3) (20%).
- wide:    uniform over the exponents where the functions are actually evaluated (|x| from 2^-31 to
           2^8), both signs. Rewards entries that are fast beyond the typical range.
- hard:    near-midpoint inputs (results within 2^-18 ulp of a rounding boundary, where a fast path
           must fall back), plus specials, subnormals, each function's thresholds and the published
           DEEP list. The near-midpoint pool is found afresh for every evaluation: harness/hardscan.c
           samples 2^26 words with a seed derived from the evaluation's, so a pool cannot be learnt
           in advance, and the same seed always gives the same pool. EIK_HARD_FRESH=0 uses the
           published pool in reference/hard-<fn>.txt instead (faster, for development).
"""
import math
import os
import random
import struct
import subprocess

from . import config as K

DEEP = [0x34000000, 0x34C00000, 0x35200000, 0x35600000, 0x35900000, 0x35B00000, 0xB3800000, 0xB4400000,
        0xB4A00000, 0xB4E00000, 0xB5100000, 0xB5300000, 0xB5500000, 0xB5700000, 0xB5980000]
SPECIALS = [0x00000000, 0x80000000, 0x7F800000, 0xFF800000, 0x7FC00000, 0xFFC00001, 0x7F800001, 0x00000001,
            0x80000001, 0x007FFFFF, 0x807FFFFF, 0x00800000, 0x39800000, 0xB9800000, 0x41800000, 0xC1800000,
            0x41800001, 0x42000000, 0x42000001, 0xC3000000, 0xC3000001, 0x3F800000, 0xBF800000]


def f32(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


def around(x, k=1):
    """The 2k + 1 words around binary32(x)."""
    w = f32(x)
    return [w + i for i in range(-k, k + 1)]


LN2 = math.log(2)
# exp's edges: the overflow threshold ln(2^128), exact-c's +inf shortcut at 89, the first subnormal
# result near -126 ln 2, the least subnormal near -149 ln 2, rounding to +0 below -150 ln 2, the +0
# shortcut at -104, and the tiny inputs where e^x rounds to 1 or to its neighbours.
EXP_SPECIALS = (SPECIALS[:12]
                + around(128 * LN2, 2) + around(89.0) + around(-126 * LN2, 2) + around(-149 * LN2, 2)
                + around(-150 * LN2, 2) + around(-104.0)
                + [w | s for w in (0x33000000, 0x33800000, 0x34000000) for s in (0, 0x80000000)])


def fixed_hard(fn):
    """The inputs every hard set of `fn` contains."""
    return (EXP_SPECIALS if fn == "exp" else SPECIALS) + DEEP


def typical(rng, fn):
    if fn == "exp":
        g = rng.gauss(0, 3)
        return f32(-abs(g) if rng.random() < 0.8 else g)
    return f32(rng.gauss(0, 3 if rng.random() < 0.8 else 1))


FRESH = os.environ.get("EIK_HARD_FRESH", "1") != "0"
FRESH_SAMPLES = 1 << 26
FRESH_THRESHOLD = -18  # log2 of the distance to a midpoint, in ulps


def _words(path):
    return [int(l.split()[0], 16) for l in path.read_text().splitlines() if l.strip()] if path.exists() else []


def published_pool(fn):
    return _words(K.REFERENCE / f"hard-{fn}.txt")


def fresh_pool_path(seed: int, fn: str):
    from . import toolchain as T
    scan = T.hardscan()
    return K.BUILD / "hard" / f"{scan.name}-{FRESH_SAMPLES}-{seed}-{fn}.txt", scan


def prepare_fresh_pools(seed: int):
    """Runs hardscan for every function with this evaluation's seed, once; the files are cached in
    build/hard so the per-target measurement processes only read them."""
    if not FRESH:
        return
    for fn in K.FUNCTIONS:
        path, scan = fresh_pool_path(seed, fn)
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        scan_seed = int.from_bytes(random.Random(f"{seed}:{fn}:hardscan").randbytes(8), "little")
        p = subprocess.run([str(scan), fn, str(FRESH_SAMPLES), str(FRESH_THRESHOLD), str(scan_seed)],
                           capture_output=True, text=True, check=True)
        tmp = path.with_suffix(f".tmp{os.getpid()}")
        tmp.write_text(p.stdout)
        os.replace(tmp, path)


def hard_pool(fn, seed=None):
    """The near-midpoint pool for one evaluation: fresh for its seed, or the published one."""
    if FRESH and seed is not None:
        path, _ = fresh_pool_path(seed, fn)
        if not path.exists():
            prepare_fresh_pools(seed)
        pool = _words(path)
        if pool:
            return pool
    return published_pool(fn)


def draw(seed: int, fn: str) -> dict:
    rng = random.Random(f"{seed}:{fn}")
    n = K.SET_SIZES
    typical_set = [typical(rng, fn) for _ in range(n["typical"])]
    wide = [rng.getrandbits(1) << 31 | rng.randint(96, 134) << 23 | rng.getrandbits(23) for _ in range(n["wide"])]
    pool = hard_pool(fn, seed)
    fixed = fixed_hard(fn)
    k = max(0, n["hard"] - len(fixed))
    hard = fixed + ([rng.choice(pool) for _ in range(k)] if pool else
                    [rng.getrandbits(32) for _ in range(k)])
    # Its own stream, so adding it changed none of the other sets' words.
    urng = random.Random(f"{seed}:{fn}:uniform")
    uniform = [urng.getrandbits(32) for _ in range(n["uniform"])]
    return {"typical": typical_set, "wide": wide, "hard": hard, "uniform": uniform}


def target_sample(seed: int, n: int) -> list:
    """Stratified over all 2^32 words: one word from each of n equal strata, at a seeded offset."""
    rng = random.Random(f"{seed}:strata")
    step = (1 << 32) // n
    return [i * step + rng.randrange(step) for i in range(n)]
