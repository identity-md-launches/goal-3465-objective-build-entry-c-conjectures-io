#!/usr/bin/env python3
"""Assemble the rv32im/tanh coverage packet from a scratch toolkit work directory.

Usage (repository root): python3 eik-work/final-validation/coverage/rv32im-tanh/collect.py WORK HOSTLOGS
WORK is the toolkit/run.py work directory used for the rerun (cases rv32im-tanh, repro-root,
repro-trials); HOSTLOGS holds the scratch provisioning/bootstrap/prepare logs and the GCC
download list. Only files below this directory are written.
"""
import gzip
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
import elfcheck as E  # noqa: E402

REL = HERE.relative_to(REPO).as_posix()
PIN = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
BUILD = "593e2420f5363dcb-3fd8738f07e4"


def h(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    return Path(path).resolve().relative_to(REPO).as_posix()


def portable(text):
    return text.replace(str(REPO), "$REPO")


def copy(src, dst, text=False):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if text:
        dst.write_text(portable(Path(src).read_text()))
    else:
        shutil.copyfile(src, dst)
    return dst


def gz(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as out:
        out.write(Path(src).read_bytes())
    return dst


def main():
    work, hostlogs = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    cases = work / "cases"
    for sub in ("rerun", "host"):
        if (HERE / sub).exists():
            shutil.rmtree(HERE / sub)
    logs = HERE / "rerun/logs"
    for case, labels in (("rv32im-tanh", ("targetcheck-rv32im-tanh-all", "fingerprint", "setup")),
                         ("repro-root", ("probe-root",)), ("repro-trials", ("probe-trials",))):
        for label in labels:
            for ext in ("json", "stdout", "stderr"):
                copy(cases / case / "logs" / f"{label}.{ext}", logs / f"{label}.{ext}")
    copy(work / "install.log", HERE / "rerun/install.log")
    objects = HERE / "rerun/objects"
    build = cases / "rv32im-tanh/build"
    copy(build / BUILD / "target-check-rv32im.elf", objects / "target-check-rv32im.elf")
    copy(build / BUILD / "sub-rv32im.o", objects / "sub-rv32im.o")
    zig_objects = {}
    for obj in sorted((build / "zig-cache/o").glob("*/*.o")):
        zig_objects[obj.name] = {"zig_cache_key": obj.parent.name, "sha256": h(obj), "bytes": obj.stat().st_size}
        if obj.name != "compiler_rt_zcu.o":
            copy(obj, objects / "zig-cache" / obj.name)
    zig_objects["compiler_rt_zcu.o"]["retained"] = False
    zig_objects["compiler_rt_zcu.o"]["note"] = ("zig's own compiler_rt build product (1.8 MB), identified by digest only; "
                                                "its linked contribution is inside the retained image's .text")
    for case in ("repro-root", "repro-trials"):
        for name in ("target-check-rv32im.elf", "sub-rv32im.o"):
            gz(cases / case / "build" / BUILD / name, HERE / "rerun/probes" / case / f"{name}.gz")
    host = HERE / "host"
    for name in ("provision.stdout", "prepare.stdout", "prepare.stderr", "bootstrap.stdout", "bootstrap.stderr",
                 "bootstrap2.stdout", "bootstrap2.stderr"):
        copy(hostlogs / name, host / name, text=True)
    copy(hostlogs / "debs/uris.txt", host / "gcc-debs-uris.txt")
    copy(hostlogs / "deps/qemu/bin/gcc", host / "gcc-wrapper.sh", text=True)

    report = json.loads((logs / "targetcheck-rv32im-tanh-all.stdout").read_text())
    image = objects / "target-check-rv32im.elf"
    main_summary = E.summary(image.read_bytes())
    obj_summary = E.summary((objects / "sub-rv32im.o").read_bytes())
    probes = {}
    for case, label in (("repro-root", "probe-root"), ("repro-trials", "probe-trials")):
        rep = json.loads((logs / f"{label}.stdout").read_text())
        img = gzip.decompress((HERE / "rerun/probes" / case / "target-check-rv32im.elf.gz").read_bytes())
        obj = gzip.decompress((HERE / "rerun/probes" / case / "sub-rv32im.o.gz").read_bytes())
        si, so = E.summary(img), E.summary(obj)
        probes[case] = {
            "report": f"{REL}/rerun/logs/{label}.stdout", "source_path": json.loads(
                (logs / f"{label}.json").read_text())["argv"][4],
            "image_sha256": sha256(img).hexdigest(), "reported_image_sha256": rep["image_sha256"],
            "chunks": [rep["chunk_lo"], rep["chunk_hi"]], "verdict": rep["verdict"], "mismatches": rep["mismatches"],
            "image_executable_view_equal": E.executable_view(si) == E.executable_view(main_summary),
            "image_metadata_differences": E.metadata_differences(main_summary, si),
            "object_sha256": sha256(obj).hexdigest(),
            "object_executable_view_equal": E.executable_view(so) == E.executable_view(obj_summary),
            "object_metadata_differences": E.metadata_differences(obj_summary, so),
            "counts_toward_coverage": False,
        }
    prior_dir = REPO / "eik-work/trials/m0-tanh-refine"
    packet = json.loads((prior_dir / "packet.json").read_text())
    prior_entry = packet["runs"]["targetcheck-rv32im-tanh-all"]
    prior_report = json.loads((prior_dir / "targetcheck-rv32im-tanh-all.stdout").read_text())
    prior_files = {n: {"path": rel(prior_dir / n), "sha256": h(prior_dir / n),
                       "packet_sha256": prior_entry["files"][n]} for n in prior_entry["files"]}
    fp = json.loads((logs / "fingerprint.stdout").read_text())
    manifest_fp = json.loads((REPO / "eik-work/toolkit/manifest.json").read_text())["fingerprint"]

    coverage = {
        "schema": "rv32im-tanh-coverage-1",
        "function": "tanh",
        "target": "rv32im",
        "status": "pass",
        "source": {"path": "entry.c", "sha256": h(REPO / "entry.c"), "pinned_sha256": PIN,
                   "trials_copy": {"path": "eik-work/trials/m0-tanh-refine/entry.c",
                                   "sha256": h(prior_dir / "entry.c")}},
        "runtime": {
            "fingerprint": {"verifier": fp["verifier"], "measurement": fp["measurement"], "sandbox": fp["sandbox"],
                            "mode": fp["mode"], "production_problems": fp["production_problems"]},
            "toolkit_manifest_fingerprint": {"verifier": manifest_fp["verifier"],
                                             "measurement": manifest_fp["measurement"]},
            "tools": fp["details"]["tools"],
            "fingerprint_log": f"{REL}/rerun/logs/fingerprint.stdout",
            "kit": "eik-work/toolkit/kit (copied unchanged by toolkit/run.py into each case)",
            "dependencies": ("eik-work/toolkit/provision.py --fetch into a scratch cache: every wheel, both QEMU "
                             "executables and the QEMU source archives verified against toolkit pins"),
            "host_cc": ("exact Ubuntu noble gcc-13 13.3.0-6ubuntu2~24.04.1 packages unpacked in scratch (SHA-512 from "
                        "the apt index, see host/gcc-debs-uris.txt), reached as 'gcc' through host/gcc-wrapper.sh "
                        "on the toolkit runner PATH; the rv32im targetcheck path compiles only with zig and runs QEMU, "
                        "gcc is consulted for its --version line inside the fingerprint"),
        },
        "selected_set": "rerun",
        "ranges": [{
            "chunk_lo": report["chunk_lo"], "chunk_hi": report["chunk_hi"], "words": report["words_checked"],
            "provenance": "rerun", "report": f"{REL}/rerun/logs/targetcheck-rv32im-tanh-all.stdout",
            "report_sha256": h(logs / "targetcheck-rv32im-tanh-all.stdout"),
            "record": f"{REL}/rerun/logs/targetcheck-rv32im-tanh-all.json",
            "record_sha256": h(logs / "targetcheck-rv32im-tanh-all.json"),
            "image": f"{REL}/rerun/objects/target-check-rv32im.elf", "image_sha256": h(image),
            "fingerprint": report["fingerprint"], "verdict": report["verdict"], "mismatches": report["mismatches"],
            "complete": report["complete"], "range_complete": report["range_complete"],
        }],
        "totals": {"chunks": 4096, "words": 4294967296, "mismatches": 0, "gaps": [], "overlaps": []},
        "image_identity": {
            "image": f"{REL}/rerun/objects/target-check-rv32im.elf",
            "sha256": h(image), "reported_image_sha256": report["image_sha256"],
            "summary": E.executable_view(main_summary),
            "object": {"path": f"{REL}/rerun/objects/sub-rv32im.o", "sha256": h(objects / "sub-rv32im.o"),
                       "summary": E.executable_view(obj_summary)},
            "zig_cache_objects": zig_objects,
            "reproduction_probes": probes,
            "note": ("Linked image hashes differ per case directory because .debug_*, .symtab and the section-header "
                     "location embed paths; loaded segments (header fields locating the section table and non-load "
                     "p_offset masked), alloc sections, entry point, kernel symbols and alloc relocations are equal."),
        },
        "prior": {
            "status": "audited-not-reused",
            "report": rel(prior_dir / "targetcheck-rv32im-tanh-all.stdout"),
            "packet": rel(prior_dir / "packet.json"),
            "packet_command": prior_entry["command"], "packet_exit_code": prior_entry["exit_code"],
            "files": prior_files,
            "facts": {k: prior_report[k] for k in ("chunk_lo", "chunk_hi", "complete", "range_complete", "mismatches",
                                                    "words_checked", "verdict", "fingerprint", "image_sha256",
                                                    "sha256", "function", "target", "jobs", "reasons")},
            "reason": ("Raw hashes, command/source binding, fingerprint, exit, verdict and range all check, but the "
                       "recorded image 4c46aa4f... was linked under test/scratch (deleted) and no object or guest "
                       "file was retained, so the image hash cannot be bound to bytes or proven equivalent. The "
                       "fresh rerun is the selected set; old and new reports are kept separate."),
        },
        "failures": [
            {"step": "offline-runtime/prepare.py", "exit_code": 1, "log": f"{REL}/host/prepare.stderr",
             "effect": "reduced export lacks unicorn/ziglang wheels and QEMU orig source; provision.py --fetch used"},
            {"step": "toolkit/verify.py bootstrap --offline", "exit_code": 1, "log": f"{REL}/host/bootstrap2.stderr",
             "effect": "bootstrap compiles with gcc under a fixed /usr/bin:/bin PATH; this host has no system gcc"},
            {"step": "toolkit/run.py setup", "exit_code": 1, "log": f"{REL}/rerun/logs/setup.stderr",
             "effect": "same gcc PATH limitation; setup only prepares evaluate state and is not used by targetcheck"},
        ],
        "gaps": [],
    }
    (HERE / "coverage.json").write_text(json.dumps(coverage, indent=1, sort_keys=True) + "\n")
    write_result(coverage, report)


COMMANDS = [
    {"command": "python3 eik-work/toolkit/provision.py --fetch --dependencies test/scratch/deps", "exit_code": 0,
     "log": f"{REL}/host/provision.stdout"},
    {"command": "python3 eik-work/offline-runtime/prepare.py test/scratch/prep-deps", "exit_code": 1,
     "log": f"{REL}/host/prepare.stderr"},
    {"command": "python3 eik-work/toolkit/verify.py bootstrap --offline --dependencies test/scratch/deps",
     "exit_code": 1, "log": f"{REL}/host/bootstrap.stderr"},
    {"command": "PATH=test/scratch/deps/qemu/bin:$PATH python3 eik-work/toolkit/verify.py bootstrap --offline "
                "--dependencies test/scratch/deps", "exit_code": 1, "log": f"{REL}/host/bootstrap2.stderr"},
    {"command": "python3 eik-work/toolkit/run.py --dependencies test/scratch/deps test/scratch/rvtanh rv32im-tanh "
                "setup setup", "exit_code": 1, "log": f"{REL}/rerun/logs/setup.json"},
    {"command": "python3 eik-work/toolkit/run.py --dependencies test/scratch/deps test/scratch/rvtanh rv32im-tanh "
                "fingerprint fingerprint --details", "exit_code": 0, "log": f"{REL}/rerun/logs/fingerprint.json"},
    {"command": "python3 eik-work/toolkit/run.py --dependencies test/scratch/deps test/scratch/rvtanh rv32im-tanh "
                "targetcheck-rv32im-tanh-all targetcheck entry.c --function tanh --target rv32im --chunks 0:4096 "
                "--jobs 2", "exit_code": 0, "log": f"{REL}/rerun/logs/targetcheck-rv32im-tanh-all.json"},
    {"command": "python3 eik-work/toolkit/run.py --dependencies test/scratch/deps test/scratch/rvtanh repro-root "
                "probe-root targetcheck entry.c --function tanh --target rv32im --chunks 0:1 --jobs 1",
     "exit_code": 0, "log": f"{REL}/rerun/logs/probe-root.json"},
    {"command": "python3 eik-work/toolkit/run.py --dependencies test/scratch/deps test/scratch/rvtanh repro-trials "
                "probe-trials targetcheck eik-work/trials/m0-tanh-refine/entry.c --function tanh --target rv32im "
                "--chunks 0:1 --jobs 1", "exit_code": 0, "log": f"{REL}/rerun/logs/probe-trials.json"},
]


def write_result(coverage, report):
    files = sorted(p for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts
                   and p.name != "result.json")
    result = {
        "schema": "rv32im-tanh-result-1",
        "status": coverage["status"],
        "function": "tanh", "target": "rv32im",
        "source": {"path": "entry.c", "sha256": coverage["source"]["sha256"]},
        "runtime": {**coverage["runtime"]["fingerprint"], "tools": coverage["runtime"]["tools"]},
        "toolkit": {"run.py": h(REPO / "eik-work/toolkit/run.py"),
                    "provision.py": h(REPO / "eik-work/toolkit/provision.py"),
                    "manifest.json": h(REPO / "eik-work/toolkit/manifest.json")},
        "commands": COMMANDS,
        "measured": {"chunks": [report["chunk_lo"], report["chunk_hi"]], "words_checked": report["words_checked"],
                     "mismatches": report["mismatches"], "verdict": report["verdict"],
                     "complete": report["complete"], "range_complete": report["range_complete"],
                     "evaluator_seconds": report["seconds"], "jobs": report["jobs"],
                     "image_sha256": report["image_sha256"]},
        "prior": {"status": coverage["prior"]["status"], "image_sha256": coverage["prior"]["facts"]["image_sha256"]},
        "failures": coverage["failures"],
        "gaps": coverage["gaps"],
        "artifacts": {rel(p): h(p) for p in files},
    }
    (HERE / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
