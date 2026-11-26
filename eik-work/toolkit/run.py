#!/usr/bin/env python3
"""Run the pinned local evaluator with an offline runtime and case-local state."""
import argparse
import fcntl
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from provision import DEFAULT, checked, stage

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
COMMANDS = {"setup", "fingerprint", "check", "gate", "measure", "evaluate",
            "compare", "fullcheck", "targetcheck", "merge"}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def portable(text):
    return text.replace(str(REPO), "$REPO")


def runner(work, case_name, label, args, dependencies=DEFAULT):
    if not args or args[0] not in COMMANDS:
        raise ValueError("expected a supported local evaluator command")
    if any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", s) for s in (case_name, label)):
        raise ValueError("invalid case or label")
    args = list(args)
    source_hash = None
    if args[0] in {"check", "gate", "measure", "evaluate", "compare", "fullcheck", "targetcheck"}:
        source = Path(args[1]).resolve()
        source_hash = sha256(source.read_bytes()).hexdigest()
        args[1] = str(source)
    # Absolute paths for arguments whose values refer to caller-side files.
    for i, arg in enumerate(args[:-1]):
        if arg in {"--out", "--known-hashes"}:
            args[i + 1] = str(Path(args[i + 1]).resolve())
        if arg == "--champion":
            board, sep, path = args[i + 1].partition("=")
            if sep:
                args[i + 1] = f"{board}={Path(path).resolve()}"
    if args[0] == "merge":
        for i, arg in enumerate(args[1:], 1):
            if not arg.startswith("-") and args[i - 1] != "--require-targets":
                args[i] = str(Path(arg).resolve())
    work = work.resolve()
    dependencies = dependencies.resolve()
    if args[0] == "targetcheck":
        for item in json.loads((ROOT / "dependencies.json").read_text())["qemu"]["executables"].values():
            checked(dependencies / item["path"], item)
    case = work / "cases" / case_name
    logs = case / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    env = {"PATH": f"{dependencies / 'qemu/bin'}:/usr/bin:/bin", "LANG": "C.UTF-8",
           "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
           "PIP_NO_CACHE_DIR": "1", "PIP_CONFIG_FILE": os.devnull,
           "TMPDIR": str(case / "tmp"), "HOME": str(case / "home")}
    for key in ("HOME", "TMPDIR"):
        Path(env[key]).mkdir(exist_ok=True)
    runtime = work / "runtime"
    python = runtime / "bin/python"
    with (work / "runtime.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not (runtime / "ready").exists():
            stage(dependencies)
            commands = [
                ["python3.12", "-m", "venv", "--without-pip", str(runtime)],
                ["python3.12", "-m", "pip", "--isolated", "--python", str(python),
                 "install", "--no-index", "--only-binary=:all:", "--require-hashes",
                 "--find-links", str(ROOT / "wheels"),
                 "--find-links", str(dependencies / "wheels"),
                 "-r", str(ROOT / "kit/requirements.txt")],
            ]
            for command in commands:
                result = subprocess.run(command, env=env, capture_output=True, text=True)
                with (work / "install.log").open("a") as log:
                    log.write(portable(f"{command!r} -> {result.returncode}\n{result.stdout}{result.stderr}"))
                if result.returncode:
                    raise RuntimeError("offline runtime installation failed; see install.log")
            (runtime / "ready").touch()
    with (case / "case.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        record_path = logs / f"{label}.json"
        if record_path.exists():
            raise ValueError("label already recorded; choose a new label")
        kit = case / "kit"
        if not kit.exists():
            staging = case / "kit-staging"
            if staging.exists():
                shutil.rmtree(staging)
            shutil.copytree(ROOT / "kit", staging)
            staging.rename(kit)
        env["EIK_BUILD_DIR"] = str(case / "build")
        env["EIK_THREADS"] = "2"
        env["ZIG_GLOBAL_CACHE_DIR"] = str(case / "build/zig-cache")
        env["ZIG_LOCAL_CACHE_DIR"] = env["ZIG_GLOBAL_CACHE_DIR"]
        command = [str(python), "-m", "eik", *args]
        start = time.monotonic()
        result = subprocess.run(command, cwd=kit, env=env, capture_output=True, text=True,
                                errors="replace")
        stdout, stderr = portable(result.stdout), portable(result.stderr)
        (logs / f"{label}.stdout").write_text(stdout)
        (logs / f"{label}.stderr").write_text(stderr)
        write_json(record_path, {"argv": [portable(str(a)) for a in command],
                                "exit_code": result.returncode, "source_sha256": source_hash,
                                "stdout_sha256": sha256(stdout.encode()).hexdigest(),
                                "stderr_sha256": sha256(stderr.encode()).hexdigest(),
                                "seconds": round(time.monotonic() - start, 3)})
        return result.returncode, stdout, stderr


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependencies", type=Path, default=DEFAULT)
    parser.add_argument("work", type=Path)
    parser.add_argument("case")
    parser.add_argument("label")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        code, stdout, stderr = runner(args.work, args.case, args.label, args.command, args.dependencies)
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"runner failed: {exc}", file=sys.stderr)
        return 1
    print(stdout, end="")
    print(stderr, file=sys.stderr, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
