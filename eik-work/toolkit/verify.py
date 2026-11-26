#!/usr/bin/env python3
"""Verify the offline toolkit or one baseline evidence packet."""
import argparse
from datetime import datetime
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile

sys.dont_write_bytecode = True
from run import REPO, ROOT, runner
from provision import DEFAULT, stage

BOARDS = {"rv32im", "thumbv6m", "overall"}
TARGETS = {"rv32im", "thumbv6m", "thumbv7em"}
FUNCTIONS = {"sigmoid", "tanh", "exp"}
FORMER = {f"id{i}": i for i in (50, 48, 46, 42, 37)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def is_digest(value):
    return isinstance(value, str) and re.fullmatch("[a-f0-9]{64}", value) is not None


def positive(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def read_json(path):
    return json.loads(path.read_text())


def local(root, relative):
    path = root / relative
    require(path.resolve().is_relative_to(root.resolve()) and path.is_file(),
            f"missing or out-of-scope file {relative}")
    return path


def identity(component):
    """The evaluator's identity hash of one fingerprint component (eik/fingerprint.py: _id)."""
    return sha256(json.dumps(component, sort_keys=True, default=list).encode()).hexdigest()


def same_evaluator(report, manifest):
    """Compare a `fingerprint --details` report with the pinned identities.

    Returns None when both identities are the pinned ones, or the local host compiler line when
    that line is the only difference: every hashed file, constant, flag, target compiler, emulator
    and package version must still be the pinned one. Scores come from the pinned clang and
    emulator on inputs whose digest the manifest pins, so such reports stay comparable; the host
    compiler only builds the reference checker and the hard-input scanner.
    """
    pinned = manifest["fingerprint"]
    require(not report["production_problems"], f"evaluator problems: {report['production_problems']}")
    for field in ("verifier", "measurement"):
        require(identity(pinned["details"][field]) == pinned[field], f"manifest {field} details are inconsistent")
        require(identity(report["details"][field]) == report[field], f"reported {field} details are inconsistent")
    if all(report[f] == pinned[f] for f in ("verifier", "measurement")):
        return None
    local_cc = report["details"]["tools"]["host_cc"]
    require(isinstance(local_cc, str) and local_cc.startswith("gcc "), "host compiler is not GCC")
    for field in ("verifier", "measurement"):
        part = json.loads(json.dumps(report["details"][field]))
        require(part["tools"]["host_cc"] == local_cc, f"inconsistent host compiler in {field}")
        part["tools"]["host_cc"] = pinned["details"][field]["tools"]["host_cc"]
        require(identity(part) == pinned[field], f"{field} fingerprint differs beyond the host compiler line")
    return local_cc


def snapshot(m):
    require(m["schema"] == 1, "unknown manifest schema")
    require(m["kit"]["commit"] == "5a32428ad4aa23bce737d50a738ace24ddeeed2e", "wrong kit pin")
    seeds = m["shared_seeds"]
    require(len(seeds) == 2 and len(set(seeds)) == 2
            and all(type(s) is int and 0 <= s < 2**32 for s in seeds), "invalid shared seeds")
    seed_inputs = m["seed_inputs"]
    require(set(seed_inputs) == {str(seed) for seed in seeds}
            and len({r["sha256"] for r in seed_inputs.values()}) == 2, "incomplete seed input hashes")
    for row in seed_inputs.values():
        require(is_digest(row["sha256"]) and set(row["hard_pool_sizes"]) == FUNCTIONS
                and all(type(n) is int and n > 0 for n in row["hard_pool_sizes"].values()),
                "invalid seed input metadata")
    requests = m["requests"]
    entries = m["entries"]
    require(set(entries) == set(FORMER) | {f"current-{b}" for b in BOARDS}, "invalid source keys")
    for key, request in requests.items():
        dt = datetime.fromisoformat(request["timestamp_utc"])
        require(dt.utcoffset() is not None, f"missing timestamp offset for {key}")
        require(digest(local(ROOT, request["path"])) == request["sha256"], f"response hash mismatch {key}")

    def published(key, endpoint):
        request = requests[key]
        require(request["http_status"] == 200 and request["curl_exit_code"] == 0
                and request["url"] == API + endpoint, f"invalid response for {key}")
        return read_json(ROOT / request["path"])

    API = "https://conjectures.io/v1/competitions/exact-integer-kernels/"
    board_data = published("boards", "boards")
    boards = {b["id"]: b for b in board_data["boards"]}
    require(set(boards) == set(m["board_references"]) == BOARDS, "incomplete board snapshot")
    for b in BOARDS:
        leader = published(f"leaderboard-{b}", f"leaderboard?board={b}")
        ref = m["board_references"][b]
        require(leader["board"] == b and leader["config_hash"] == boards[b]["config_hash"]
                and leader["configuration_hash"] == board_data["configuration_hash"]
                and leader["reference"] == ref and ref["promotion_id"] == boards[b]["current_promotion_id"],
                f"unresolved promotion for {b}")
        entry = entries[f"current-{b}"]
        require((entry["submission"], entry["promotion_id"], entry["sha256"], entry["board"]) ==
                (ref["submission"], ref["promotion_id"], ref["source_sha256"], b), f"wrong reference for {b}")
    for key, entry in entries.items():
        i = entry["submission"]
        if key in FORMER:
            require(i == FORMER[key] and entry["promotion_id"] is None and entry["board"] is None,
                    f"wrong submission for {key}")
        meta = published(f"submission-{i}", f"submissions/{i}")
        require(meta["id"] == i and is_digest(entry["sha256"]) and meta["source_sha256"] == entry["sha256"],
                f"invalid advertised hash for {key}")
        require(entry["hash_provenance"] == requests[f"submission-{i}"]["path"] + "#/source_sha256",
                f"invalid hash provenance for {key}")
        expected_ratios = []
        for j, evaluation in enumerate(meta["evaluations"]):
            decision = evaluation.get("decision") or {}
            ratio = decision.get("score")
            if ratio is not None:
                expected_ratios.append({"board": evaluation["board"], "evaluation_id": evaluation["id"],
                                        "S_ratio": ratio, "reference_promotion_id": evaluation["reference_promotion_id"],
                                        "provenance": f"api/submission-{i}.json#/evaluations/{j}/decision/score"})
            require(not decision.get("suite_scores"), f"unrecorded published suite scores for {key}")
        require(entry["published_ratios"] == expected_ratios and entry["published_S"] == dict.fromkeys(BOARDS),
                f"invalid published score metadata for {key}")
        req = requests[entry["source_request"]]
        require(req["url"] == f"{API}submissions/{i}/source", f"invalid source URL for {key}")
        if entry["status"] == "available":
            require(req["http_status"] == 200 and req["curl_exit_code"] == 0
                    and req["path"] == entry["path"] and req["sha256"] == entry["sha256"],
                    f"source response mismatch for {key}")
        else:
            require(entry["status"] == "unavailable" and entry["path"] is None
                    and (req["curl_exit_code"] != 0 or req["http_status"] != 200),
                    f"unavailable source {key} lacks failure evidence")
    return entries


def bootstrap(m, dependencies, fetch):
    entries = snapshot(m)
    index = read_json(ROOT / "files.json")
    tracked = {str(path.relative_to(ROOT)) for path in ROOT.rglob("*")
               if path.is_file() and path.name != "files.json" and "__pycache__" not in path.parts}
    require(set(index) == tracked, "toolkit inventory differs from files.json")
    for name, expected in sorted(index.items()):
        require(digest(local(ROOT, name)) == expected, f"toolkit hash mismatch for {name}")
    kit = m["kit"]
    require(kit["file_hashes"] == {name: h for name, h in index.items() if name.startswith("kit/")}
            and kit["rules_sha256"] == index["kit/RULES.md"]
            and kit["reference_digest_list_sha256"] == index["kit/reference/digests.sha256"],
            "kit inventory differs from the pinned export")
    deps = read_json(ROOT / m["dependencies_path"])
    wheels = deps["wheels"]
    bundled = [item for item in wheels if item["storage"] == "bundled"]
    require({w["path"] for w in bundled} == {n for n in index if n.endswith(".whl")},
            "wheel inventory differs from dependency manifest")
    for item in bundled:
        path = item["path"]
        require(index[path] == item["sha256"], f"dependency hash mismatch for {path}")
    for line in (ROOT / "kit/reference/digests.sha256").read_text().splitlines():
        expected, name = line.split()
        require(index[f"kit/{name}"] == expected, f"original digest mismatch for {name}")
    stage(dependencies, fetch=fetch)
    for name, item in deps["qemu"]["executables"].items():
        result = subprocess.run([str(dependencies / item["path"]), "--version"], capture_output=True,
                                text=True, env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}, timeout=20)
        require(result.returncode == 0 and result.stdout.splitlines()[:1] == [item["version"]],
                f"staged {name} is unusable or has a different version")
    scratch = REPO / "test/scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="eik-bootstrap-", dir=scratch) as temporary:
        work = Path(temporary)
        code, out, err = runner(work, "bootstrap", "setup", ["setup"], dependencies)
        require(code == 0 and "incumbent registered as champion" in out, f"setup failed ({code}): {err}")
        code, out, err = runner(work, "bootstrap", "fingerprint", ["fingerprint", "--details"], dependencies)
        require(code == 0, f"fingerprint failed ({code}): {err}")
        report = json.loads(out)
        local_cc = same_evaluator(report, m)
    count = sum(e["status"] == "available" for e in entries.values())
    print(f"bootstrap passed: offline setup, pinned fingerprints, {count} verified sources, "
          f"{len(entries) - count} evidenced unavailable sources, both QEMU binaries")
    if local_cc is not None:
        print(f"note: host compiler is '{local_cc}', pinned '{m['fingerprint']['details']['tools']['host_cc']}'; "
              "all other evaluator components match. Baseline packets from this machine must include "
              "a fingerprint log (run.py ... fingerprint fingerprint --details).")


def logs(directory, name, command, source):
    record = read_json(local(directory, f"{name}.json"))
    out = local(directory, f"{name}.stdout")
    err = local(directory, f"{name}.stderr")
    require(record["stdout_sha256"] == digest(out) and record["stderr_sha256"] == digest(err),
            f"{name} log hash mismatch")
    require(record["argv"][1:4] == ["-m", "eik", command] and record["source_sha256"] == source,
            f"{name} used another command or source")
    require(type(record["exit_code"]) is int and positive(record["seconds"]), f"{name} invalid exit or runtime")
    return record, out.read_text()


def fingerprints(report, manifest, directory):
    """Require the pinned identities, or a retained fingerprint log proving only the host GCC line differs."""
    got = report["fingerprint"]
    if all(got[f] == manifest["fingerprint"][f] for f in ("verifier", "measurement")):
        return
    record = read_json(local(directory, "fingerprint.json"))
    out = local(directory, "fingerprint.stdout")
    require(record["stdout_sha256"] == digest(out) and record["exit_code"] == 0
            and record["argv"][1:] == ["-m", "eik", "fingerprint", "--details"], "invalid fingerprint log")
    proof = json.loads(out.read_text())
    require(same_evaluator(proof, manifest) is not None
            and all(got[f] == proof[f] for f in ("verifier", "measurement")),
            "report fingerprint is neither pinned nor explained by the fingerprint log")


def verify_score(report, manifest, static, seed):
    input_row = manifest["seed_inputs"][str(seed)]
    require(report["status"] in {"evaluated", "would-take-over-after-full-check"}
            and report["seed"] == seed and report["inputs_sha256"] == input_row["sha256"],
            "incomplete score report or different seed inputs")
    require(report["normalised_sha256"] and is_digest(report["normalised_sha256"])
            and report["bytes"] == static["bytes"], "score/check source build mismatch")
    hard = report["hard_pool"]
    constants = manifest["fingerprint"]["details"]["measurement"]["constants"]
    require(hard["source"] == "hardscan" and hard["samples"] == constants["hard_samples"]
            and hard["threshold_log2_ulps"] == constants["hard_threshold"]
            and hard["sizes"] == input_row["hard_pool_sizes"],
            "incomplete or altered hard pools")
    measured = report["measurements"]
    scores = report["scores"]
    require(set(measured) == TARGETS and set(scores) == TARGETS | {"overall"}, "incomplete targets")
    for target, data in measured.items():
        require(data["target"] == target and not data.get("timeout") and data["wrong"] == []
                and data["sample"]["mismatches"] == 0
                and data["sample"]["words"] == 3 * constants["target_sample"]
                and set(data["functions"]) == FUNCTIONS, f"incomplete or failed {target} measurement")
        require(0 <= data["stack"] <= 8192, f"invalid stack measurement for {target}")
        fn_logs = []
        factor, scale, exponent = constants["tail"]
        for fn, sets in data["functions"].items():
            require(set(sets) == set(constants["sets"]), f"missing input classes for {target}/{fn}")
            for name, values in sets.items():
                require(values["n"] == constants["set_sizes"][name]
                        and all(positive(values[k]) for k in ("mean", "median", "p999", "max"))
                        and max(values["mean"], values["median"], values["p999"]) <= values["max"]
                        <= constants["cap_instr"], f"invalid counts for {target}/{fn}/{name}")
            base = sum(w * math.log(sets[n]["mean"]) for n, w in constants["sets"].items())
            tail = (1 + max(0.0, sets["hard"]["p999"] - factor * sets["typical"]["mean"]) / scale) ** exponent
            fn_logs.append(base + math.log(tail))
        size_unit, size_exponent = constants["size"]
        require(0 < report["bytes"][target] <= 65536, f"invalid code size for {target}")
        expected = math.exp(sum(fn_logs) / len(fn_logs)) * (1 + report["bytes"][target] / size_unit) ** size_exponent
        measured_score = scores[target]["S"]
        require(positive(measured_score) and math.isclose(measured_score, expected, rel_tol=1e-12),
                f"invalid S for {target}")
    overall = scores["overall"]["S"]
    require(positive(overall) and math.isclose(overall, math.sqrt(scores["rv32im"]["S"] * scores["thumbv6m"]["S"]),
                                               rel_tol=1e-12), "invalid overall S")
    host = report.get("host_check")
    if report["status"] == "would-take-over-after-full-check":
        require(host is not None, "missing quick host check for takeover candidate")
    if host is not None:
        require(host["ok"] is True and host["quick"] is True and host["complete"] is False
                and set(host["functions"]) == FUNCTIONS, "missing quick host checks")
        for fn, check in host["functions"].items():
            require(check["verdict"] == "passed" and check["mismatches"] == 0
                    and check["words_checked"] == 128 * (1 << 20) and check["complete"] is False
                    and not check.get("sanitizer"), f"incomplete quick host check for {fn}")


def baseline(m, directory):
    packet = read_json(local(directory, "packet.json"))
    entry_key = packet["source"]
    expected_key = f"id{directory.name.removeprefix('former-')}" if directory.name.startswith("former-") else directory.name
    if expected_key in m["entries"]:
        require(entry_key == expected_key, "packet is for a different baseline target")
    entry = m["entries"][entry_key]
    require(packet["sha256"] == entry["sha256"], "packet source hash differs from manifest")
    status = packet["status"]
    if status == "unavailable":
        req = m["requests"][entry["source_request"]]
        require(entry["status"] == status and packet["source_request"] == entry["source_request"],
                "no matching HTTP failure in manifest")
        print(f"{entry_key}: unavailable (HTTP {req['http_status']}, curl {req['curl_exit_code']})")
        return
    require(entry["status"] == "available", "source bytes are unavailable")
    check, out = logs(directory, "check", "check", entry["sha256"])
    if status == "gate-rejected":
        gate, gate_out = logs(directory, "gate", "gate", entry["sha256"])
        rep = json.loads(gate_out)
        fingerprints(rep, m, directory)
        require(gate["exit_code"] == 1 and rep["kind"] == "gate" and rep["schema"] == "eik-report-1"
                and rep["verdict"] == "rejected" and rep["stage"] and rep["reasons"]
                and rep["sha256"] == entry["sha256"], "invalid gate rejection evidence")
        require((check["exit_code"] == 1 and out.startswith(f"REJECT [{rep['stage']}]"))
                or (check["exit_code"] == 0 and out.startswith("PASS ") and rep["stage"] == "build"),
                "static check is inconsistent with gate rejection")
        print(f"{entry_key}: gate-rejected ({rep['stage']})")
        return
    require(status == "measured" and check["exit_code"] == 0 and out.startswith("PASS "),
            "expected completed measurement with passing check")
    static = json.loads(out.removeprefix("PASS "))
    rows = {}
    for seed in m["shared_seeds"]:
        execution, score_out = logs(directory, f"evaluate-{seed}", "evaluate", entry["sha256"])
        args = execution["argv"][5:]
        require(execution["exit_code"] == 0 and "--quick" in args and "--json" in args
                and args.count("--seed") == 1 and args[args.index("--seed") + 1] == str(seed),
                f"missing or unsuccessful required evaluation for seed {seed}")
        rep = json.loads(score_out)
        require(rep["sha256"] == entry["sha256"], "score source hash differs")
        fingerprints(rep, m, directory)
        verify_score(rep, m, static, seed)
        rows[str(seed)] = {b: rep["scores"][b]["S"] for b in sorted(BOARDS)}
    require(packet["scores"] == rows, "packet score rows differ")
    require(isinstance(packet["techniques"], str) and packet["techniques"].strip(), "missing techniques note")
    print(f"{entry_key}: measured {json.dumps(rows, sort_keys=True)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="mode", required=True)
    bundle = subparsers.add_parser("bootstrap")
    bundle.add_argument("--offline", action="store_true", help="require an already staged dependency cache")
    bundle.add_argument("--dependencies", type=Path, default=DEFAULT)
    subparsers.add_parser("baseline").add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        manifest = read_json(ROOT / "manifest.json")
        if args.mode == "bootstrap":
            bootstrap(manifest, args.dependencies.resolve(), fetch=not args.offline)
        else:
            directory = args.directory.resolve()
            snapshot(manifest)
            baseline(manifest, directory)
    except (ValueError, OSError, KeyError, IndexError, TypeError, RuntimeError,
            subprocess.SubprocessError, tarfile.TarError) as exc:
        print(f"{args.mode} failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
