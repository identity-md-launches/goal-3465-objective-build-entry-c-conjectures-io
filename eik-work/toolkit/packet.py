#!/usr/bin/env python3
"""Assemble a baseline packet from completed run.py logs."""
import argparse
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
from run import ROOT, write_json
from verify import baseline, read_json, require, snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="manifest source key, e.g. id50")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--logs", type=Path, help="case's logs directory")
    parser.add_argument("--techniques", help="short source analysis for measured packets")
    args = parser.parse_args()
    try:
        m = read_json(ROOT / "manifest.json")
        entry = snapshot(m)[args.source]
        packet = {"source": args.source, "sha256": entry["sha256"]}
        labels = []
        if entry["status"] == "unavailable":
            packet.update(status="unavailable", source_request=entry["source_request"])
        else:
            require(args.logs is not None, "available sources require --logs")
            labels.append("check")
            check = read_json(args.logs / "check.json")
            gate_record = args.logs / "gate.json"
            if check["exit_code"] == 1 or (gate_record.exists() and read_json(gate_record)["exit_code"] == 1):
                labels.append("gate")
                packet.update(status="gate-rejected")
            else:
                require(check["exit_code"] == 0, "check failed to run")
                rows = {}
                for seed in m["shared_seeds"]:
                    label = f"evaluate-{seed}"
                    labels.append(label)
                    rep = read_json(args.logs / f"{label}.stdout")
                    rows[str(seed)] = {board: rep["scores"][board]["S"] for board in m["board_references"]}
                packet.update(status="measured", scores=rows, techniques=args.techniques)
        args.directory.mkdir(parents=True, exist_ok=True)
        require(not (args.directory / "packet.json").exists(), "packet.json already exists")
        for label in labels:
            for ext in ("json", "stdout", "stderr"):
                name = f"{label}.{ext}"
                shutil.copyfile(args.logs / name, args.directory / name)
        packet_path = args.directory / "packet.json"
        write_json(packet_path, packet)
        try:
            baseline(m, args.directory)
        except Exception:
            packet_path.unlink()
            raise
    except (ValueError, KeyError, OSError, TypeError, IndexError) as exc:
        print(f"packet failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
