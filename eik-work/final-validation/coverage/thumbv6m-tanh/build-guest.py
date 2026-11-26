import os
from pathlib import Path
import sys

case = Path(sys.argv[1]).resolve()
source = Path("entry.c").resolve()
os.environ["EIK_BUILD_DIR"] = str(case / "build")
os.environ["ZIG_GLOBAL_CACHE_DIR"] = str(case / "build/zig-cache")
os.environ["ZIG_LOCAL_CACHE_DIR"] = os.environ["ZIG_GLOBAL_CACHE_DIR"]
os.environ["HOME"] = str(case / "home")
os.environ["TMPDIR"] = str(case / "tmp")
sys.path.insert(0, str(case / "kit"))

from eik.toolchain import guest_image

print(guest_image(source, "thumbv6m").relative_to(Path.cwd()))
