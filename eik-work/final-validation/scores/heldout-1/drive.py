#!/usr/bin/env python3
"""Scratch driver: run pinned toolkit/run.py steps for one case, with a wall-clock cap, and retain records."""
import hashlib, json, os, shutil, signal, subprocess, sys, time
from pathlib import Path
REPO = Path.cwd()
T = "eik-work/toolkit"
WORK = "test/scratch/h1w"
OUT = REPO / "eik-work/final-validation/scores/heldout-1/raw"
SEED = "849230117"
CAND = "entry.c"
ID50 = "eik-work/baselines/former-50/entry.c"
def sha(b): return hashlib.sha256(b).hexdigest()
def step(case, label, args, cap=None):
    argv = [sys.executable, f"{T}/run.py", WORK, case, label, *args]
    t0 = time.time(); started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    timed_out = False
    try:
        so, se = p.communicate(timeout=cap)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(p.pid, signal.SIGKILL)
        so, se = p.communicate()
    d = OUT / case; d.mkdir(parents=True, exist_ok=True)
    so = so.decode(errors="replace").replace(str(REPO), "$REPO"); se = se.decode(errors="replace").replace(str(REPO), "$REPO")
    (d / f"{label}.stdout").write_text(so); (d / f"{label}.stderr").write_text(se)
    rec = {"case": case, "label": label, "argv": ["python3", *argv[1:]], "exit_code": p.returncode,
           "timed_out": timed_out, "cap_seconds": cap, "seconds": round(time.time() - t0, 3), "started_utc": started,
           "stdout": f"raw/{case}/{label}.stdout", "stdout_sha256": sha(so.encode()),
           "stderr": f"raw/{case}/{label}.stderr", "stderr_sha256": sha(se.encode())}
    inner = REPO / WORK / "cases" / case / "logs" / f"{label}.json"
    if inner.exists():
        shutil.copy(inner, d / f"{label}.runner.json")
        rec["runner_record"] = f"raw/{case}/{label}.runner.json"
        rec["runner_record_sha256"] = sha((d / f"{label}.runner.json").read_bytes())
    else:
        rec["runner_record"] = None
    cmds = d / "commands.json"
    lst = json.loads(cmds.read_text()) if cmds.exists() else []
    lst.append(rec); cmds.write_text(json.dumps(lst, indent=1) + "\n")
    print(case, label, "exit", p.returncode, "timeout", timed_out, rec["seconds"], flush=True)
    return rec, so
def pools(case):
    src = REPO / WORK / "cases" / case / "build" / "hard"
    d = OUT / case / "hard"; d.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob(f"*-{SEED}-*.txt")):
        shutil.copy(f, d / f.name)
def fallback(case, src):
    step(case, "fallback-measure", ["measure", src, "--seed", SEED])
    for fn in ("sigmoid", "tanh", "exp"):
        step(case, f"fallback-fullcheck-quick-{fn}", ["fullcheck", src, "--function", fn, "--quick", "--seed", SEED])
def evaluated(rec, so):
    if rec["timed_out"]: return False
    try: return json.loads(so).get("status") is not None
    except Exception: return False
case = sys.argv[1]
if case == "cand":
    step(case, "setup", ["setup"]); step(case, "fingerprint", ["fingerprint", "--details"])
    step(case, "check", ["check", CAND])
    rec, so = step(case, "evaluate-849230117", ["evaluate", CAND, "--quick", "--json", "--seed", SEED], cap=600)
    if not evaluated(rec, so): fallback(case, CAND)
    step(case, "historical-compare-id50", ["compare", CAND, "--seed", SEED, "--champion", f"rv32im={ID50}",
         "--champion", f"thumbv6m={ID50}", "--champion", f"overall={ID50}"])
    pools(case)
elif case == "id50":
    step(case, "setup", ["setup"]); step(case, "fingerprint", ["fingerprint", "--details"])
    step(case, "check", ["check", ID50])
    rec, so = step(case, "evaluate-849230117", ["evaluate", ID50, "--quick", "--json", "--seed", SEED], cap=600)
    if not evaluated(rec, so): fallback(case, ID50)
    step(case, "measure-849230117", ["measure", ID50, "--seed", SEED])
    pools(case)
