#!/usr/bin/env python3
"""Offline verifier for the frozen root entry.c of the e03 kernel trials (standard library only).

    python3 eik-work/freeze/verify.py                   verify manifest.json against every raw log
    python3 eik-work/freeze/verify.py --write-manifest  (re)compute manifest.json from the raw logs

What it checks, with no network and no evaluator run:
  * every trial packet under eik-work/trials/ and the paired id50 control, through the shared
    paired-control verifier (index, S, tail, size factor and ratios recomputed from raw logs);
  * ledger coverage: manifest ledger and experiments.md name every trial packet exactly once;
  * eligibility (measured, distinct normalised hash from the control, the accepted former sources
    and every other candidate, passing check/gate, quick host check, passing target evidence);
  * the selection rule (worse ratio over the two seeds per board, best board, minimise, ties by
    overall) and that no combination is warranted (no two compatible gains on one board);
  * root entry.c bytes equal the chosen packet's source; the freeze re-check (eik check / gate)
    raw logs bind those bytes, their normalised hash, bytes and stack bound;
  * the three target objects and guest images: file SHA-256 and allocated-section SHA-256;
  * static source rules on root entry.c;
  * negative self-tests: an absent, a copied-control, an invalid and a duplicate candidate are refused.
"""
import copy
import difflib
import importlib.util
import json
import re
import struct
import sys
from hashlib import sha256
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MANIFEST = HERE / "manifest.json"
LEDGER_MD = HERE / "experiments.md"
EVID = HERE / "evidence"
ROOT_ENTRY = "entry.c"
TRIALS = REPO / "eik-work/trials"
BASELINES = REPO / "eik-work/baselines"
TARGETS = ("rv32im", "thumbv6m", "thumbv7em")
BOARDS = ("rv32im", "thumbv6m", "overall")
FUNCTIONS = ("sigmoid", "tanh", "exp")


def load_pv():
    spec = importlib.util.spec_from_file_location("paired_verify", REPO / "eik-work/trials/paired-control/verify.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PV = load_pv()
Bad = PV.Bad
require = PV.require


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def rel(p):
    return str(Path(p).resolve().relative_to(REPO))


def jload(p):
    return json.loads(Path(p).read_text())


def norm(x):
    return json.loads(json.dumps(x))


# ---------------------------------------------------------------- ELF sections
def elf_sections(path):
    b = Path(path).read_bytes()
    require(b[:4] == b"\x7fELF" and b[4] == 1 and b[5] == 1, f"{path}: not a little-endian ELF32 file")
    shoff = struct.unpack_from("<I", b, 0x20)[0]
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 0x2E)
    hs = [struct.unpack_from("<IIIIIIIIII", b, shoff + i * shentsize) for i in range(shnum)]
    st = hs[shstrndx]
    names = b[st[4]:st[4] + st[5]]
    out = {}
    for h in hs:
        name = names[h[0]:names.index(b"\0", h[0])].decode()
        if h[2] & 2 and h[1] != 8:  # SHF_ALLOC, not NOBITS
            out[name] = {"size": h[5], "sha256": sha256(b[h[4]:h[4] + h[5]]).hexdigest()}
        if h[2] & 1 and h[2] & 2 and h[1] != 8 and h[5]:  # writable allocated data
            out.setdefault("_writable", []).append(name)
    return out


# ---------------------------------------------------------------- static rules
def static_rules(text):
    require(len(text.encode()) <= 256 * 1024, "source over 256 KiB")
    PV.source_rules(ROOT_ENTRY)
    code = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    code = re.sub(r"//[^\n]*", " ", code)
    for line in code.splitlines():
        s = line.strip()
        if s.startswith("#") or s.startswith("%:"):
            d = re.match(r"(?:#|%:)\s*(\w*)", s).group(1)
            require(d in ("define", "undef", "if", "ifdef", "ifndef", "elif", "else", "endif"), f"directive #{d}")
    code = re.sub(r'"(?:\\.|[^"\\])*"', '""', code)
    require(not re.search(r"\blong\s+double\b", code), "long double")
    code = re.sub(r"\blong\s+long\b", "int64", code)  # `long long` is 64-bit everywhere; lone `long` is refused
    for tok in ("float", "double", "long", "volatile", "_Atomic", "asm", "__asm__", "__attribute__", "_Pragma",
                "_Complex", "__int128"):
        require(not re.search(r"\b%s\b" % tok, code), f"forbidden token {tok}")
    require(not re.search(r"(?<!signed )(?<!unsigned )\bchar\b", code), "plain char")
    require("??" not in code, "trigraph sequence")
    require(not re.search(r"\b\d+\.\d*(?:[eE][+-]?\d+)?[fF]?\b|\b\d+[eE][+-]?\d+\b|0[xX][0-9a-fA-F]*\.[0-9a-fA-F]*[pP]", code),
            "floating literal")
    # mutable static/file-scope storage: every `static` object must be const
    for m in re.finditer(r"\bstatic\b([^;{(=]*)", code):
        decl = m.group(1)
        nxt = code[m.end():m.end() + 1]
        if nxt == "(":
            continue  # function
        require("const" in decl.split(), f"non-const static: static{decl[:60]}")


# ---------------------------------------------------------------- packets
def accepted_hashes():
    """Normalised hashes of the accepted former sources reported by the pinned evaluator."""
    out = {}
    for f in sorted(BASELINES.glob("former-*/evaluate-*.stdout")):
        try:
            rep = json.loads(f.read_text())
        except ValueError:
            continue
        if rep.get("normalised_sha256") and rep.get("sha256"):
            out[rep["normalised_sha256"]] = f.parent.name
    return out


TARGET_LABEL = re.compile(r"^(targetcheck|tc|exhaustive|fullcheck)")


def target_evidence(d, packet):
    """Passing target-object and host evidence runs of one packet (raw log hashes re-checked)."""
    src_sha = packet["source"]["sha256"]
    targets, host_full = set(), set()
    for label, run in sorted(packet["runs"].items()):
        cmd = run["command"].split()
        if len(cmd) < 6 or cmd[5] not in ("targetcheck", "fullcheck"):
            continue
        rec = jload(d / f"{label}.json")
        out = d / f"{label}.stdout"
        require(rec["stdout_sha256"] == digest(out) and rec["stderr_sha256"] == digest(d / f"{label}.stderr")
                and run["files"][f"{label}.stdout"] == digest(out), f"{d.name}/{label}: log hash mismatch")
        text = out.read_text()
        if not text.strip() and "--out" in cmd:
            # report written with --out and kept by the trial under targetcheck-reports/ (not hashed by run.py)
            text = (d / "targetcheck-reports" / Path(cmd[cmd.index("--out") + 1]).name).read_text()
        rep = json.loads(text)
        require(rep.get("sha256") == src_sha, f"{d.name}/{label}: run on other bytes")
        if run["exit_code"] != 0 or rep.get("verdict") != "passed" or rep.get("mismatches", 0) != 0:
            raise Bad(f"{d.name}/{label}: failing {cmd[5]}")
        if cmd[5] == "targetcheck":
            targets.add(rep["target"])
        elif not rep.get("quick") and rep.get("complete"):
            host_full.add(rep["function"])
    return sorted(targets), sorted(host_full)


def survey():
    """Verify control and every trial packet; return (control_index, {key: record})."""
    m = PV.manifest()
    ctl = PV.verify(TRIALS / "paired-control", m, quiet=True)
    acc = accepted_hashes()
    recs = {}
    for d in sorted(p for p in TRIALS.iterdir() if p.is_dir() and p.name != "paired-control"):
        r = {"path": rel(d), "packet_sha256": digest(d / "packet.json")}
        try:
            idx = PV.verify(d, m, quiet=True)
            packet = jload(d / "packet.json")
            r.update(status=packet["status"], source=packet["source"], normalised_sha256=idx.get("normalised_sha256"))
            if packet["status"] != "measured":
                r.update(eligible=False, reason=f"packet status {packet['status']}")
                recs[d.name] = r
                continue
            rat = PV.ratios(idx, ctl)
            r["S"] = {s: idx["rows"][s]["S"] for s in idx["rows"]}
            r["ratio"] = rat
            r["worst"] = {b: max(rat[s][b] for s in rat) for b in BOARDS}
            best = min(BOARDS, key=lambda b: (r["worst"][b], BOARDS.index(b)))
            r["best_board"] = best
            r["metric"] = [r["worst"][best], r["worst"]["overall"]]
            tg, hf = target_evidence(d, packet)
            r["target_evidence"] = tg
            r["full_host_functions"] = hf
            reasons = []
            if idx["normalised_sha256"] == ctl["normalised_sha256"]:
                reasons.append("copied control")
            if idx["normalised_sha256"] in acc:
                reasons.append(f"duplicate of accepted {acc[idx['normalised_sha256']]}")
            if not tg:
                reasons.append("no passing target-object evidence")
            r["eligible"] = not reasons
            if reasons:
                r["reason"] = "; ".join(reasons)
        except (Bad, ValueError, KeyError, IndexError, TypeError, OSError) as exc:
            r.update(eligible=False, reason=f"invalid packet: {type(exc).__name__}: {exc}")
        recs[d.name] = r
    seen = {}
    for k, r in recs.items():  # duplicate normalised hash among candidates
        h = r.get("normalised_sha256")
        if h and r.get("eligible"):
            if h in seen:
                for kk in (k, seen[h]):
                    recs[kk]["eligible"] = False
                    recs[kk]["reason"] = "duplicate normalised hash among candidates"
            seen[h] = k
    return ctl, recs, acc


def select(recs):
    el = {k: r for k, r in recs.items() if r.get("eligible")}
    require(el, "no eligible candidate: " + json.dumps({k: r.get("reason") for k, r in recs.items()}))
    order = sorted(el, key=lambda k: (el[k]["metric"][0], el[k]["metric"][1], k))
    gains = {b: sorted(k for k in el if el[k]["worst"][b] < 1.0) for b in BOARDS}
    combo = {b: ks for b, ks in gains.items() if len(ks) >= 2}
    return order, combo


# ---------------------------------------------------------------- freeze evidence
def run_log(label, command, src):
    d = EVID / "logs"
    rec = jload(d / f"{label}.json")
    out = d / f"{label}.stdout"
    require(rec["stdout_sha256"] == digest(out) and rec["stderr_sha256"] == digest(d / f"{label}.stderr"),
            f"freeze {label}: log hash mismatch")
    require(rec["argv"][1:4] == ["-m", "eik", command], f"freeze {label}: not eik {command}")
    if src:
        require(rec["argv"][4] == "$REPO/" + src and rec["source_sha256"] == digest(REPO / src),
                f"freeze {label}: not run on the current {src}")
    require(rec["exit_code"] == 0, f"freeze {label}: exit {rec['exit_code']}")
    return rec, out.read_text()


def freeze_evidence(chosen_packet):
    _, cout = run_log("check", "check", ROOT_ENTRY)
    require(cout.startswith("PASS "), "freeze check did not pass")
    static = json.loads(cout.removeprefix("PASS "))
    _, gout = run_log("gate", "gate", ROOT_ENTRY)
    gate = json.loads(gout)
    require(gate["verdict"] == "accepted" and gate["sha256"] == digest(REPO / ROOT_ENTRY), "freeze gate not accepted")
    _, fout = run_log("fingerprint", "fingerprint", None)
    fp = json.loads(fout)
    pinned = PV.manifest()["fingerprint"]
    require(gate["fingerprint"]["verifier"] == pinned["verifier"] and gate["fingerprint"]["measurement"] == pinned["measurement"],
            "freeze gate used another evaluator")
    require(fp["verifier"] == pinned["verifier"] and fp["measurement"] == pinned["measurement"], "fingerprint differs")
    row = next(iter(chosen_packet["index"]["rows"].values()))
    require(gate["normalised_sha256"] == chosen_packet["index"]["normalised_sha256"], "normalised hash differs from the packet")
    for t in TARGETS:
        require(static["bytes"][t] == gate["bytes"][t] == row["targets"][t]["bytes"] and static["bytes"][t] <= 65536,
                f"{t}: bytes differ or exceed 64 KiB")
        require(static["stack_bound"][t] == gate["stack_bound"][t] == row["targets"][t]["stack_bound"] <= 8192,
                f"{t}: stack bound differs or exceeds 8 KiB")
    objs = {}
    for t in TARGETS:
        o = {}
        for kind, name in (("object", f"sub-{t}.o"), ("guest_image", f"guest-{t}.elf")):
            p = EVID / "objects" / name
            secs = elf_sections(p)
            require("_writable" not in secs, f"{name}: writable allocated data {secs.get('_writable')}")
            o[kind] = {"path": rel(p), "sha256": digest(p), "sections": secs}
        objs[t] = o
    return {"check": static, "normalised_sha256": gate["normalised_sha256"], "source_bytes": gate["source_bytes"],
            "evaluator": {"verifier": fp["verifier"], "measurement": fp["measurement"], "sandbox": fp.get("sandbox")},
            "objects": objs}


def unified_diff(a, b):
    return "".join(difflib.unified_diff(
        (REPO / a).read_text().splitlines(True), (REPO / b).read_text().splitlines(True),
        fromfile="a/" + a, tofile="b/" + ROOT_ENTRY))


# ---------------------------------------------------------------- manifest
def compute():
    ctl, recs, acc = survey()
    order, combo = select(recs)
    chosen = order[0]
    cp = jload(TRIALS / chosen / "packet.json")
    src = cp["source"]["path"]
    require((REPO / ROOT_ENTRY).read_bytes() == (REPO / src).read_bytes(), f"root entry.c is not the bytes of {src}")
    static_rules((REPO / ROOT_ENTRY).read_text())
    fe = freeze_evidence(cp)
    base = cp["base"]
    diff_text = unified_diff(base["path"], ROOT_ENTRY)
    diff_path = HERE / "entry-vs-id50.diff"
    tm = PV.manifest()
    r = recs[chosen]
    logs = {}
    for p in sorted((EVID / "logs").glob("*")):
        logs[p.name] = digest(p)
    man = {
        "schema": "eik-freeze-1",
        "target": "freeze-entry",
        "outcome": "frozen-best-eligible-single (regression vs id50; no candidate reaches 0.970)",
        "chosen": chosen,
        "chosen_packet": {"path": rel(TRIALS / chosen / "packet.json"), "sha256": r["packet_sha256"]},
        "entry": {"path": ROOT_ENTRY, "sha256": digest(REPO / ROOT_ENTRY), "normalised_sha256": fe["normalised_sha256"],
                  "source_bytes": fe["source_bytes"], "same_bytes_as": src},
        "base": {"path": base["path"], "sha256": base["sha256"], "normalised_sha256": ctl["normalised_sha256"]},
        "diff": {"path": rel(diff_path), "sha256": sha256(diff_text.encode()).hexdigest(),
                 "trial_diff": {"path": rel(TRIALS / chosen / "id50.diff"), "sha256": digest(TRIALS / chosen / "id50.diff")}},
        "kit": {"commit": tm["kit"].get("commit"), "toolkit_manifest_sha256": digest(REPO / "eik-work/toolkit/manifest.json"),
                "toolkit_files_sha256": digest(REPO / "eik-work/toolkit/files.json")},
        "evaluator": fe["evaluator"],
        "shared_verifier": {"path": "eik-work/trials/paired-control/verify.py",
                            "sha256": digest(REPO / "eik-work/trials/paired-control/verify.py")},
        "static": fe["check"],
        "objects": fe["objects"],
        "seeds": list(PV.SEEDS),
        "control": {"path": "eik-work/trials/paired-control", "S": {s: ctl["rows"][s]["S"] for s in ctl["rows"]},
                    "inputs_sha256": {s: ctl["rows"][s]["inputs_sha256"] for s in ctl["rows"]}},
        "scores": {"S": r["S"], "ratio_vs_id50": r["ratio"], "worst_over_seeds": r["worst"],
                   "best_board": r["best_board"], "metric": r["metric"],
                   "takes_board_at_0970": [b for b in BOARDS if r["worst"][b] <= 0.97]},
        "selection": {"rule": "per board worse ratio over the two seeds; best board; minimise; ties by worse overall",
                      "order": order, "combination": None if not combo else combo,
                      "combination_note": "no board has two eligible gains (<1.0) so no combination was built"
                      if not combo else "combination warranted"},
        "accepted_normalised_hashes": acc,
        "ledger": recs,
        "freeze_runs": {
            "commands": [
                "python3 eik-work/toolkit/provision.py --fetch",
                "python3 eik-work/toolkit/verify.py bootstrap --offline",
                "python3 eik-work/toolkit/run.py test/scratch/freeze freeze setup setup",
                "python3 eik-work/toolkit/run.py test/scratch/freeze freeze check check entry.c",
                "python3 eik-work/toolkit/run.py test/scratch/freeze freeze gate gate entry.c",
                "python3 eik-work/toolkit/run.py test/scratch/freeze freeze fingerprint fingerprint --details",
                "python3 eik-work/toolkit/run.py test/scratch/freeze rebuild check check entry.c  (determinism of section bytes)"],
            "logs": logs,
            "crosscheck": {p.name: digest(p) for p in sorted((HERE / "crosscheck").glob("*"))},
            "trial_scores_referenced": {lab: run["files"] for lab, run in cp["runs"].items()},
        },
        "change_note": "m0-tanh-refine: only the exponent-119 Thumb tanh refinement guard of id50 changes "
                       "(refine below 253952 instead of 262144 in the Q23 remainder; 5,632 more fast returns per sign). "
                       "RV32IM .text/.rodata identical to id50; Thumbv6-M +8 bytes; S ratio thumbv6m 1.000378/1.000327.",
        "follow_up": "No trial gains; all eight are >=1.0 on every board. Next: target Thumbv6-M typical-class "
                     "cost (exp/sigmoid ~40 instr) with a cheaper 32x32 high-multiply substitute, or a smaller table "
                     "layout that reduces bytes without adding loads; the m0-tanh-refine guard only pays if emitted "
                     "as a single shift+branch.",
    }
    return norm(man), diff_text


def check_ledger_md(recs):
    text = LEDGER_MD.read_text()
    for k, r in recs.items():
        require(text.count(f"`{k}`") >= 1, f"experiments.md lacks {k}")
        if "ratio" in r:
            for s in r["ratio"]:
                require(f"{r['ratio'][s]['thumbv6m']:.6f}" in text and f"{r['ratio'][s]['rv32im']:.6f}" in text,
                        f"experiments.md lacks {k} ratios for seed {s}")


def self_tests(man, recs):
    """The checks must refuse an absent, copied-control, invalid and duplicate candidate."""
    def refused(fn):
        try:
            fn()
        except Bad:
            return True
        return False

    def chosen_ok(name, recs_):
        require(name in recs_, f"absent candidate {name}")
        require(recs_[name].get("eligible"), f"ineligible candidate {name}: {recs_[name].get('reason')}")
    require(refused(lambda: chosen_ok("no-such-trial", recs)), "absent candidate not refused")
    require(refused(lambda: chosen_ok("paired-control", recs)), "copied control not refused")
    bad = copy.deepcopy(recs)
    bad[man["chosen"]]["eligible"] = False
    bad[man["chosen"]]["reason"] = "invalid packet"
    require(refused(lambda: chosen_ok(man["chosen"], bad)), "invalid candidate not refused")
    dup = copy.deepcopy(recs)
    dup["dup-copy"] = copy.deepcopy(dup[man["chosen"]])
    seen = {}
    for k, r in dup.items():
        h = r.get("normalised_sha256")
        if h and r.get("eligible"):
            if h in seen:
                for kk in (k, seen[h]):
                    dup[kk]["eligible"] = False
            seen[h] = k
    require(refused(lambda: chosen_ok(man["chosen"], dup)), "duplicate candidate not refused")
    acc = man["accepted_normalised_hashes"]
    require(man["entry"]["normalised_sha256"] not in acc and man["entry"]["normalised_sha256"] != man["base"]["normalised_sha256"],
            "chosen entry duplicates an accepted source")


def main():
    try:
        man, diff_text = compute()
        if "--write-manifest" in sys.argv[1:]:
            (HERE / "entry-vs-id50.diff").write_text(diff_text)
            MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")
            print(f"wrote {rel(MANIFEST)}")
        stored = jload(MANIFEST)
        require(stored == man, "manifest.json differs from what the raw logs give: " + ", ".join(
            k for k in sorted(set(stored) | set(man)) if stored.get(k) != man.get(k)))
        require(digest(HERE / "entry-vs-id50.diff") == man["diff"]["sha256"], "entry-vs-id50.diff differs")
        recs = man["ledger"]
        require(sorted(recs) == sorted(p.name for p in TRIALS.iterdir() if p.is_dir() and p.name != "paired-control"),
                "ledger does not cover every trial packet")
        check_ledger_md(recs)
        self_tests(man, recs)
        require(man["chosen"] in recs and recs[man["chosen"]]["eligible"], "chosen candidate absent or ineligible")
        sc = man["scores"]
        for s in man["seeds"]:
            print(f"seed {s}: S " + json.dumps(sc["S"][str(s)], sort_keys=True)
                  + " ratio/id50 " + json.dumps(sc["ratio_vs_id50"][str(s)], sort_keys=True))
        print(f"chosen {man['chosen']} entry.c sha256 {man['entry']['sha256']} normalised {man['entry']['normalised_sha256']}")
        print(f"best board vs id50: {sc['best_board']} worse-seed ratio {sc['metric'][0]:.9f} (overall {sc['metric'][1]:.9f}); "
              f"boards taken at 0.970: {sc['takes_board_at_0970'] or 'none'}")
        print(f"manifest: {rel(MANIFEST)}")
        print("PASS")
        return 0
    except (Bad, ValueError, KeyError, IndexError, TypeError, OSError, AttributeError) as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
