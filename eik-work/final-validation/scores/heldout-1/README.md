# heldout-1: paired score comparison on fresh seed 849230117

Outcome: **incomplete** (an evidenced non-success). The frozen root `entry.c` and the unchanged former
champion 50 were measured on the same seed, inputs, kit and measurement identity; no current-board
reference source is public (submissions 52, 53 and 56 are withheld), so the current S, the ratios and the
`<= 0.970` eligibility are null / undetermined on every board. See `scores.md` for the table and
`scores.json` for full-precision values.

- `drive.py`: the driver that was run (from scratch) around the unchanged `eik-work/toolkit/run.py`;
  it caps `eik evaluate` at 600 s and retains exits, times and logs. Neither evaluation hit the cap.
- `raw/cand`, `raw/id50`: stdout/stderr of every command, the runner's own records, `commands.json`,
  and the fresh hard pools of the seed. `raw/provision.*`, `raw/bootstrap.*`: runtime restoration.
- `current-references.json`: extract of the landed board snapshot showing no reference bytes exist.
- `build_scores.py`: assembles `scores.json`, `scores.md` and `result.json` from `raw/`.
- `verify.py`: standard-library offline check. It re-hashes all evidence, binds sources and kit files,
  recomputes S / overall S / ratios from the raw class means and rejects unsupported success.

The held-out seed was used once, for measurement only; the candidate source was not changed.
