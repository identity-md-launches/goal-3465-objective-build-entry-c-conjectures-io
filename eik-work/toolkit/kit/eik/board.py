"""Board state: accepted entries and the champion of each board (state/boards.json)."""
import json
import shutil
import time
from pathlib import Path

from . import config as K

STATE = K.STATE_DIR / "boards.json"
ENTRIES = K.STATE_DIR / "entries"


def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"boards": {}, "entries": {}, "history": []}


def save(st):
    K.STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=1))


def entry_path(name) -> Path:
    return ENTRIES / f"{name}.c"


def add_entry(st, name, src: Path, meta):
    ENTRIES.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, entry_path(name))
    st["entries"][name] = {**meta, "accepted": time.strftime("%Y-%m-%dT%H:%M:%S")}


def crown(st, board, name, score, seed):
    prev = st["boards"].get(board, {}).get("champion")
    st["boards"][board] = {"champion": name, "score_at_takeover": score, "seed": seed,
                           "since": time.strftime("%Y-%m-%dT%H:%M:%S")}
    st["history"].append({"board": board, "from": prev, "to": name, "score": score, "seed": seed,
                          "time": st["boards"][board]["since"]})


def champions(st):
    return {b: v["champion"] for b, v in st["boards"].items()}
