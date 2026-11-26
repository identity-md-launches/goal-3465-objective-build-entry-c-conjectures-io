#!/usr/bin/env python3
"""Reconstruct the pinned evaluator dependencies in a new or empty directory."""
import argparse
from hashlib import file_digest, sha256
import json
import lzma
from pathlib import Path
import sys
from contextlib import nullcontext
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
TOOLKIT = HERE.parent / "toolkit"
SPLIT_BYTES = 4 * 1024 * 1024
IDENTITIES = {
    "dependencies.json", "provision.py", "run.py", "verify.py", "manifest.json",
    "files.json", "kit/requirements.txt", "kit/RULES.md", "kit/reference/digests.sha256",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ordinary(path):
    require(path.is_file() and path.resolve() == path, f"missing or non-ordinary file: {path}")
    return path


def digest(path):
    with ordinary(path).open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def read_json(path):
    return json.loads(ordinary(path).read_bytes())


def bundle_manifest():
    manifest = read_json(HERE / "manifest.json")
    require(manifest["schema"] == 1 and manifest["split_bytes"] == SPLIT_BYTES,
            "unknown bundle format")
    require(set(manifest["toolkit_sha256"]) == IDENTITIES, "incomplete toolkit identity")
    for name, expected in manifest["toolkit_sha256"].items():
        require(digest(TOOLKIT / name) == expected, f"toolkit identity differs: {name}")

    pins = read_json(TOOLKIT / "dependencies.json")
    qemu = pins["qemu"]
    index = read_json(TOOLKIT / "files.json")
    notices = set(pins["upstream"]["license_paths"])
    notices.add(pins["upstream"]["vendored_exact_c_provenance"])
    notices.update([qemu["license_path"], qemu["source_descriptor"]])
    for wheel in pins["wheels"]:
        notices.update(name for name in wheel["license_paths"] if name.startswith(("licenses/", "wheels/")))
    expected = {name: (index[name], f"toolkit/{name}", "0644") for name in notices}
    for item in [*pins["wheels"], *qemu["source_archives"], *qemu["executables"].values()]:
        provenance = item.get("url") or item.get("origin") or qemu["package_url"]
        expected[item["path"]] = (item["sha256"], provenance,
                                  "0755" if "package_member" in item else "0644")

    files = manifest["files"]
    require(set(files) == set(expected), "manifest must cover every pinned dependency and notice")
    for name, item in files.items():
        require((item["sha256"], item["provenance"], item["mode"]) == expected[name],
                f"asset disagrees with toolkit pin: {name}")
    return manifest


def reconstruct(manifest, destination=None, *, omitted=()):
    """Validate part and whole-file hashes, optionally writing the reconstructed files."""
    used = set()
    for name, item in manifest["files"].items():
        require(type(item["bytes"]) is int and item["bytes"] > 0, f"invalid size: {name}")
        count = (item["bytes"] + SPLIT_BYTES - 1) // SPLIT_BYTES
        require(len(item["parts"]) == count, f"wrong part count: {name}")
        packed = item.get("xz")
        archive = nullcontext()
        if packed is not None:
            path = f"payload/{name}.xz"
            require(packed["path"] == path and type(packed["bytes"]) is int
                    and 0 < packed["bytes"] <= SPLIT_BYTES, f"invalid XZ metadata: {name}")
            if name not in omitted:
                source = ordinary(HERE / path)
                require(source.stat().st_size == packed["bytes"] and digest(source) == packed["sha256"],
                        f"wrong packed size or hash: {path}")
                archive = lzma.open(source, "rb")
                used.add(path)
        whole = sha256()
        output = None
        if destination is not None and name not in omitted:
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            output = target.open("xb")
        try:
            with archive as stream:
                for i, part in enumerate(item["parts"]):
                    path = f"payload/{name}.part{i:03}"
                    size = min(SPLIT_BYTES, item["bytes"] - i * SPLIT_BYTES)
                    require(part["path"] == path and part["bytes"] == size
                            and len(bytes.fromhex(part["sha256"])) == 32, f"invalid part: {path}")
                    if name in omitted:
                        continue
                    if stream is None:
                        used.add(path)
                        source = ordinary(HERE / path)
                        require(source.stat().st_size == size, f"wrong size: {path}")
                        data = source.read_bytes()
                    else:
                        data = stream.read(size)
                    require(len(data) == size and sha256(data).hexdigest() == part["sha256"],
                            f"wrong reconstructed part: {path}")
                    whole.update(data)
                    if output is not None:
                        output.write(data)
                if stream is not None:
                    require(not stream.read(1), f"extra decompressed bytes: {name}")
        finally:
            if output is not None:
                output.close()
        if name in omitted:
            continue
        require(whole.hexdigest() == item["sha256"], f"wrong reconstructed hash: {name}")
        if output is not None:
            target.chmod(int(item["mode"], 8))
            require(digest(target) == item["sha256"], f"wrong on-disk hash: {name}")
    actual = {p.relative_to(HERE).as_posix() for p in (HERE / "payload").rglob("*")
              if not p.is_dir() or p.is_symlink()}
    require(actual == used, "payload inventory differs from manifest")


def prepare(destination):
    destination = destination.absolute()
    require(destination.resolve() == destination, "destination must not traverse symlinks or '..'")
    require(not destination.exists() or (destination.is_dir() and not any(destination.iterdir())),
            "destination must be a new or empty directory")
    manifest = bundle_manifest()
    missing = [name for name in manifest.get("omitted", [])
               if not all((HERE / part["path"]).is_file() for part in manifest["files"][name]["parts"])]
    require(not missing, "required payloads absent from export: " + ", ".join(missing))
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".eik-prepare-", dir=destination.parent) as temporary:
        staged = Path(temporary) / "dependencies"
        staged.mkdir()
        reconstruct(manifest, staged)
        staged.rename(destination)
    print(f"Prepared {len(manifest['files'])} pinned files and verified their on-disk hashes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="new or empty dependency directory")
    args = parser.parse_args()
    try:
        prepare(args.directory)
    except (ValueError, OSError, KeyError, TypeError, lzma.LZMAError, EOFError) as exc:
        print(f"preparation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
