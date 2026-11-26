#!/usr/bin/env python3
"""Export the input words and two fresh hard pools from the pinned kit cases."""
import os
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[3] / "test/scratch/heldout-2/work/cases"
RAW = HERE / "raw"
SEED = 2715043869

measured = WORK / "measured"
os.environ["EIK_BUILD_DIR"] = str(measured / "build")
os.environ["EIK_HARD_FRESH"] = "1"
sys.path.insert(0, str(measured / "kit"))
from eik import config, inputs

with (RAW / "scored-inputs.bin").open("wb") as output:
    for fn in config.FUNCTIONS:
        path, _ = inputs.fresh_pool_path(SEED, fn)
        shutil.copyfile(path, RAW / f"hard-{fn}.txt")
        shutil.copyfile(WORK / "frozen/build/hard" / path.name, RAW / f"evaluate-hard-{fn}.txt")
        for words in inputs.draw(SEED, fn).values():
            output.write(struct.pack(f"<{len(words)}I", *words))
sample = inputs.target_sample(SEED, config.TARGET_SAMPLE)
(RAW / "target-sample.bin").write_bytes(struct.pack(f"<{len(sample)}I", *sample))
