#!/usr/bin/env python3
"""Run the held-out replay through the pinned offline toolkit runner."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUNNER = "eik-work/toolkit/run.py"
WORK = "test/scratch/heldout2"
RAW = HERE / "raw"
SEED = "2715043869"
CANDIDATE = "entry.c"
ID50 = "eik-work/baselines/former-50/entry.c"
FUNCTIONS = ("sigmoid", "tanh", "exp")
BOARDS = ("rv32im", "thumbv6m", "overall")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(case, label, args, cap_scope=None):
    case_dir = ROOT / WORK / "cases" / case
    out = RAW / case
    out.mkdir(parents=True, exist_ok=True)
    argv = [RUNNER, WORK, case, label, *args]
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    start = time.monotonic()
    process = subprocess.run([sys.executable, *argv], cwd=ROOT, capture_output=True,
                             start_new_session=True)
    marker = case_dir / "tmp/incumbent-comparison-timeout"
    timed_out = cap_scope == "compare" and marker.is_file()
    record = {"case": case, "label": label, "argv": ["python3.12", *argv],
              "exit_code": process.returncode, "timed_out": timed_out,
              "cap_seconds": 600 if cap_scope else None, "cap_scope": cap_scope,
              "seconds": round(time.monotonic() - start, 3), "started_utc": started}
    streams = {"stdout": process.stdout,
               "stderr": process.stderr + (marker.read_bytes() if timed_out else b"")}
    for stream, data in streams.items():
        output = out / f"{label}.{stream}"
        output.write_text(data.decode(errors="replace").replace(str(ROOT), "$REPO"))
        record[stream] = str(output.relative_to(HERE))
        record[f"{stream}_sha256"] = sha(output.read_bytes())
    inner = case_dir / "logs" / f"{label}.json"
    record["runner_record"] = None
    if inner.is_file():
        output = out / f"{label}.runner.json"
        shutil.copyfile(inner, output)
        record["runner_record"] = str(output.relative_to(HERE))
        record["runner_record_sha256"] = sha(output.read_bytes())
    ledger = out / "commands.json"
    existing = json.loads(ledger.read_text()) if ledger.is_file() else []
    ledger.write_text(json.dumps([*existing, record], indent=1) + "\n")
    print(case, label, "exit", process.returncode, "timeout", timed_out, record["seconds"], flush=True)
    if process.returncode and not timed_out:
        raise SystemExit(process.returncode)
    return timed_out


def install_watchdog():
    runtime = ROOT / WORK / "runtime"
    site = Path(subprocess.check_output(
        [runtime / "bin/python", "-I", "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
        text=True).strip())
    if not site.is_relative_to(runtime):
        raise ValueError("watchdog destination is outside the scratch runtime")
    shutil.copyfile(HERE / "compare_watchdog.py", site / "heldout2_compare_watchdog.py")
    (site / "heldout2_watchdog.pth").write_text("import heldout2_compare_watchdog\n")
    shutil.copyfile(ROOT / WORK / "install.log", RAW / "replay-install.log")


def copy_pools(case):
    pools = ROOT / WORK / "cases" / case / "build/hard"
    destination = RAW / case / "hard"
    destination.mkdir(exist_ok=True)
    for pool in sorted(pools.glob(f"*-{SEED}-*.txt")):
        shutil.copyfile(pool, destination / pool.name)


def candidate(case):
    run(case, "fingerprint", ["fingerprint", "--details"])
    run(case, "check", ["check", CANDIDATE])
    case_dir = ROOT / WORK / "cases" / case
    state = case_dir / "kit/state/boards.json"
    shutil.copyfile(state, RAW / case / "incumbent-state.json")
    timed_out = run(case, "evaluate-phase-scoped",
                    ["evaluate", CANDIDATE, "--quick", "--json", "--seed", SEED], "compare")
    shutil.copyfile(state, RAW / case / "incumbent-state-after.json")
    marker = "incumbent-comparison-timeout" if timed_out else "incumbent-comparison-seconds"
    shutil.copyfile(case_dir / "tmp" / marker, RAW / case / marker)
    if timed_out:
        run(case, "fallback-measure", ["measure", CANDIDATE, "--seed", SEED])
        for fn in FUNCTIONS:
            run(case, f"fallback-fullcheck-quick-{fn}",
                ["fullcheck", CANDIDATE, "--function", fn, "--quick", "--seed", SEED])
    run(case, "historical-compare-id50", [
        "compare", CANDIDATE, "--seed", SEED,
        *[arg for board in BOARDS for arg in ("--champion", f"{board}={ID50}")],
    ])
    copy_pools(case)


def main():
    action = sys.argv[1]
    if action in ("setup-scoped", "setup-scoped-clean", "setup-id50"):
        run(action.removeprefix("setup-"), "setup", ["setup"])
    elif action == "install-watchdog":
        install_watchdog()
    elif action in ("cand-scoped", "cand-scoped-clean"):
        candidate(action.removeprefix("cand-"))
    elif action == "id50":
        run("id50", "fingerprint", ["fingerprint", "--details"])
        run("id50", f"measure-{SEED}", ["measure", ID50, "--seed", SEED])
        copy_pools("id50")
    else:
        raise SystemExit(f"unknown replay action {action}")


if __name__ == "__main__":
    main()
