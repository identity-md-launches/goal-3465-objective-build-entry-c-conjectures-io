#!/usr/bin/env python3
"""Stage and verify the exact evaluator assets omitted from the source upload."""
import argparse
import fcntl
from hashlib import file_digest
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
DEFAULT = ROOT.parents[1] / "test/scratch/eik-dependencies"


def digest(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def checked(path, item):
    if not path.is_file() or digest(path) != item["sha256"]:
        raise ValueError(f"missing or invalid dependency {item['path']}")


def download(destination, item):
    with urlopen(item["url"], timeout=45) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)
    checked(destination, item)


def stage(cache, fetch=False):
    deps = json.loads((ROOT / "dependencies.json").read_text())
    qemu = deps["qemu"]
    executables = list(qemu["executables"].values())
    loose = [item for item in deps["wheels"] if item["storage"] == "staged"]
    loose += qemu["source_archives"]
    cache.mkdir(parents=True, exist_ok=True)
    with (cache / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for item in deps["wheels"]:
            if item["storage"] == "bundled":
                checked(ROOT / item["path"], item)
        missing = []
        for item in [*loose, *executables]:
            try:
                checked(cache / item["path"], item)
            except ValueError:
                missing.append(item)
        if missing and not fetch:
            raise ValueError(f"missing or invalid staged assets: {', '.join(i['path'] for i in missing)}")
        if not missing:
            return
        with tempfile.TemporaryDirectory(prefix="fetch-", dir=cache) as tmp:
            tmp = Path(tmp)
            for item in loose:
                if item in missing:
                    staged = tmp / Path(item["path"]).name
                    download(staged, item)
                    install(staged, cache / item["path"])
            needed = {item["package_member"]: item for item in executables if item in missing}
            if needed:
                package = tmp / "qemu.deb"
                download(package, {"url": qemu["package_url"], "sha256": qemu["package_sha256"],
                                   "path": "qemu.deb"})
                extract(package, needed, tmp, cache)


def install(staged, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    staged.replace(destination)


def extract(package, needed, tmp, cache):
    with subprocess.Popen(["dpkg-deb", "--fsys-tarfile", str(package)],
                          stdout=subprocess.PIPE) as proc:
        try:
            with tarfile.open(fileobj=proc.stdout, mode="r|") as tar:
                for member in tar:
                    item = needed.get(member.name.removeprefix("./"))
                    if item is None:
                        continue
                    if not member.isfile():
                        raise ValueError(f"unexpected archive member type for {member.name}")
                    staged = tmp / Path(item["path"]).name
                    with tar.extractfile(member) as source, staged.open("wb") as output:
                        shutil.copyfileobj(source, output)
                    checked(staged, item)
                    staged.chmod(0o755)
            if proc.wait() != 0:
                raise ValueError("could not read QEMU package")
        finally:
            if proc.poll() is None:
                proc.kill()
    for item in needed.values():
        staged = tmp / Path(item["path"]).name
        checked(staged, item)
        install(staged, cache / item["path"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependencies", type=Path, default=DEFAULT)
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    try:
        stage(args.dependencies.resolve(), fetch=args.fetch)
    except (ValueError, OSError, tarfile.TarError) as exc:
        print(f"dependency staging failed: {exc}", file=sys.stderr)
        return 1
    print("Pinned wheels, QEMU executables and QEMU source archives verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
