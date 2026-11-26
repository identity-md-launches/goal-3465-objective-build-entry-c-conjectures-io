"""Watch only the compare call inside the unmodified eik evaluate."""
import os
from pathlib import Path
import signal
import sys
import time

if len(sys.argv) > 1 and sys.argv[1] == "evaluate":
    started = None
    compare_frame = None
    path = Path(os.environ["TMPDIR"])

    def expired(signum, frame):
        (path / "incumbent-comparison-timeout").write_text(
            "Local incumbent comparison exceeded 600 seconds.\n"
        )
        os.killpg(os.getpgrp(), signal.SIGKILL)

    def watch(frame, event, arg):
        global compare_frame, started
        if event == "call" and frame.f_code.co_name == "compare" and (
            frame.f_globals.get("__name__") == "eik.stages"
        ):
            compare_frame = frame
            started = time.monotonic()
            signal.signal(signal.SIGALRM, expired)
            signal.setitimer(signal.ITIMER_REAL, 600)
        elif event == "return" and frame is compare_frame:
            signal.setitimer(signal.ITIMER_REAL, 0)
            (path / "incumbent-comparison-seconds").write_text(
                f"{time.monotonic() - started:.6f}\n"
            )
            sys.setprofile(None)

    sys.setprofile(watch)
