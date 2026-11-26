#!/usr/bin/env python3
"""Collect a fresh heldout case after restoring, bootstrapping and setting up the kit."""
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import random
from pathlib import Path
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCRATCH = ROOT / "test/scratch/heldout-3"
WORK = SCRATCH / "work"
CASE = WORK / "cases/heldout"
KIT = CASE / "kit"
RAW = HERE / "raw"
PYTHON = WORK / "runtime/bin/python"
DEPS = SCRATCH / "deps"
BOARD = ROOT / "eik-work/final-validation/boards"
ID50 = ROOT / "eik-work/baselines/former-50/entry.c"
CANDIDATE = ROOT / "entry.c"
SEED = "396172055"
ENV = {
    "PATH": f"{DEPS / 'qemu/bin'}:/usr/bin:/bin", "LANG": "C.UTF-8",
    "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
    "TMPDIR": str(CASE / "tmp"), "HOME": str(CASE / "home"),
    "EIK_BUILD_DIR": str(CASE / "build"), "EIK_THREADS": "2",
    "ZIG_GLOBAL_CACHE_DIR": str(CASE / "build/zig-cache"),
    "ZIG_LOCAL_CACHE_DIR": str(CASE / "build/zig-cache"),
}
COMMANDS = RAW / "commands.json"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def record(label, argv, source=None):
    print(label, flush=True)
    started = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    with (RAW / f"{label}.stdout").open("wb") as out, (RAW / f"{label}.stderr").open("wb") as err:
        status = subprocess.run(argv, cwd=KIT, env=ENV, stdout=out, stderr=err).returncode
    commands = json.loads(COMMANDS.read_text()) if COMMANDS.exists() else {}
    commands[label] = {
        "argv": [str(s).replace(str(ROOT), "$REPO") for s in argv],
        "exit_code": status, "started_utc": started, "seconds": round(time.monotonic() - tick, 3),
        "source_sha256": digest(source) if source else None,
    }
    write(COMMANDS, commands)
    return status


def cli(label, *args, source=None):
    return record(label, [PYTHON, "-m", "eik", *args], source)


def main():
    assert digest(CANDIDATE) == "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
    assert digest(ID50) == "88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3"
    for extension in ("json", "stdout", "stderr"):
        shutil.copyfile(CASE / f"logs/setup.{extension}", RAW / f"setup.{extension}")
    shutil.copyfile(WORK / "install.log", RAW / "install.log")
    state = KIT / "state/boards.json"
    shutil.copyfile(state, RAW / "boards-before.json")
    for tool, flags in (("uname", ("-sm",)), ("gcc", ("--version",))):
        record(tool, [tool, *flags])
    cli("fingerprint", "fingerprint", "--details")

    exit_code = record("evaluate", [PYTHON, HERE / "cap_evaluate.py", "evaluate", CANDIDATE,
                                     "--quick", "--json", "--seed", SEED], CANDIDATE)
    shutil.copyfile(state, RAW / "boards-after.json")
    for label, source in (("candidate", CANDIDATE), ("id50", ID50)):
        cli(label, "measure", source, "--seed", SEED, source=source)

    references = defaultdict(list)
    snapshot = json.loads((BOARD / "snapshot.json").read_text())
    for board, ref in snapshot["board_references"].items():
        matches = [p for p in (BOARD / "references").rglob("*.c")
                   if digest(p) == ref["source_sha256"]]
        if matches:
            references[min(matches)].append(board)
    if references:
        flags = []
        for path, boards in references.items():
            cli(f"current-{digest(path)}", "measure", path, "--seed", SEED, source=path)
            for board in boards:
                flags.extend(("--champion", f"{board}={path}"))
        cli("compare", "compare", CANDIDATE, "--seed", SEED, *flags, source=CANDIDATE)

    # Raw standalone quick reports also bind each function and the fixed seed.
    for fn in ("sigmoid", "tanh", "exp"):
        cli(f"quick-{fn}", "fullcheck", CANDIDATE, "--quick", "--function", fn,
            "--seed", SEED, source=CANDIDATE)

    scans = {}
    for fn in ("sigmoid", "tanh", "exp"):
        path, = (CASE / "build/hard").glob(f"*-{SEED}-{fn}.txt")
        scanner = path.parent.parent / path.name.split("-67108864-", 1)[0]
        scan_seed = int.from_bytes(random.Random(f"{SEED}:{fn}:hardscan").randbytes(8), "little")
        scans[fn] = {
            "argv": [scanner.name, fn, "67108864", "-18", str(scan_seed)],
            "cache_file": path.name,
            "scanner_sha256": digest(scanner),
            "pool_sha256": digest(path),
            "pool_mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            "pool_words": len(path.read_text().splitlines()),
        }
        shutil.copyfile(path, RAW / f"pool-{fn}.txt")
    write(RAW / "hardscan.json", scans)
    print(f"Collection complete, evaluate exit {exit_code}", flush=True)


if __name__ == "__main__":
    main()
