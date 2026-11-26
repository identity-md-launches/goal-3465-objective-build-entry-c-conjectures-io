# Measured unchanged selector id42

Quick coverage: **partial**. Scores are instruction-count metrics; lower is better.

| Seed | RV32IM S | Thumb v6-M S | Overall S | Thumb v7E-M S (diagnostic) |
|---|---:|---:|---:|---:|
| 180434352 | 30.8668188855508 | 47.59018747001752 | 38.326983932556445 | 46.49303828278393 |
| 2851275305 | 30.864146868820445 | 47.66916564989685 | 38.35711315691715 | 46.65029593485769 |

Current-champion same-seed ratios: unavailable. Live board takeovers: not established.
The raw evaluation comparisons are against the local incumbent only.

| Target | Code | Read-only data | Other allocated | Total charged bytes | Static stack bound |
|---|---:|---:|---:|---:|---:|
| rv32im | 6728 | 12920 | 0 | 19648 | 192 |
| thumbv6m | 4332 | 15538 | 96 | 19966 | 332 |
| thumbv7em | 5040 | 15538 | 96 | 20674 | 336 |

See `report.json` for seed-specific peak stack, wrong-output counts, class means, p99.9, score terms, input identities and host checks; `analysis.md` for techniques and two proposed experiments.
