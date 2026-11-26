#!/usr/bin/env python3
"""Observe entry to the kit's incumbent worker and cap only that phase."""
import os
import runpy
import selectors
import signal
import subprocess
import sys
import time
from pathlib import Path


def evaluate(fd, argv):
    sys.path.insert(0, str(Path.cwd()))
    from eik import board, stages

    incumbent = board.entry_path("incumbent").resolve()

    def mark(event, frame):
        source, target, _, sample = frame.f_locals["args"]
        if Path(source) == incumbent and not sample:
            os.write(fd, f"{event} {target}\n".encode())

    def start(code, offset):
        mark("start", sys._getframe(1))

    def finish(code, offset, result):
        mark("finish", sys._getframe(1))

    monitor = sys.monitoring
    monitor.use_tool_id(4, "heldout-incumbent-observer")
    monitor.register_callback(4, monitor.events.PY_START, start)
    monitor.register_callback(4, monitor.events.PY_RETURN, finish)
    monitor.set_local_events(4, stages._job.__code__,
                             monitor.events.PY_START | monitor.events.PY_RETURN)
    sys.argv = ["eik", *argv]
    runpy.run_module("eik", run_name="__main__", alter_sys=True)


def supervise(argv):
    before = time.monotonic()
    read_fd, write_fd = os.pipe()
    with subprocess.Popen([sys.executable, __file__, "--worker", str(write_fd), *argv],
                          pass_fds=(write_fd,), start_new_session=True) as child:
        os.close(write_fd)
        deadline = None
        finished = set()
        with os.fdopen(read_fd, "rb", buffering=0) as stream, selectors.DefaultSelector() as selector:
            selector.register(stream, selectors.EVENT_READ)
            while len(finished) < 2:
                remaining = None if deadline is None else max(0, deadline - time.monotonic())
                if not selector.select(remaining):
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
                    print("Timeout: incumbent comparison exceeded 600s", file=sys.stderr)
                    return 124
                line = stream.readline().decode().strip()
                if not line:
                    break
                event, target = line.split()
                if event == "start" and deadline is None:
                    deadline = time.monotonic() + 600
                    print(f"Incumbent worker started after {time.monotonic() - before:.3f}s "
                          f"({target}); 600s cap armed", file=sys.stderr, flush=True)
                if event == "finish":
                    finished.add(target)
                    print(f"Incumbent worker finished ({target})", file=sys.stderr, flush=True)
        return child.wait()


if __name__ == "__main__":
    if sys.argv[1] == "--worker":
        evaluate(int(sys.argv[2]), sys.argv[3:])
    else:
        sys.exit(supervise(sys.argv[1:]))
