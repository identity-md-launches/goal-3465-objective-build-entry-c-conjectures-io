"""Every constant the competition depends on, in one place."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HARNESS = ROOT / "harness"
# Build cache: guest images, host checkers, the reference library, fresh hard pools. Writable; the
# rest of the checkout can be read-only (EIK_BUILD_DIR moves it, e.g. in the container image).
BUILD = Path(os.environ.get("EIK_BUILD_DIR", ROOT / "build"))
REFERENCE = ROOT / "reference"
STATE_DIR = ROOT / "state"
RESULTS = ROOT / "results"
# The reference implementation, vendored and pinned (third_party/exact-c/PROVENANCE.md). EIK_EXACT_C
# points elsewhere for development only; production mode refuses it.
EXACT_C_VENDORED = ROOT / "third_party" / "exact-c"
EXACT_C = Path(os.environ.get("EIK_EXACT_C", EXACT_C_VENDORED))

# Wire format shared with the central API (conjectures-validator) and the miner client: the slug is
# part of every signed submission, and an entry is one file with this name.
COMPETITION_SLUG = "exact-integer-kernels"
SOURCE_FILENAME = "entry.c"

# "development" (default) or "production". Production refuses every setting that would make a verdict
# differ from the published rules or run miner code unconfined (eik/production.py).
MODE = os.environ.get("EIK_MODE", "development")

# The functions an entry defines, in a fixed order: harness/guest.c (eik_batch), check.c and
# hardscan.c index them the same way.
FUNCTIONS = ("sigmoid", "tanh", "exp")
ENTRY_POINTS = {f"eik_{f}" for f in FUNCTIONS}

# Target ISAs. Scored boards: rv32im and thumbv6m. thumbv7em (Cortex-M4/M33) is checked and reported.
TARGETS = {
    "rv32im": {"cc": ["-target", "riscv32-freestanding-none", "-mcpu=generic_rv32+m"], "scored": True},
    "thumbv6m": {"cc": ["-target", "thumb-freestanding-eabi", "-mcpu=cortex_m0plus"], "scored": True},
    "thumbv7em": {"cc": ["-target", "thumb-freestanding-eabi", "-mcpu=cortex_m4"], "scored": False},
}
SCORED = [t for t, v in TARGETS.items() if v["scored"]]
BOARDS = SCORED + ["overall"]

# One set of flags for every build of a submission. -ftrivial-auto-var-init=zero makes a read of an
# uninitialised local deterministic (zero) on every target, so it cannot differ between ISAs.
CFLAGS = ["-std=c11", "-O2", "-ffreestanding", "-fno-builtin", "-ftrivial-auto-var-init=zero", "-fstack-size-section", "-fno-jump-tables",
          "-Werror=vla", "-Werror=implicit-function-declaration", "-Werror=int-conversion",
          "-Wno-unused-command-line-argument", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables"]
HOST_CC = os.environ.get("EIK_HOST_CC", "gcc")
HOST_SANITIZE = ["-fsanitize=undefined,address", "-fno-sanitize-recover=all"]

# Input sets per function and their weights in the score. Production: ~20k per set.
SCALE = float(os.environ.get("EIK_SCALE", "1"))
# "uniform" is words uniform over all 2^32: a small weight so slow paths outside the other sets cost
# something (the C-8 dry run, research/C8-SCORING.md: without it an entry thousands of times slower
# there lost 0.4%; with 5% it loses at least 41%, and no tested gamed entry gets closer to a takeover).
SETS = {"typical": 0.55, "wide": 0.30, "hard": 0.10, "uniform": 0.05}
SET_SIZES = {k: max(20, int(n * SCALE)) for k, n in
             {"typical": 2000, "wide": 1000, "hard": 300, "uniform": 1000}.items()}
TARGET_SAMPLE = max(1024, int(32768 * SCALE))  # words batch-checked on each emulated target

# Score: S = prod_sets mean^w  x  (1 + max(0, p99.9_hard - 20 S_typ)/1e6)^0.1  x  (1 + bytes/64Ki)^0.5,
# geometric mean over the functions. Takeover needs S <= 0.97 x champion's S on the same inputs.
TAIL_FACTOR, TAIL_SCALE, TAIL_EXP = 20, 1e6, 0.1
SIZE_UNIT, SIZE_EXP = 64 * 1024, 0.5   # 0.25 let table-heavy entries buy speed with bytes (C-8)
TAKEOVER_RATIO = 0.97

# Hard caps
CAP_SOURCE_BYTES = 256 * 1024
CAP_CODE_BYTES = 64 * 1024     # code + tables, per target
CAP_STACK_BYTES = 8 * 1024     # the incumbent's big-float temporaries need ~3-5 KiB
CAP_INSTR_PER_CALL = 20_000_000

HOST_THREADS = int(os.environ.get("EIK_THREADS", os.cpu_count() or 4))
QUICK_CHUNKS = 128             # of 4096: what --quick checks on the host (3%)
CHUNKS = 4096                  # the full check's unit: 2^20 words (harness/check.c)

# Wall-clock budgets (seconds). A build or check that exceeds its budget rejects the entry: the
# budgets are generous multiples of what the incumbent needs.
BUILD_SECONDS = int(os.environ.get("EIK_BUILD_SECONDS", "300"))
# The full checks' budgets scale with the work: BUDGET_FACTOR times what the incumbent needs for the
# same number of chunks, divided by the threads (or QEMU processes), and never below BUDGET_FLOOR.
# Measured with the incumbent on an 8-core x86-64 host: core-seconds per chunk of 2^20 words, the
# slowest function. EIK_FULLCHECK_SECONDS replaces the computed budget with a fixed one.
INCUMBENT_CORE_SECONDS_PER_CHUNK = {"host": 12.0, "rv32im": 230.0, "thumbv6m": 352.0, "thumbv7em": 352.0}
BUDGET_FACTOR = 5
BUDGET_FLOOR = 300
FULLCHECK_SECONDS = int(os.environ["EIK_FULLCHECK_SECONDS"]) if os.environ.get("EIK_FULLCHECK_SECONDS") else None


def check_budget(where: str, chunks: int, threads: int) -> int:
    """Wall-clock seconds allowed for one fullcheck (where="host") or targetcheck (where=target)."""
    if FULLCHECK_SECONDS:
        return FULLCHECK_SECONDS
    work = INCUMBENT_CORE_SECONDS_PER_CHUNK[where] * chunks / max(1, threads)
    return int(max(BUDGET_FLOOR, BUDGET_FACTOR * work))
# Memory cap for compiler runs on miner source (address space; not applied to the ASan checker,
# whose shadow memory reserves terabytes of address space: cap that one with the service's cgroup).
BUILD_MEMORY_BYTES = int(os.environ.get("EIK_BUILD_MEMORY_MB", "4096")) * 1024 * 1024
