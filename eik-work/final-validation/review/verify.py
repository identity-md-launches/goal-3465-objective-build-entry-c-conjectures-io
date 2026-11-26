#!/usr/bin/env python3
"""Verify the source review from retained bytes, using only the standard library."""
import ast
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TRIALS = ROOT / "eik-work/trials"
LOGS = HERE / "logs"
SOURCE = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
NORMAL = "adf3a5a8074ffcca8e58ea852f58143a20a00aa6a74df8f14c1b742fa21a03c8"
INVENTORY = "f7aa26a8952910df85b0d71994cd2d8274a21085596bf488fb85a2c0c02b33c2"
KEYS = ("m0-exp-layout", "m0-exp-reduction", "m0-sigmoid-cell", "m0-tanh-refine",
        "rv-exp-interval", "rv-exp-loads", "rv-tanh-quadratic", "shared-small-sigmoid")
CHOSEN = "m0-tanh-refine"
SEEDS = (1874435642, 1947282751)
TARGETS = ("rv32im", "thumbv6m", "thumbv7em")
BOARDS = ("rv32im", "thumbv6m", "overall")
FUNCTIONS = ("sigmoid", "tanh", "exp")
CLASSES = {"typical": (2000, .55), "wide": (1000, .30), "hard": (300, .10),
           "uniform": (1000, .05)}
CHAMPIONS = {"rv32im": 52, "thumbv6m": 53, "overall": 56}
SUBMISSIONS = (37, 42, 46, 48, 50)
SHARED = TRIALS / "shared-small-sigmoid"
SHARED_CHUNKS = (0, 823, 824, 952, 959, 960, 2048, 2871, 2872, 3000, 3007, 3008)
GAPS = {
    "runtime_export": "Three pinned payloads absent from the committed export. Fresh runs used exact scratch-restored files.",
    "champions": "Same-input live ratios and duplicate checks against private sources are unavailable.",
    "shared_packet": "Freeze only indexed packet runs. The 36 external --out reports lack a historical output-report hash and have 12 different image hashes per target.",
    "host_path": "The GCC exhaustive run exercises the signed wide-character selector arm. Thumb correctness depends on target evidence.",
    "portability": "Inherited table subobject byte-offset and struct-view idioms need a strict C11 review. The pinned runs establish empirical behavior.",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def path_evidence(path):
    return {"path": rel(path), "sha256": digest(path)}


def stem_file(stem, suffix):
    return stem.with_name(stem.name + "." + suffix)


def run_record(stem, operation, source, *, exact_path=True, exit_code=0):
    record = read(stem_file(stem, "json"))
    args = record["argv"]
    require(args[1:4] == ["-m", "eik", operation] and record["exit_code"] == exit_code,
            f"{stem}: command/exit mismatch")
    if source is not None:
        require(record["source_sha256"] == digest(source), f"{stem}: source mismatch")
        if exact_path:
            require(args[4] == "$REPO/" + rel(source), f"{stem}: unexpected source path")
    for channel in ("stdout", "stderr"):
        require(record[f"{channel}_sha256"] == digest(stem_file(stem, channel)),
                f"{stem}: {channel} mismatch")
    return record


def report_at(stem):
    return read(stem_file(stem, "stdout"))


def close(got, want, label):
    require(math.isfinite(got) and math.isclose(got, want, rel_tol=1e-12), label)


def measurement(report, seed, source, static, fp, staged):
    require(report["seed"] == seed and report["sha256"] == digest(source)
            and report["fingerprint"] == fp and report["bytes"] == static["bytes"],
            f"{source}: scoring provenance")
    if staged:
        require(report["kind"] == "measure" and report["verdict"] == "passed" and report["sampled"],
                f"{source}: measure verdict")
    pool = report["hard_pool"]
    require((pool["source"], pool["samples"], pool["threshold_log2_ulps"]) == ("hardscan", 67108864, -18)
            and set(pool["sizes"]) == set(FUNCTIONS), f"{source}: hard population")
    data = report["targets" if staged else "measurements"]
    require(set(data) == set(TARGETS), f"{source}: targets")
    scores, counts = {}, {}
    for target in TARGETS:
        m = data[target]
        size = static["bytes"][target]
        require(m["target"] == target and m["wrong"] == [] and not m.get("timeout")
                and m["sample"]["mismatches"] == 0 and m["sample"]["words"] == 98304
                and 0 < size <= 65536 and 0 <= m["stack"] <= static["stack_bound"][target] <= 8192,
                f"{source}: measurement gate {target}")
        require(set(m["functions"]) == set(FUNCTIONS), f"{source}: functions")
        factors = []
        logged = report["scores"][target]
        for fn in FUNCTIONS:
            sets = m["functions"][fn]
            require(set(sets) == set(CLASSES), f"{source}: population")
            for name, (n, _) in CLASSES.items():
                c = sets[name]
                require(c["n"] == n and 0 < c["mean"] <= c["max"] <= 20000000
                        and 0 < c["p999"] <= c["max"], f"{source}: invalid count")
            typical, hard = sets["typical"], sets["hard"]
            tail = (1 + max(0, hard["p999"] - 20 * typical["mean"]) / 1000000) ** .1
            weighted = math.prod(sets[name]["mean"] ** w for name, (_, w) in CLASSES.items())
            close(logged["functions"][fn]["tail_factor"], tail, "tail formula")
            close(logged["functions"][fn]["geo_mean_instr"], weighted, "weighted formula")
            factors.append(weighted * tail)
        size_factor = math.sqrt(1 + size / 65536)
        close(logged["size_factor"], size_factor, "size formula")
        close(logged["S"], math.prod(factors) ** (1 / 3) * size_factor, "target S formula")
        scores[target] = logged["S"]  # canonical precision, verified independently above
        counts[target] = {"scored_outputs": sum(n for n, _ in CLASSES.values()) * len(FUNCTIONS),
                          "target_sample_words": m["sample"]["words"], "wrong_outputs": 0,
                          "sample_mismatches": 0, "image_bytes": size, "peak_stack": m["stack"],
                          "static_stack_bound": static["stack_bound"][target]}
    overall = report["scores"]["overall"]["S"]
    close(overall, math.sqrt(scores["rv32im"] * scores["thumbv6m"]), "overall formula")
    scores["overall"] = overall
    return {"seed": seed, "S": scores, "inputs_sha256": report["inputs_sha256"],
            "hard_pool": pool, "target_measurements": counts}


def packet_rows(folder, fp, expected):
    packet = read(folder / "packet.json")
    src = ROOT / packet["source"]["path"]
    require(packet["target"] == folder.name and packet["status"] == "measured"
            and digest(src) == packet["source"]["sha256"] == expected["sha256"],
            f"{folder}: packet source/status")
    for label, claim in packet["runs"].items():
        require(claim["files"] == {f"{label}.{suffix}": digest(folder / f"{label}.{suffix}")
                                   for suffix in ("json", "stdout", "stderr")}
                and read(folder / f"{label}.json")["exit_code"] == claim["exit_code"],
                f"{folder}/{label}: packet run")
    check = folder / "check"
    run_record(check, "check", src)
    static = json.loads(stem_file(check, "stdout").read_text().removeprefix("PASS "))
    run_record(folder / "gate", "gate", src)
    gate = report_at(folder / "gate")
    require(gate["verdict"] == "accepted" and gate["fingerprint"] == fp
            and gate["sha256"] == digest(src) and gate["source_bytes"] == src.stat().st_size <= 262144
            and gate["normalised_sha256"] == expected["normalised_sha256"]
            and gate["bytes"] == static["bytes"] and gate["stack_bound"] == static["stack_bound"],
            f"{folder}: gate evidence")
    rows = {}
    for seed in SEEDS:
        staged = f"evaluate-{seed}" not in packet["runs"]
        operation = "measure" if staged else "evaluate"
        stem = folder / f"{operation}-{seed}"
        args = run_record(stem, operation, src)["argv"][5:]
        report = report_at(stem)
        if staged:
            require(args == ["--seed", str(seed)], f"{stem}: measure flags")
            hosts = {}
            for fn in FUNCTIONS:
                h = folder / f"fullcheck-{seed}-{fn}"
                h_args = run_record(h, "fullcheck", src)["argv"][5:]
                require(h_args == ["--function", fn, "--quick", "--seed", str(seed)],
                        f"{h}: quick flags")
                hosts[fn] = report_at(h)
        else:
            require(len(args) == 4 and set(args) == {"--seed", str(seed), "--json", "--quick"}
                    and args[args.index("--seed") + 1] == str(seed), f"{stem}: evaluate flags")
            require(report["normalised_sha256"] == expected["normalised_sha256"]
                    and report["host_check"]["ok"] and report["host_check"]["quick"],
                    f"{stem}: evaluate identity")
            hosts = report["host_check"]["functions"]
        for fn in FUNCTIONS:
            host = hosts[fn]
            require(host["verdict"] == "passed" and host["complete"] is False
                    and host["words_checked"] == 128 << 20 and not host["mismatches"],
                    f"{stem}: quick host {fn}")
            if staged:
                require(host["sha256"] == digest(src) and host["function"] == fn and host["quick"]
                        and host["fingerprint"] == fp, f"{stem}: quick host source/flags {fn}")
        row = measurement(report, seed, src, static, fp, staged)
        row["quick_host_words_per_function"] = 128 << 20
        row["score_log"] = rel(stem_file(stem, "stdout"))
        rows[str(seed)] = row
    return packet, rows


def coverage(stem, source, fp, out=None):
    args = read(stem_file(stem, "json"))["argv"]
    command = args[3]
    require(command in ("targetcheck", "fullcheck"), f"{stem}: unexpected operation")
    record = run_record(stem, command, source)
    report_path = out or stem_file(stem, "stdout")
    if out:
        require("--out" in args and Path(args[args.index("--out") + 1]).name == out.name
                and not stem_file(stem, "stdout").stat().st_size, f"{stem}: --out provenance")
    report = read(report_path)
    lo, hi = report["chunk_lo"], report["chunk_hi"]
    require(report["kind"] == command and report["verdict"] == "passed"
            and report["sha256"] == digest(source) and report["fingerprint"] == fp
            and not report["mismatches"] and report["range_complete"]
            and report["function"] in FUNCTIONS and args[args.index("--function") + 1] == report["function"]
            and 0 <= lo < hi <= 4096 and report["words_checked"] == (hi - lo) << 20
            and report["complete"] == ((lo, hi) == (0, 4096)), f"{stem}: coverage inconsistent")
    if "--chunks" in args:
        require(args[args.index("--chunks") + 1] == f"{lo}:{hi}", f"{stem}: shard span")
    else:
        require((lo, hi) == (0, 4096), f"{stem}: expected full span")
    if command == "targetcheck":
        require(report["target"] in TARGETS and report["target"] == args[args.index("--target") + 1]
                and re.fullmatch("[0-9a-f]{64}", report["image_sha256"]), f"{stem}: target/image")
    else:
        require(not report["quick"] and not report.get("sanitizer") and report["exit"] == 0,
                f"{stem}: sanitizer exit")
    keys = ("kind", "function", "target", "chunk_lo", "chunk_hi", "complete", "words_checked",
            "mismatches", "image_sha256")
    return {"report": path_evidence(report_path), "run": rel(stem_file(stem, "json")),
            "exit_code": record["exit_code"], **{k: report[k] for k in keys if k in report}}


def packet_target_reports(folder, packet, fp):
    source = ROOT / packet["source"]["path"]
    reports = []
    for label in sorted(packet["runs"]):
        stem = folder / label
        args = read(stem_file(stem, "json"))["argv"]
        if args[3] != "targetcheck":
            continue
        out = None
        if "--out" in args and not stem_file(stem, "stdout").stat().st_size:
            out = folder / "targetcheck-reports" / Path(args[args.index("--out") + 1]).name
        reports.append(coverage(stem, source, fp, out))
    return reports


def shared_supplement(fp):
    src = SHARED / "entry.c"
    runs, out = SHARED / "evidence/runlogs", SHARED / "evidence"
    target_reports, image_counts = [], {}
    for target in TARGETS:
        images = set()
        for chunk in SHARED_CHUNKS:
            shard = coverage(runs / f"tc-{target}-{chunk}", src, fp,
                             out / f"targetcheck/{target}-sigmoid-{chunk}.json")
            require((shard["chunk_lo"], shard["chunk_hi"], shard["function"]) ==
                    (chunk, chunk + 1, "sigmoid"), "unexpected shared shard")
            images.add(shard["image_sha256"])
            target_reports.append(shard)
        image_counts[target] = len(images)
    require(len(list(runs.glob("tc-*.json"))) == len(list((out / "targetcheck").glob("*.json"))) == 36,
            "wrong shared shard inventory")
    hosts = [coverage(runs / f"full-host-{fn}", src, fp, out / f"hostfull/host-{fn}-full.json")
             for fn in FUNCTIONS]
    return {"target_shards": target_reports, "full_host": hosts, "sigmoid_words_per_target": 12 << 20,
            "distinct_reported_image_hashes": image_counts}


def variants(fp, control):
    out = {}
    for version in ("v2", "v3"):
        folder = SHARED / f"evidence/experiments/{version}"
        src = folder / "entry.c.txt"
        run_record(folder / "check", "check", src, exact_path=False)
        static = json.loads((folder / "check.stdout").read_text().removeprefix("PASS "))
        seed = SEEDS[0]
        stem = folder / f"measure-{seed}"
        args = run_record(stem, "measure", src, exact_path=False)["argv"][5:]
        require(args == ["--seed", str(seed)], f"{version}: altered flags")
        row = measurement(report_at(stem), seed, src, static, fp, True)
        require(row["inputs_sha256"] == control["inputs_sha256"] and row["hard_pool"] == control["hard_pool"],
                f"{version}: unpaired populations")
        row.update(source=path_evidence(src), score_log=rel(stem_file(stem, "stdout")),
                   verdict="measure-only regression", ratio_vs_id50=ratios(row, control),
                   scope="single seed, measured target sample, no retained quick host or targetcheck packet",
                   change={"v2": "Affine guard for biased exponents 90–114, F nonzero, no table",
                           "v3": "Narrow v2 to biased exponents 103–114"}[version])
        out[version] = row
    return out


def ratios(row, control):
    return {b: score / control["S"][b] for b, score in row["S"].items()}


def target_rank(rows):
    return sorted(rows, key=lambda key: (*rows[key]["selection_metric"], key))


def ledger(freeze, probe):
    fp = freeze["evaluator"]
    norms = probe["normalised"]
    directory = TRIALS / "paired-control"
    packet, control = packet_rows(directory, fp, norms["id50"])
    require(packet["source"]["path"] == freeze["base"]["path"], "wrong paired control")
    accepted = {norms[f"id{i}"]["normalised_sha256"] for i in SUBMISSIONS}
    require(len(accepted) == len(SUBMISSIONS) and accepted == set(freeze["accepted_normalised_hashes"]),
            "accepted hash coverage differs")
    require({d.name for d in TRIALS.iterdir() if d.is_dir()} == {*KEYS, "paired-control"},
            "trial packet inventory differs")
    rows = {}
    seen = set(accepted)
    for key in KEYS:
        folder = TRIALS / key
        packet, paired = packet_rows(folder, fp, norms[key])
        normal = norms[key]["normalised_sha256"]
        require(normal not in seen, f"{key}: normalised duplicate")
        seen.add(normal)
        for seed, row in paired.items():
            require(row["inputs_sha256"] == control[seed]["inputs_sha256"]
                    and row["hard_pool"] == control[seed]["hard_pool"], f"{key}: unpaired seeds")
            row["ratio_vs_id50"] = ratios(row, control[seed])
            for board in BOARDS:
                close(row["ratio_vs_id50"][board], freeze["ledger"][key]["ratio"][seed][board],
                      f"{key}: freeze ratio {board}")
        worst = {b: max(r["ratio_vs_id50"][b] for r in paired.values()) for b in BOARDS}
        reports = packet_target_reports(folder, packet, fp)
        eligible = bool(reports)
        require(eligible == freeze["ledger"][key]["eligible"] == (key != SHARED.name),
                f"{key}: historical eligibility")
        require(all(v >= 1 for r in paired.values() for v in (r["ratio_vs_id50"][b] for b in BOARDS)),
                f"{key}: unexpected board gain")
        rows[key] = {"packet": path_evidence(folder / "packet.json"), "source": norms[key],
                     "change": packet["note"], "rows": paired, "packet_target_reports": reports,
                     "worst_ratio_vs_id50": worst, "selection_metric": [min(worst.values()), worst["overall"]],
                     "original_eligible": eligible,
                     "original_disposition": ("selected fallback" if key == CHOSEN else
                                              "eligible loss" if eligible else
                                              "rejected: no packet-indexed targetcheck")}
    original_order = target_rank({k: r for k, r in rows.items() if r["original_eligible"]})
    corrected_order = target_rank(rows)
    require(original_order == freeze["selection"]["order"] and freeze["chosen"] == CHOSEN
            and original_order[0] == corrected_order[0] == CHOSEN and corrected_order[-1] == SHARED.name,
            "frozen selection changed")
    attempts = [
        TRIALS / "paired-control/evaluate-attempts.json",
        TRIALS / "rv-exp-loads/incumbent-evaluate-attempts.json",
        *(TRIALS / f"rv-exp-interval/evaluate-attempt-{seed}.attempt.json" for seed in SEEDS),
    ]
    return {"control": {"packet": path_evidence(directory / "packet.json"), "source": norms["id50"],
                        "rows": control},
            "trials": rows, "original_rank": original_order, "rank_with_shared_target_evidence": corrected_order,
            "combination": None, "boards_at_0_970_vs_id50": [],
            "shared_small_sigmoid_supplement": shared_supplement(fp),
            "additional_measured_variants": variants(fp, control[str(SEEDS[0])]),
            "recorded_evaluate_attempts_without_scores": [
                {"evidence": path_evidence(p), "records": read(p)} for p in attempts]}


def verify_inventory():
    path = HERE / "evidence-sha256.json"
    require(digest(path) == INVENTORY, "evidence inventory hash differs")
    files = read(path)
    require("entry.c" in files and "eik-work/freeze/manifest.json" in files, "missing key inputs")
    for name, expected in files.items():
        path = ROOT / name
        require(path.is_relative_to(ROOT) and path.resolve() == path and path.is_file()
                and digest(path) == expected, f"missing, non-ordinary or changed evidence: {name}")
    return files


def proof_and_guard(fp):
    chosen = TRIALS / CHOSEN
    path = chosen / "prove-bound.py"
    process = subprocess.run([sys.executable, "-I", str(path)], capture_output=True, check=True)
    proof_log = LOGS / "prove-bound.stdout"
    require(not process.stderr and process.stdout == proof_log.read_bytes()
            == (chosen / "prove-bound.stdout").read_bytes(), "rounding certificate replay differs")
    lines = proof_log.read_text().splitlines()
    residual = [int(n) for n in re.findall(r"-\d+", lines[0].split("in units")[0])]
    bins = ast.literal_eval(lines[4].split(": ", 1)[1])
    require(residual == [-250889, -33522] and sum(bins.values()) == 5632
            and set(bins) == set(range(952, 959)), "unexpected certificate bounds")
    guard = []
    historical = []
    for target in TARGETS[1:]:
        for sign, start in [("pos", 952), ("neg", 3000)]:
            suffix = "positive" if sign == "pos" else "negative"
            label = f"targetcheck-{'thumbv7em-' if target == 'thumbv7em' else ''}{suffix}"
            old = coverage(chosen / label, chosen / "entry.c", fp)
            evidence = coverage(LOGS / f"guard-{target}-{sign}", ROOT / "entry.c", fp)
            for row in [old, evidence]:
                require((row["target"], row["function"], row["chunk_lo"], row["chunk_hi"])
                        == (target, "tanh", start, start + 8), "guard boundary coverage differs")
            guard.append(evidence)
            historical.append(old)
    return {"certificate": path_evidence(path), "residual_q54": residual, "domain_words_per_sign": 8388352,
            "first_cell_bypasses_guard": 32768, "new_fast_per_sign": sum(bins.values()),
            "changed_positive_chunks": {str(k): v for k, v in bins.items()},
            "negative_chunk_offset": 2048, "old_cutoff": 262144, "new_cutoff": 253952,
            "lower_margin_q54": 253952 + residual[0], "upper_margin_q54": 1 - residual[1],
            "retained_refinements_per_sign": 260608, "fresh_thumb_checks": guard,
            "historical_guard_checks": historical}


def original_full(fp):
    folder = TRIALS / CHOSEN
    src = folder / "entry.c"
    hosts = [coverage(folder / f"exhaustive-{fn}", src, fp) for fn in FUNCTIONS]
    targets = []
    for target in TARGETS:
        for fn in FUNCTIONS:
            label = f"targetcheck-{target}-all" if target != "rv32im" and fn == "tanh" else (
                f"targetcheck-{target}-{fn}-all")
            row = coverage(folder / label, src, fp)
            require(row["target"] == target and row["function"] == fn, f"{label}: wrong matrix cell")
            targets.append(row)
    require(all(r["complete"] and r["words_checked"] == 1 << 32 for r in hosts + targets)
            and {h["function"] for h in hosts} == set(FUNCTIONS), "missing historical full coverage")
    run_record(folder / "exhaustive-merged", "merge", None)
    merged = report_at(folder / "exhaustive-merged")
    full = {fn: {"chunks_covered": 4096, "words_checked": 1 << 32} for fn in FUNCTIONS}
    require(merged["verdict"] == "passed" and merged["sha256"] == SOURCE and merged["fingerprint"] == fp
            and merged["functions"] == full and merged["targets"] == {t: full for t in TARGETS},
            "historical merged coverage differs")
    return {"host": hosts, "target": targets, "merged": path_evidence(folder / "exhaustive-merged.stdout")}


def validate_probe(probe, freeze):
    norms = probe["normalised"]
    require(set(norms) == {"entry.c", *KEYS, *(f"id{i}" for i in SUBMISSIONS)}, "normalisation scope")
    for item in norms.values():
        require(digest(ROOT / item["path"]) == item["sha256"], "normalised source bytes differ")
    for i in SUBMISSIONS:
        record = read(ROOT / f"eik-work/toolkit/api/submission-{i}.json")
        require(record["id"] == i and record["source_sha256"] == norms[f"id{i}"]["sha256"],
                f"id{i}: published source provenance")
    require(norms["entry.c"] == {"path": "entry.c", "sha256": SOURCE, "normalised_sha256": NORMAL}
            and norms[CHOSEN]["sha256"] == SOURCE and norms[CHOSEN]["normalised_sha256"] == NORMAL,
            "frozen source differs")
    base = ROOT / freeze["base"]["path"]
    old = b"if (((t_z << 9) >> 27) != 0u)"
    new = b"if (((t_z << 9) >> 22) >= 31u)"
    require(digest(base) == norms["id50"]["sha256"] == freeze["base"]["sha256"]
            and base.read_bytes().count(old) == 1
            and base.read_bytes().replace(old, new) == (ROOT / "entry.c").read_bytes(),
            "frozen C has changes beyond the cutoff")
    require(probe["selector"] == {"host": 1, "rv32im": 1, "thumbv6m": 0, "thumbv7em": 0},
            "unsubstantiated selector facts")
    words = probe["words"]
    require(words[:4] == [0, 0x80000000, 0x7f800000, 0xff800000] and len(words) == 16,
            "special inputs missing")
    for fn, first in {"sigmoid": [0x3f000000, 0x3f000000, 0x3f800000, 0],
                      "tanh": [0, 0x80000000, 0x3f800000, 0xbf800000],
                      "exp": [0x3f800000, 0x3f800000, 0x7f800000, 0]}.items():
        require(probe["expected"][fn][:10] == first + [i | 0x00400000 for i in words[4:10]],
                f"{fn}: special values")
    require(probe["expected"]["exp"][10:] == [0x7f7fff84, 0x7f800000, 0x800026, 0x7fffe6, 1, 0],
            "exp threshold values")
    require(set(probe["targets"]) == set(TARGETS), "incomplete target probes")
    for target, output in probe["targets"].items():
        require(output["outputs"] == probe["expected"]
                and output["same_text_and_rodata_as_id50"] == (target == "rv32im"),
                f"{target}: supplemental probe result")


def elf_facts(path, record, target, check_exports):
    image = path.read_bytes()
    require(image[:6] == b"\x7fELF\x01\x01", f"{path}: not little-endian ELF32")
    machine, = struct.unpack_from("<H", image, 18)
    require(machine == (243 if target == "rv32im" else 40), f"{path}: unexpected ISA")
    off, = struct.unpack_from("<I", image, 32)
    width, count, names_idx = struct.unpack_from("<HHH", image, 46)
    require(width == 40, f"{path}: unexpected section headers")
    sections = [struct.unpack_from("<10I", image, off + width * i) for i in range(count)]

    def data(section):
        return image[section[4]:section[4] + section[5]]

    def name(table, i):
        return table[i:table.index(b"\0", i)].decode("ascii")

    names = data(sections[names_idx])
    require(all(section[5] == 0 or section[2] & 3 != 3 for section in sections),
            f"{path}: writable allocated storage")
    allocated = {name(names, sec[0]): {"sha256": hashlib.sha256(data(sec)).hexdigest(), "size": sec[5]}
                 for sec in sections if sec[2] & 2 and sec[1] != 8}
    require(allocated == record["sections"] and digest(path) == record["sha256"],
            f"{path}: allocated section bytes differ")
    defined, undefined = set(), set()
    if check_exports:
        table, = [sec for sec in sections if sec[1] == 2]
        sym_names = data(sections[table[6]])
        for sym, _, _, info, _, index in struct.iter_unpack("<IIIBBH", data(table)):
            if sym and info >> 4 in (1, 2):
                (defined if index else undefined).add(name(sym_names, sym))
        require(defined == {"eik_" + fn for fn in FUNCTIONS}
                and undefined == ({"__udivdi3"} if target == "rv32im" else set()),
                f"{path}: unexpected exports or dependencies")
    return {"machine": machine, "writable_allocated_bytes": 0,
            "exports": sorted(defined), "undefined": sorted(undefined)}


def audit():
    freeze_path = ROOT / "eik-work/freeze/manifest.json"
    toolkit_path = ROOT / "eik-work/toolkit/manifest.json"
    offline_path = ROOT / "eik-work/offline-runtime/manifest.json"
    freeze, toolkit, offline = (read(p) for p in (freeze_path, toolkit_path, offline_path))
    fp = freeze["evaluator"]
    entry = ROOT / "entry.c"
    require(digest(entry) == freeze["entry"]["sha256"] == SOURCE and entry.stat().st_size == 166756,
            "frozen entry byte identity")
    require(fp == {k: toolkit["fingerprint"][k] for k in fp}, "evaluator identity differs")
    for name, expected in toolkit["kit"]["file_hashes"].items():
        require(digest(toolkit_path.parent / name) == expected, f"kit file differs: {name}")
    commands = read(LOGS / "commands.json")
    fresh_cases = {f"guard-{t}-{sign}" for t in TARGETS[1:] for sign in ("pos", "neg")}
    require(set(commands) == {"network", "isolated-bootstrap", "setup", "check", "gate",
                              "fingerprint", "probe", *fresh_cases}, "fresh command inventory")
    for label, command in commands.items():
        require(command["argv"][:3] == ["unshare", "-Urn", "--"] and command["exit_code"] == 0,
                f"{label}: isolation or command failure")
    lines = (LOGS / "network.stdout").read_text().splitlines()[2:]
    require([line.split(":")[0].strip() for line in lines] == ["lo"], "network namespace interfaces")
    for label, action, source in [
        ("setup", "setup", None), ("check", "check", entry), ("gate", "gate", entry),
        ("fingerprint", "fingerprint", None),
    ]:
        run_record(LOGS / label, action, source)
    check_text = (LOGS / "check.stdout").read_text()
    require(check_text.startswith("PASS "), "fresh check failed")
    check = json.loads(check_text.removeprefix("PASS "))
    gate = report_at(LOGS / "gate")
    require(check == freeze["static"] and gate["verdict"] == "accepted" and gate["stage"] is None
            and gate["sha256"] == SOURCE and gate["normalised_sha256"] == NORMAL
            and gate["fingerprint"] == fp and gate["source_bytes"] == entry.stat().st_size,
            "fresh gate differs")
    for target in TARGETS:
        require(check["bytes"][target] == gate["bytes"][target] <= 65536
                and check["stack_bound"][target] == gate["stack_bound"][target] <= 8192,
                f"{target}: fresh size/stack")
    fingerprint = report_at(LOGS / "fingerprint")
    require(not fingerprint["production_problems"] and all(fingerprint[k] == v for k, v in fp.items()),
            "fresh fingerprint differs")
    objects = {
        t: {kind: elf_facts(ROOT / record["path"], record, t, kind == "object")
            for kind, record in freeze["objects"][t].items()}
        for t in TARGETS
    }
    require((LOGS / "platform.stdout").read_text().strip() == "Linux x86_64"
            and (LOGS / "python.stdout").read_text().startswith("Python 3.12.")
            and (LOGS / "gcc.stdout").read_text().startswith("gcc "), "wrong host tool profile")
    require("Prepared 33 pinned files" in (LOGS / "prepare.stdout").read_text()
            and "bootstrap passed: offline setup" in (LOGS / "isolated-bootstrap.stdout").read_text()
            and "Export replay status: incomplete" in (LOGS / "runtime-export.stdout").read_text()
            and (LOGS / "freeze.stdout").read_text().rstrip().endswith("PASS"),
            "local supporting check output differs")
    restored = read(LOGS / "restored-payloads.json")
    require(set(restored) == set(offline["omitted"]), "scratch restoration manifest incomplete")
    for name, evidence in restored.items():
        pin = offline["files"][name]
        require(evidence == {"sha256": pin["sha256"], "bytes": pin["bytes"], "url": pin["provenance"]},
                f"{name}: scratch restoration provenance")
    probe = report_at(LOGS / "probe")
    validate_probe(probe, freeze)
    guard = proof_and_guard(fp)
    scores = ledger(freeze, probe)
    live_path = TRIALS / CHOSEN / "live-sources.json"
    live = read(live_path)
    for board, submission in CHAMPIONS.items():
        require(live[board]["submission"] == submission and live[board]["http_status"] == 403
                and live[board]["response"]["reason_code"] == "SOURCE_WITHHELD"
                and live[board]["trial_champion_ratio"] is None
                and live[board]["same_seed_champion_S"] is None, f"{board}: private source claim")
    result = {
        "schema": "eik-source-review-1", "status": "incomplete",
        "review_verdict": "verified negative fallback",
        "reviewed_commit": "dacbfa31d0b52d8536e93daa962b32855225106d",
        "source": {**probe["normalised"]["entry.c"], "bytes": entry.stat().st_size},
        "available_accepted_sources": {f"id{i}": probe["normalised"][f"id{i}"] for i in SUBMISSIONS},
        "normalised_source_novelty_scope": "Distinct from the five available accepted sources",
        "tools": {"platform": (LOGS / "platform.stdout").read_text().strip(),
                  "python": (LOGS / "python.stdout").read_text().strip(),
                  "gcc": (LOGS / "gcc.stdout").read_text().splitlines()[0],
                  "kit": toolkit["kit"]["commit"], "evaluator": fp,
                  "tool_versions": fingerprint["details"]["measurement"]["tools"],
                  "measurement_constants": fingerprint["details"]["measurement"]["constants"]},
        "artifacts": {p.name: path_evidence(p) for p in
                      (freeze_path, toolkit_path, offline_path, live_path, HERE / "review.md",
                       HERE / "ledger.json", HERE / "probe.py", HERE / "restore-payload.py",
                       LOGS / "restored-payloads.json", HERE / "evidence-sha256.json")
                      if p.name != "manifest.json"},
        "manifests": {p.parent.name: path_evidence(p) for p in (freeze_path, toolkit_path, offline_path)},
        "commands": commands,
        "additional_local_commands": {
            "bootstrap": {"argv": ["python3", "eik-work/toolkit/verify.py", "bootstrap", "--offline",
                                   "--dependencies", "test/scratch/source-review/deps"], "exit_code": 0},
            "recover_payloads": {"argv": ["python3", "test/scratch/source-review/restore_payload.py"],
                                 "retained_script": rel(HERE / "restore-payload.py"), "exit_code": 0},
            "prepare": {"argv": ["python3", "test/scratch/source-review/restore/offline-runtime/prepare.py",
                                 "test/scratch/source-review/deps"], "exit_code": 0},
            "prove-bound": {"argv": ["python3", rel(TRIALS / CHOSEN / "prove-bound.py")], "exit_code": 0},
            "freeze": {"argv": ["python3", "eik-work/freeze/verify.py"], "exit_code": 0},
            "runtime-export": {"argv": ["python3", "eik-work/offline-runtime/verify.py"], "exit_code": 0},
        },
        "static": check, "retained_freeze_objects": freeze["objects"], "object_facts": objects,
        "special_and_threshold_probe": path_evidence(LOGS / "probe.stdout"),
        "selector": probe["selector"], "rounding_guard": guard,
        "historical_exhaustive": original_full(fp),
        "selection": {"chosen": CHOSEN, "original_order": scores["original_rank"],
                      "rank_with_shared_target_evidence": scores["rank_with_shared_target_evidence"],
                      "boards_at_0_970_vs_id50": [], "live_takeover": None,
                      "ratio_vs_live_champions": dict.fromkeys(BOARDS),
                      "candidate_S": {s: r["S"] for s, r in scores["trials"][CHOSEN]["rows"].items()},
                      "control_S": {s: r["S"] for s, r in scores["control"]["rows"].items()},
                      "ratio_vs_id50": {s: r["ratio_vs_id50"]
                                        for s, r in scores["trials"][CHOSEN]["rows"].items()}},
        "offline_export": {"status": "incomplete", "scratch_restored_payloads": {
            name: offline["files"][name]["sha256"] for name in offline["omitted"]}},
        "gaps": GAPS,
    }
    return scores, result


def main():
    try:
        files = verify_inventory()
        scores, result = audit()
        require(read(HERE / "ledger.json") == scores, "ledger differs from the raw logs")
        require(read(HERE / "result.json") == result, "result claims differ from evidence")
        print(f"PASS source review · {len(files)} evidence files · 9 packets · 2 variants")
        print("Frozen m0-tanh-refine is the least-regressing original trial. No board at 0.970× id50.")
        print("36 shared-small-sigmoid target shards verified outside the original packet.")
        print("Live takeover unknown. Committed runtime export incomplete.")
    except (ValueError, OSError, KeyError, IndexError, TypeError, subprocess.SubprocessError) as exc:
        print(f"FAIL source review: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
