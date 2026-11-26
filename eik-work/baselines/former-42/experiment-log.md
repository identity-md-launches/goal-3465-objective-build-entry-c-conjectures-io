# Experiment log

No optimization was performed. Both baseline runs use the exact id42 source.
Quick correctness coverage is partial; ratios in the raw output compare only with the local incumbent.

| Run | Seed | RV32IM S | Thumb v6-M S | Overall S | Thumb v7E-M S (diagnostic) |
|---|---|---:|---:|---:|---:|
| B0a | 180434352 | 30.8668188855508 | 47.59018747001752 | 38.326983932556445 | 46.49303828278393 |
| B0b | 2851275305 | 30.864146868820445 | 47.66916564989685 | 38.35711315691715 | 46.65029593485769 |

Each run retains its full evaluator stdout JSON, stderr and command/exit record in evaluate-SEED.{stdout,stderr,json}.
Source modifications: none. Future single-technique experiments in analysis.md have not been run and have no scores.
