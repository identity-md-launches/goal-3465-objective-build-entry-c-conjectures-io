"""Build the scoring guest from the same case cache and target object."""
from pathlib import Path
import sys

case, source = (Path(arg).resolve() for arg in sys.argv[1:])
sys.path.insert(0, str(case / "kit"))
from eik import toolchain

guest = toolchain.guest_image(source, "thumbv7em")
print(guest.name, toolchain.sha(guest))
