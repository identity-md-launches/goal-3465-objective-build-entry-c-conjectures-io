#!/usr/bin/env python3
"""Check the frozen-source coverage matrix and the retained kit merge, offline."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = "593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b"
VERIFIER = "ebbf9d5cac596a718532b34798dc452e4050d6940594005c44f9a729c699c5a8"
MEASUREMENT = "2c8fd1f3a6711f0639685319fb25262b02bfecf4c6589c52cb58928270a46322"
FUNCTIONS = ("sigmoid", "tanh", "exp")
RUNTIMES = ("host", "rv32im", "thumbv6m", "thumbv7em")
TARGETS = RUNTIMES[1:]
CHUNKS = 4096
CHUNK_WORDS = 1 << 20


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read_path(rel):
    need(isinstance(rel, str) and rel and not rel.startswith("/"), "invalid artifact path")
    path = ROOT / rel
    need(path.resolve().is_relative_to(ROOT) and path.is_file() and not path.is_symlink(),
         f"missing or unsafe artifact: {rel}")
    return path


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def artifact(item):
    need(isinstance(item, dict) and set(item) == {"path", "sha256"}, "malformed artifact")
    path = read_path(item["path"])
    need(digest(path) == item["sha256"], f"tampered artifact: {item['path']}")
    return path


def obj(item):
    return json.loads(artifact(item).read_text())


def same_fingerprint(value):
    need(isinstance(value, dict) and value.get("verifier") == VERIFIER
         and value.get("measurement") == MEASUREMENT and value.get("sandbox") == "none",
         "incompatible fingerprint")


def verify_record(cell, selected, report):
    record = obj(selected["record"])
    stdout = artifact(selected["stdout"])
    stderr = artifact(selected["stderr"])
    need(record.get("exit_code") == 0 and record.get("source_sha256") == SOURCE,
         f"failed or unbound run: {cell['runtime']}/{cell['function']}")
    need(record.get("stdout_sha256") == digest(stdout)
         and record.get("stderr_sha256") == digest(stderr)
         and stderr.stat().st_size == 0, "run stream digest or stderr mismatch")
    argv = record.get("argv")
    kind = "fullcheck" if cell["runtime"] == "host" else "targetcheck"
    need(isinstance(argv, list) and len(argv) >= 6 and argv[1:4] == ["-m", "eik", kind]
         and "--function" in argv and argv[argv.index("--function") + 1] == cell["function"],
         "run argv does not bind function")
    need(argv[4].startswith("$REPO/") and
         digest(read_path(argv[4].removeprefix("$REPO/"))) == SOURCE,
         "run argv does not bind frozen source bytes")
    if cell["runtime"] != "host":
        need("--target" in argv and argv[argv.index("--target") + 1] == cell["runtime"],
             "run argv does not bind target")
    need("--quick" not in argv, "quick sample cannot count as exhaustive")
    if "--chunks" in argv:
        lo, hi = map(int, argv[argv.index("--chunks") + 1].split(":"))
        need((lo, hi) == (report["chunk_lo"], report["chunk_hi"]), "argv/report range conflict")
    need("--out" in argv or digest(stdout) == digest(artifact(selected["report"])),
         "run stdout is not its report")
    if "--out" in argv:
        need(Path(argv[argv.index("--out") + 1]).name ==
             Path(selected["report"]["path"]).name, "run output filename conflict")


def verify_cell(cell, fingerprint):
    runtime, fn = cell["runtime"], cell["function"]
    packet = obj(cell["packet"])
    packet_result = obj(cell["packet_result"])
    need(packet_result.get("status") == cell["packet_status"] and
         cell["packet_status"] in ("pass", "incomplete"), f"packet status conflict: {runtime}/{fn}")
    need(packet.get("function") == fn and
         packet.get("status", packet_result.get("status")) in ("pass", "incomplete"),
         f"wrong coverage packet: {runtime}/{fn}")
    need(cell["status"] in ("pass", "incomplete", "fail"), "invalid cell status")
    selected = cell["selected"]
    need(isinstance(selected, list) and selected, f"no selected reports: {runtime}/{fn}")
    covered = bytearray(CHUNKS)
    words = 0
    mismatches = 0
    for item in selected:
        report = obj(item["report"])
        need(report.get("schema") == "eik-report-1" and
             report.get("competition") == "exact-integer-kernels" and
             report.get("sha256") == SOURCE and
             report.get("function") == fn and
             report.get("kind") == ("fullcheck" if runtime == "host" else "targetcheck"),
             f"report identity conflict: {runtime}/{fn}")
        same_fingerprint(report.get("fingerprint"))
        need(report["fingerprint"] == fingerprint, "different fingerprint between reports")
        need(report.get("verdict") == "passed" and report.get("stage") is None
             and report.get("reasons") == [] and report.get("range_complete") is True
             and report.get("mismatches") == 0, f"report failure: {runtime}/{fn}")
        if runtime == "host":
            need(report.get("quick") is False and report.get("exit") == 0,
                 f"sample or sanitizer/checker failure: {runtime}/{fn}")
            need(item.get("image") is None, "host report has target image")
        else:
            need(report.get("target") == runtime, "target report conflict")
            need(digest(artifact(item["image"])) == report.get("image_sha256"),
                 f"unbound checker image: {runtime}/{fn}")
            artifact(item["object"])
        lo, hi = report.get("chunk_lo"), report.get("chunk_hi")
        need(type(lo) is int and type(hi) is int and 0 <= lo < hi <= CHUNKS,
             "invalid chunk interval")
        need(item.get("chunks") == [lo, hi] and
             report.get("words_checked") == (hi - lo) * CHUNK_WORDS,
             "range or word count conflict")
        need(not any(covered[lo:hi]), f"double-counted overlap: {runtime}/{fn}")
        covered[lo:hi] = b"\1" * (hi - lo)
        words += report["words_checked"]
        mismatches += report["mismatches"]
        verify_record(cell, item, report)
    gaps = []
    start = None
    for i in range(CHUNKS + 1):
        absent = i < CHUNKS and not covered[i]
        if absent and start is None:
            start = i
        if not absent and start is not None:
            gaps.append([start, i])
            start = None
    chunks = sum(covered)
    need(cell["chunks_covered"] == chunks and cell["words_checked"] == words
         and cell["mismatches"] == mismatches and cell["gaps"] == gaps
         and cell.get("sanitizer_failures") == 0,
         f"coverage matrix overclaims {runtime}/{fn}")
    need(cell["status"] == ("pass" if not gaps and mismatches == 0 else "incomplete"),
         f"cell verdict overclaims {runtime}/{fn}")
    if cell["packet_status"] == "incomplete":
        need(cell.get("resolution") == "fresh rerun" and all(
            p["report"]["path"].startswith("eik-work/final-validation/merged/rerun/")
            for p in selected), "incomplete packet credited without a fresh rerun")
    for prior in cell.get("excluded_prior", []):
        old = obj(prior["report"])
        need(old.get("sha256") == SOURCE and old.get("function") == fn and
             old.get("image_sha256") == prior.get("image_sha256") and
             old.get("image_sha256") != report.get("image_sha256") and
             prior.get("reason") == "checker image not retained", "invalid excluded prior")
    return chunks, words


def verify_merge(matrix, cells):
    merge = matrix["merge"]
    record = obj(merge["record"])
    stdout_path = artifact(merge["stdout"])
    stderr_path = artifact(merge["stderr"])
    need(record.get("exit_code") == 0 and record.get("stdout_sha256") == digest(stdout_path)
         and record.get("stderr_sha256") == digest(stderr_path) and
         stderr_path.stat().st_size == 0, "pinned kit merger failed or streams differ")
    argv = record.get("argv")
    need(isinstance(argv, list) and argv[1:4] == ["-m", "eik", "merge"],
         "merger command was not the kit")
    need("--require-targets" in argv and
         argv[argv.index("--require-targets") + 1] == ",".join(TARGETS),
         "required target set changed")
    reported_paths = ["$REPO/" + p["report"]["path"] for c in cells for p in c["selected"]]
    need(argv[4:argv.index("--require-targets")] == reported_paths,
         "merger inputs differ from selected raw reports")
    raw = json.loads(stdout_path.read_text())
    need(raw.get("kind") == "fullcheck-merged" and raw.get("sha256") == SOURCE and
         raw.get("fingerprint") == matrix["fingerprint"] and
         raw.get("required_targets") == sorted(TARGETS), "merger identity mismatch")
    all_pass = all(c["status"] == "pass" for c in cells)
    expected = "passed" if all_pass else "incomplete"
    need(raw.get("verdict") == expected and raw.get("reasons") == [],
         "unsupported merger verdict")
    for c in cells:
        dest = raw["functions"][c["function"]] if c["runtime"] == "host" else \
            raw["targets"][c["runtime"]][c["function"]]
        need(dest == {"chunks_covered": c["chunks_covered"],
                      "words_checked": c["words_checked"]}, "merger/matrix count conflict")
    return record["exit_code"], raw["verdict"]


def main():
    matrix = json.loads((HERE / "coverage-matrix.json").read_text())
    result = json.loads((HERE / "result.json").read_text())
    need(matrix.get("schema") == 1 and result.get("schema") == 1, "unknown schema")
    need(matrix.get("source") == {"path": "entry.c", "sha256": SOURCE} and
         digest(read_path("entry.c")) == SOURCE, "frozen source changed")
    same_fingerprint(matrix.get("fingerprint"))
    need(digest(read_path("eik-work/toolkit/kit/RULES.md")) ==
         "d9a56849153fff88e3873f3550035e426b88d6fbcbe064e42c4456819b08352e",
         "kit rules changed")
    for name, expected in matrix["toolkit"].items():
        need(digest(read_path(name)) == expected, f"toolkit identity changed: {name}")
    detail = obj(matrix["fingerprint_report"])
    same_fingerprint(detail)
    fp_run = matrix["fingerprint_run"]
    fp_record = obj(fp_run["record"])
    fp_stdout = artifact(fp_run["stdout"])
    fp_stderr = artifact(fp_run["stderr"])
    need(fp_run["stdout"] == matrix["fingerprint_report"] and
         fp_record.get("exit_code") == 0 and
         fp_record.get("stdout_sha256") == digest(fp_stdout) and
         fp_record.get("stderr_sha256") == digest(fp_stderr) and
         fp_stderr.stat().st_size == 0 and
         fp_record.get("argv", [])[1:5] == ["-m", "eik", "fingerprint", "--details"],
         "fingerprint run was not retained intact")
    for side in ("verifier", "measurement"):
        for name, expected in detail["details"][side]["files"].items():
            need(digest(read_path("eik-work/toolkit/kit/" + name)) == expected,
                 f"pinned {side} file changed: {name}")
    cells = matrix.get("cells")
    need(isinstance(cells, list) and len(cells) == 12 and
         [(c["runtime"], c["function"]) for c in cells] ==
         [(r, f) for r in RUNTIMES for f in FUNCTIONS], "matrix must have twelve distinct cells")
    for c in cells:
        verify_cell(c, matrix["fingerprint"])
    selected_paths = {p["report"]["path"] for c in cells for p in c["selected"]}
    need(len(matrix.get("excluded_overlaps", [])) == 8, "missing overlap audit")
    for item in matrix["excluded_overlaps"]:
        old = obj(item["report"])
        need(item["report"]["path"] not in selected_paths and
             item["reason"] == "overlaps selected exhaustive range" and
             old.get("sha256") == SOURCE and old.get("function") == item["function"] and
             old.get("chunk_lo") is not None and 0 <= old["chunk_lo"] < old["chunk_hi"] <= CHUNKS and
             (item["runtime"] == "host" and old.get("kind") == "fullcheck" or
              item["runtime"] != "host" and old.get("kind") == "targetcheck" and
              old.get("target") == item["runtime"]),
             "excluded overlap is incompatible or selected")
    code, verdict = verify_merge(matrix, cells)
    status = "pass" if verdict == "passed" else "incomplete"
    need(matrix.get("status") == status and result.get("status") == status,
         "summary overclaims status")
    need(result.get("gaps") == [] and result.get("measured_facts", {}).get("cells_passed") == 12 and
         result["measured_facts"].get("chunks_covered") == 12 * CHUNKS and
         result["measured_facts"].get("words_checked") == 12 * CHUNKS * CHUNK_WORDS and
         result["measured_facts"].get("mismatches") == 0 and
         result["measured_facts"].get("sanitizer_failures") == 0 and
         result["measured_facts"].get("merged_verdict") == verdict,
         "summary count conflict")
    need(result.get("source") == matrix["source"] and
         result.get("fingerprint") == matrix["fingerprint"], "result identity conflict")
    for item in result["artifacts"].values():
        artifact(item)
    need(result["artifacts"]["coverage_matrix"]["path"] ==
         "eik-work/final-validation/merged/coverage-matrix.json", "wrong matrix artifact")
    need(result["commands"]["merge"]["exit_code"] == code and
         result["commands"]["merge"]["verdict"] == verdict,
         "recorded merge command conflict")
    print("verify: PASS: 12 cells; 49,152 unique chunks; 51,539,607,552 inputs; kit merge passed")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, IndexError, json.JSONDecodeError, OSError) as exc:
        print(f"verify: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
