#!/usr/bin/env python3
"""Collect a cold replay in new scratch under an isolated Linux network namespace."""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CHECKERS = ("host", "rv32im", "thumbv6m", "thumbv7em")
CHUNKS = "1016:1017"
ENV = {"PATH": "/usr/local/bin:/usr/bin:/bin", "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"}


def interfaces():
    return sorted(line.split(":")[0].strip()
                  for line in Path("/proc/net/dev").read_text().splitlines()[2:])


def commands(scratch):
    if scratch.is_relative_to(REPO):
        scratch = scratch.relative_to(REPO)
    deps = str(scratch / "dependencies")
    toolkit = "eik-work/toolkit"
    runner = ["python3", f"{toolkit}/run.py", "--dependencies", deps, str(scratch / "work")]
    specs = {
        "network-interfaces": ["cat", "/proc/net/dev"],
        "python": ["python3", "--version"],
        "gcc": ["gcc", "--version"],
        "prepare": ["python3", "eik-work/offline-runtime/prepare.py", deps],
        "bootstrap": ["python3", f"{toolkit}/verify.py", "bootstrap", "--offline",
                      "--dependencies", deps],
        "setup": [*runner, "smoke", "setup", "setup"],
        "fingerprint": [*runner, "smoke", "fingerprint", "fingerprint", "--details"],
        "check": [*runner, "smoke", "check", "check", "entry.c"],
    }
    for name in CHECKERS:
        action = ["fullcheck"] if name == "host" else ["targetcheck"]
        limit = ["--threads", "1"] if name == "host" else ["--target", name, "--jobs", "1"]
        specs[name] = [*runner, "smoke", name, *action, "entry.c", "--function", "exp",
                       "--chunks", CHUNKS, *limit, "--out", str(scratch / f"{name}.json")]
    return specs


def dump(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scratch", type=Path, help="new replay directory")
    parser.add_argument("--parent-net", help=argparse.SUPPRESS)
    args = parser.parse_args()
    scratch = args.scratch.resolve()
    if args.parent_net is None:
        return subprocess.call(
            ["unshare", "-Urn", sys.executable, str(__file__), str(scratch),
             "--parent-net", os.readlink("/proc/self/ns/net")], env=ENV, cwd=REPO)

    scratch.mkdir(parents=True)
    evidence = scratch / "evidence"
    evidence.mkdir()
    isolation = {"parent_net": args.parent_net, "child_net": os.readlink("/proc/self/ns/net"),
                 "interfaces": interfaces(), "system": platform.system(),
                 "machine": platform.machine(), "new_scratch": True}
    dump(evidence / "isolation.json", isolation)
    if isolation["parent_net"] == isolation["child_net"] or isolation["interfaces"] != ["lo"]:
        print("Expected a fresh network namespace with only loopback", file=sys.stderr)
        return 1
    home = scratch / "home"
    home.mkdir()
    env = {**ENV, "HOME": str(home), "TMPDIR": str(home)}
    records = []
    for name, argv in commands(scratch).items():
        with (evidence / f"{name}.stdout").open("wb") as out, (evidence / f"{name}.stderr").open("wb") as err:
            code = subprocess.call(argv, cwd=REPO, env=env, stdout=out, stderr=err)
        print(f"{name} exited {code}", flush=True)
        records.append({"name": name, "argv": argv, "exit_code": code})
        dump(evidence / "commands.json", records)
        if name in {"prepare", "bootstrap", "setup"} and code:
            break

    work = scratch / "work"
    if (work / "install.log").is_file():
        shutil.copyfile(work / "install.log", evidence / "install.log")
    logs = work / "cases/smoke/logs"
    if logs.is_dir():
        shutil.copytree(logs, evidence / "kit-logs")
    for name in CHECKERS:
        report = scratch / f"{name}.json"
        if report.is_file():
            shutil.copyfile(report, evidence / f"{name}.report.json")
    return int(any(record["exit_code"] for record in records))


if __name__ == "__main__":
    raise SystemExit(main())
