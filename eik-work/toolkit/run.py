#!/usr/bin/env python3
"""Run the pinned local evaluator with an offline runtime and case-local state."""
import argparse
import base64
import csv
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
import zipfile

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


def python312():
    """A Python 3.12 interpreter; the evaluator pins that minor version."""
    if sys.version_info[:2] == (3, 12):
        return sys.executable
    found = shutil.which("python3.12", path="/usr/local/bin:/usr/bin:/bin")
    if found is None:
        raise ValueError("Python 3.12 is required")
    return found


def requirements():
    """Parse the kit's hash-pinned requirements into {name: (version, {sha256, ...})}."""
    text = (ROOT / "kit/requirements.txt").read_text().replace("\\\n", " ")
    pins = {}
    for line in text.splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        spec, *options = line.split()
        name, sep, version = spec.partition("==")
        hashes = {o.removeprefix("--hash=sha256:") for o in options if o.startswith("--hash=sha256:")}
        if not sep or not hashes or len(hashes) != len(options):
            raise ValueError(f"requirement is not hash-pinned: {line}")
        pins[name.lower()] = (version, hashes)
    return pins


def unpack_wheel(wheel, site, scripts):
    """Install one binary wheel without pip: check every member against RECORD, then unpack it."""
    with zipfile.ZipFile(wheel) as archive:
        names = [i.filename for i in archive.infolist() if not i.is_dir()]
        info = {n.split("/")[0] for n in names if n.split("/")[0].endswith(".dist-info")}
        if len(info) != 1:
            raise ValueError(f"{wheel.name}: expected one dist-info directory")
        info = info.pop()
        data = info.removesuffix(".dist-info") + ".data"
        record = {}
        for row in csv.reader(archive.read(f"{info}/RECORD").decode().splitlines()):
            if row:
                record[row[0]] = row[1]
        count = 0
        for member in archive.infolist():
            name = member.filename
            if member.is_dir():
                continue
            mode = member.external_attr >> 16
            if name.startswith("/") or ".." in name.split("/") or (mode & 0o170000) not in (0, 0o100000):
                raise ValueError(f"{wheel.name}: unsafe member {name}")
            content = archive.read(member)
            expected = record.get(name, "")
            if expected.startswith("sha256="):
                actual = base64.urlsafe_b64encode(sha256(content).digest()).rstrip(b"=").decode()
                if actual != expected.removeprefix("sha256="):
                    raise ValueError(f"{wheel.name}: RECORD mismatch for {name}")
            elif not (name == f"{info}/RECORD" or name.startswith(f"{info}/RECORD.")):
                raise ValueError(f"{wheel.name}: {name} is not covered by RECORD")
            parts = name.split("/")
            if parts[0] == data:
                if len(parts) < 3 or parts[1] not in {"purelib", "platlib", "scripts"}:
                    raise ValueError(f"{wheel.name}: unsupported data member {name}")
                target = (scripts if parts[1] == "scripts" else site).joinpath(*parts[2:])
            else:
                target = site.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            target.chmod(0o755 if mode & 0o111 else 0o644)
            count += 1
        (site / info / "INSTALLER").write_text("eik-toolkit\n")
        return count


def install_runtime(runtime, links, env, log_path):
    """Create the isolated interpreter and unpack the pinned wheels; needs neither pip nor a network."""
    def note(text):
        with log_path.open("a") as log:
            log.write(portable(text) + "\n")

    if runtime.exists():
        shutil.rmtree(runtime)
    command = [python312(), "-m", "venv", "--without-pip", str(runtime)]
    result = subprocess.run(command, env=env, capture_output=True, text=True)
    note(f"{command!r} -> {result.returncode}\n{result.stdout}{result.stderr}".rstrip())
    if result.returncode:
        raise ValueError("could not create the Python 3.12 environment")
    python = runtime / "bin/python"
    site = Path(subprocess.run([str(python), "-I", "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
                               env=env, capture_output=True, text=True, check=True).stdout.strip())
    if not site.is_relative_to(runtime):
        raise ValueError("environment site-packages is outside the runtime")
    for name, (version, hashes) in requirements().items():
        prefix = f"{name}-{version}-"
        found = [p for link in links if link.is_dir() for p in sorted(link.glob("*.whl"))
                 if p.name.lower().startswith(prefix) and sha256(p.read_bytes()).hexdigest() in hashes]
        if not found:
            raise ValueError(f"no wheel with a pinned hash for {name}=={version}")
        wheel = found[0]
        count = unpack_wheel(wheel, site, runtime / "bin")
        note(f"installed {name}=={version} from {wheel} sha256={sha256(wheel.read_bytes()).hexdigest()} "
             f"({count} files, every member checked against RECORD)")
    probe = ("import json; from importlib import metadata as m; import unicorn, capstone, elftools, ziglang; "
             "print(json.dumps({n: m.version(n) for n in ('capstone', 'pyelftools', 'unicorn', 'ziglang')}))")
    result = subprocess.run([str(python), "-I", "-c", probe], env=env, capture_output=True, text=True)
    note(f"import probe -> {result.returncode}\n{result.stdout}{result.stderr}".rstrip())
    if result.returncode:
        raise ValueError("installed packages do not import")
    wanted = {name: version for name, (version, _) in requirements().items()}
    if json.loads(result.stdout) != wanted:
        raise ValueError("installed package versions differ from the pins")


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
            log_path = work / "install.log"
            try:
                install_runtime(runtime, [ROOT / "wheels", dependencies / "wheels"], env, log_path)
            except (ValueError, OSError, KeyError, zipfile.BadZipFile, subprocess.SubprocessError) as exc:
                with log_path.open("a") as log:
                    log.write(portable(f"installation failed: {exc}\n"))
                raise RuntimeError(f"offline runtime installation failed ({portable(str(exc))}); "
                                   "see install.log") from exc
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
