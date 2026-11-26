#!/usr/bin/env python3
"""Restore the three omitted pinned runtime assets into the scratch export copy."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[4]
EXPORT = ROOT / "test/scratch/heldout-3/offline-runtime"


def restore(export, name, asset):
    whole = sha256()
    with urllib.request.urlopen(asset["provenance"], timeout=120) as response:
        for part in asset["parts"]:
            data = response.read(part["bytes"])
            if len(data) != part["bytes"] or sha256(data).hexdigest() != part["sha256"]:
                raise ValueError(f"payload part disagrees with pin: {part['path']}")
            path = export / part["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            whole.update(data)
        if response.read(1) or whole.hexdigest() != asset["sha256"]:
            raise ValueError(f"payload disagrees with pin: {name}")
    print(name, whole.hexdigest(), flush=True)


def main():
    contents = (EXPORT / "manifest.json").read_bytes()
    if sha256(contents).hexdigest() != "fe7340f53675006f4d258a6ef4fa20910a56dc4eb7fda0f1d9078586403fd950":
        raise ValueError("unexpected offline-runtime manifest")
    manifest = json.loads(contents)
    with ThreadPoolExecutor() as workers:
        tasks = [workers.submit(restore, EXPORT, name, manifest["files"][name])
                 for name in manifest["omitted"]]
        for task in tasks:
            task.result()


if __name__ == "__main__":
    main()
