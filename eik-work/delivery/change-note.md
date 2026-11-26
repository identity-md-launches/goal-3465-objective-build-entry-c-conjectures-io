# Change versus public base

The frozen entry starts from former champion id50, source SHA256 `88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3`. Its only functional source edit is the exponent-119 tanh remainder guard in `t_l998689`:

```diff
- if (((t_z << 9) >> 27) != 0u)
+ if (((t_z << 9) >> 22) >= 31u)
```

The effective remainder cutoff falls from 262144 to 253952. It admits 5,632 new fast returns per sign without changing the quotient or refinement below the cutoff. The [review](../final-validation/review/review.md#exponent-119-tanh-change), [ROUNDING.md](../trials/m0-tanh-refine/ROUNDING.md), [certificate](../trials/m0-tanh-refine/prove-bound.py) and [fresh replay log](../final-validation/review/logs/prove-bound.stdout) explain the enclosure and strict rounding margins. The new strict interval avoids midpoint ties in newly fast cases.

RV32IM code sections remain equivalent to id50; the inherited selector chooses the other arm on Thumb. Thumbv6-M grows eight code/table bytes (20,500 to 20,508). Existing fast calls pay extra instructions, so this chosen entry slightly regresses against id50 despite locally cheaper refinement cases. It was frozen as the least-regressing eligible trial under the prior selection rule, not because it improved performance.

Packaging copied exact bytes and assembled evidence only. No candidate edits, evidence corrections or further optimization were made. [Original diff](../freeze/entry-vs-id50.diff).
