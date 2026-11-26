# Thumb tanh refinement guard

This is one experiment from exact former submission 50. The guard at the
end of the biased-exponent-119 Thumb tanh path now refines below 253952
instead of below 262144 in the Q23 remainder. It admits 5,632 additional
fast returns per sign. The proof covers every affected cell and both
signs. [Rounding certificate](ROUNDING.md) · [Exact source diff](id50.diff)

Thumbv6-M S increased by 0.0378% and 0.0327% versus id50. The
extra guard cost outweighed the saved refinements on both seeds.
[Paired measurements](MEASUREMENTS.md) · [Verification packet](packet.json)

| Source | SHA-256 | Normalised SHA-256 |
| --- | --- | --- |
| id50 | `88617bb49e36a06cabd7d84ce6fe504ee337f8f41ad7c55bc72f696db94060c3` | `e8722042f89400f887e0e526338d22ae756c029c4646c49c4d290da1bda04db8` |
| Trial | `593e2420f5363dcb5d4fe429dd486f23b88ed9e917c22864c6c1b3e7ec0c5f6b` | `adf3a5a8074ffcca8e58ea852f58143a20a00aa6a74df8f14c1b742fa21a03c8` |

## Emitted code and cost

Both builds put the estimate in `r1` before the guard. id50 tests two
shifts and branches on nonzero.
The trial uses two literal loads, an AND and a compare, then branches to
the original refinement on unsigned lower. The literal mask
`0x007fe000` keeps bits 13–22. The compiler's comparator `0x0003c001`
is equivalent to a lower cutoff of `0x0003e000` because the masked
operand advances by `0x2000`. The fast path still subtracts `z >> 23`.
The remaining slow path still computes `(z >> 23)`, then enters the
same refinement with the same integer argument. RV32IM has identical
linked `.text` and `.rodata` bytes. Both Thumb `.text` sections differ.
[Disassembly and section hashes](thumb-disassembly.txt)

The pinned emulator's per-call counter compared both compiled Thumbv6-M
images. Both signs of
`0x3b859800` make the same rounded result in 34 instructions instead
of 75. The examples with certified distance intervals `[0, 1]` and
`[-1, 0]` include a midpoint in their enclosure and still refine, at
76 instructions instead of 75. Existing fast calls at the ends of
the affected range take 34 instructions instead of 32. Static Thumbv6-M
image size increases by eight bytes. [Witness counts](thumb-witness.stdout)

## Reproduction and evidence

The pinned runner used Python 3.12 and GCC 13.3.0 on Linux x86-64. The
setup ran in a separate scratch case because the setup command installs
the stock slow incumbent as a local champion. Both quick evaluations
used fresh local cases with empty board state, producing absolute S
from the regular scored populations and fresh hard pools. The evaluator
labels empty boards as takeover candidates and runs its quick host
check. Same-seed comparison against id50 is computed separately by the
paired-control verifier. The packet includes the command, exit code
and stdout/stderr hashes for each evaluator invocation.

The public API reported promotions 59, 60 and 61 for RV32IM, Thumbv6-M
and overall. Source requests returned HTTP 403 `SOURCE_WITHHELD` for
submissions 52, 53 and 56. Live champion absolute S and same-seed
ratios are unavailable. [Boards endpoint](https://conjectures.io/v1/competitions/exact-integer-kernels/boards) · [Source responses](live-sources.json)

The selected targetcheck ranges are 952:960 and 3000:3008, which cover
all biased-exponent-119 words for positive and negative inputs. The
ordinary tracked inputs for offline replay are this directory's entry,
the pinned toolkit harness and its `kit/reference/tanh.digest`
(SHA-256 `6596c8553a866cac76ac119eb05c832788d10d1e972ee32bbae35f513b21c34a`).
The runner verifies the staged QEMU binary against
`eik-work/toolkit/dependencies.json`. With the pinned dependencies
already staged, replay one shard from the repository root with:

```sh
python3 eik-work/toolkit/run.py test/scratch/replay-m0-tanh thumb pos \
  targetcheck eik-work/trials/m0-tanh-refine/entry.c \
  --function tanh --target thumbv6m --chunks 952:960 --jobs 2
```

Use distinct labels for the other chunks and Thumbv7-M. Recompute the
merged exhaustive verdict from the retained reports with this command.

```sh
trial=eik-work/trials/m0-tanh-refine
python3 eik-work/toolkit/run.py test/scratch/replay-m0-tanh thumb merged merge \
  "$trial"/exhaustive-{sigmoid,tanh,exp}.stdout "$trial"/targetcheck-*-all.stdout \
  --require-targets rv32im,thumbv6m,thumbv7em
```

Run the packet verifier from the root with this command.

```sh
python3 eik-work/trials/paired-control/verify.py eik-work/trials/m0-tanh-refine
```
