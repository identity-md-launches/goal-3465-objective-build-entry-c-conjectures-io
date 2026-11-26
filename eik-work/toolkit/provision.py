#!/usr/bin/env python3
"""Stage and verify the exact evaluator assets omitted from the source upload."""
import argparse
import fcntl
import io
from hashlib import file_digest
import json
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import time
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
    error = None
    for attempt in range(3):
        try:
            with urlopen(item["url"], timeout=60) as response, destination.open("wb") as output:
                shutil.copyfileobj(response, output)
            break
        except OSError as exc:
            error = exc
            time.sleep(2 * (attempt + 1))
    else:
        raise ValueError(f"could not download {item['url']}: {error}")
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


def deb_data(package):
    """Return the data tar member of a Debian package (an ar archive), without dpkg."""
    with package.open("rb") as stream:
        if stream.read(8) != b"!<arch>\n":
            raise ValueError("QEMU package is not an ar archive")
        while True:
            header = stream.read(60)
            if len(header) < 60:
                raise ValueError("QEMU package has no data archive")
            name = header[:16].decode().strip().rstrip("/")
            size = int(header[48:58].decode().strip())
            if name.startswith("data.tar"):
                return name, stream.read(size)
            stream.seek(size + size % 2, 1)


def extract(package, needed, tmp, cache):
    name, payload = deb_data(package)
    if not name.endswith((".tar", ".tar.xz", ".tar.gz", ".tar.bz2")):
        raise ValueError(f"unsupported QEMU package compression {name}")
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:*") as tar:
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
