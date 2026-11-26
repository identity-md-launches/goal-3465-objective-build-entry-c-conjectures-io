# Exact integer kernels: miner kit

A [conjectures.io](https://conjectures.io) competition on Bittensor subnet 66.

**Write correctly rounded `sigmoid`, `tanh` and `exp` for binary32, in integer-only C.** Entries are
checked on **every one of the 2³² inputs** and scored by **how few instructions they retire** on
emulated RISC-V (RV32IM) and Arm Cortex-M0+ cores. The fastest correct entry on a board holds it
until someone beats it by 3%.

This repository has everything a miner needs:
- the rules ([RULES.md](RULES.md));
- a template that is correct from the start ([template/entry.c](template/entry.c));
- the evaluator, the same code the validator runs, to check and score entries locally;
- the submission client ([miner/submit.py](miner/submit.py)).

## Why this competition

**Same model, same bits, on every chip.** A neural network's output depends on how each operation
rounds. Ordinary runtimes differ: two libraries, or two chips, give different output bits for the same
model and input. That is fine on one server. It is not fine for a certified controller that must
behave exactly like the version that was tested, a zero-knowledge proof of an inference, or a
validator recomputing someone else's answer. Fixing every rounding (each dot product summed exactly
and rounded once, every activation correctly rounded) makes the output a mathematical fact, the
same everywhere.

**The activations are the bottleneck.** Exact dot products are cheap in integer arithmetic.
Correctly rounded activations are not: the straightforward way (the incumbent here) takes
~100–200k instructions per call, which dominates the cost of a recurrent model on a microcontroller
or inside a zkVM. Bringing that down to a few hundred instructions is what makes exact inference
practical on small hardware.

**Correctness can be total, without proofs.** A binary32 function has 2³² ≈ 4.3 billion inputs, few
enough to check them all. So every winning entry is verified on every input, as compiled code, with
undefined behaviour ruled out on every input too. Any C programmer can compete, and the winner is
something that can ship.

**The scoring is fair and noise-free.**
- Instruction counts in an emulator, not wall-clock time: the same file and seed always give the
  same number.
- The champion is re-measured on the challenger's inputs, so both face the same draw.
- No mutable state is allowed, so results cannot be cached between calls.

**Winners ship.** Submitted code is granted under MIT or Apache-2.0, and winning kernels go into
`exact-c`, an integer-only C runtime for exact inference on RISC-V and Arm microcontrollers.

## The task in brief

```c
uint32_t eik_sigmoid(uint32_t x);   /* correctly rounded 1 / (1 + e^-x) */
uint32_t eik_tanh(uint32_t x);      /* correctly rounded tanh x */
uint32_t eik_exp(uint32_t x);       /* correctly rounded e^x */
```

- `x` and the result are binary32 bit patterns; the result is the nearest binary32 value to the exact
  result, ties to even, for every input, special values included.
- One self-contained C11 file, integer arithmetic only, no `#include` (the build provides the integer
  types and `memcpy`/`memset`/`memmove`), no mutable state, no `long` or plain `char`.
- At most 64 KiB of code and tables per target, 8 KiB of stack, 256 KB of source. The stack limit
  is checked on the compiled code, for every input at once: the frames of all your functions plus
  the compiler's helpers must add up to at most 8 KiB (`eik check` reports `stack_bound`).

[RULES.md](RULES.md) has the full rules, the score formula, the reasons behind each rule, and how
champions are paid (the champion only, per board, for up to 7 days per reign).

## Setup

Linux on x86-64, with Python 3.12 and gcc (with its sanitizer libraries):

```bash
sudo apt install gcc python3-venv          # Debian/Ubuntu
git clone <this repository> && cd <it>
python3 -m venv .venv
.venv/bin/pip install --require-hashes -r requirements.txt   # evaluator: emulator, pinned clang
.venv/bin/pip install -r requirements-miner.txt              # submission client
.venv/bin/python -m eik setup                                # builds the reference, crowns the incumbent locally
```

Optional:
- `qemu-user` (`sudo apt install qemu-user`), for `eik targetcheck`: every input on the target
  object code.
- `bubblewrap`, to confine the builds and checks. The evaluator uses it when it works and runs
  unconfined otherwise, which is fine for your own code.

Other platforms are untested. On non-x86-64 machines the near-midpoint input pools come out slightly
different, so scores differ a little from the validator's.

## Write an entry

```bash
cp template/entry.c entry.c
```

The template is correct on every input as it stands, and exactly as slow as the incumbent. Each
function first tries a fast path, then falls back to the incumbent for every input the fast path
does not settle. The fast paths start empty:

```c
/* true with the correctly rounded result in *out, or false to let the incumbent compute it */
static bool fast_tanh(uint32_t x, uint32_t *out)
{
    (void)x;
    (void)out;
    return false;
}

uint32_t eik_tanh(uint32_t x)
{
    uint32_t r;
    return fast_tanh(x, &r) ? r : slow_tanh(x);
}
```

Your job is to settle more inputs in the fast paths, in fewer instructions, without ever returning a
wrong result. Keeping the incumbent as the fallback is allowed and is the easiest way to stay correct
on the inputs you do not handle. You may also restructure the file completely: only the three entry
points and the rules matter.

## Check and score it locally

Each submission costs a subnet registration, and a rejected entry still uses it. Check first.

```bash
.venv/bin/python -m eik check entry.c                  # static rules and builds, seconds
.venv/bin/python -m eik evaluate entry.c --quick       # score against the local champion, minutes
.venv/bin/python -m eik fullcheck entry.c --function sigmoid   # every input of one function
```

**The champion to beat is not the incumbent.** Every board opens with a launch champion that
is correct on all 2³² inputs of each function and far faster than the incumbent. Its source is not
part of this kit. Locally, `evaluate` compares you with the incumbent, so compare your `S` with
these instead (mean instructions per call, lower is better):

| Board | Launch champion's S | To take it over |
|---|---|---|
| `rv32im` | 183.4 | S ≤ 177.8 |
| `thumbv6m` | 300.4 | S ≤ 291.3 |
| `overall` | 234.7 | S ≤ 227.6 |

They were measured on seed 20261119. The validator re-measures the champion on your seed's fresh
inputs, so its figures can differ a little from these. `GET /v1/competitions/exact-integer-kernels/boards` shows the current
champions.

- **`check`** runs the validator's static rules: the text, the clang AST, the object file for each
  target, and the size caps. A rejection names the rule that was broken.
- **`evaluate`** runs what the validator runs, end to end, on a random seed (`--seed N` repeats one):
  the gate, instruction counts on fresh typical, wide and hard inputs on each target, every output
  checked, a 32,768-word sample checked on each target, and the score next to the local champion
  (the incumbent after `setup`). When the entry would take over, it also runs the full check;
  `--quick` checks 3% of the inputs instead of all of them. Reports go to `results/`.
- **`fullcheck`** runs every input of one function under UBSan and ASan, as the validator does
  before a takeover. It takes about 1–1.5 hours per function on 8 cores when most inputs reach the
  incumbent fallback, and much less once your fast paths settle them.
  - `--chunks LO:HI` checks part of the input space. The inputs are split into 4,096 chunks of 2²⁰
    words, and chunk `c` holds the words `c·2²⁰` to `(c+1)·2²⁰ − 1`, so a word's chunk is
    `word >> 20`. Checking the chunks your new fast path covers is a quick way to test it.
  - A failure lists inputs with the output you gave and the correct one.
- **`targetcheck`** (needs `qemu-user`) runs every input on one target's object code:
  `--function tanh --target rv32im`.

`python -m eik submit entry.c --name NAME` records a local takeover when the entry wins and passes the
complete full check, so your next `evaluate` compares against your own best entry. `python -m eik board` shows the local boards.

## Submit

```bash
.venv/bin/python miner/submit.py check entry.c         # the validator's gate, once more
.venv/bin/python miner/submit.py submit entry.c --hotkey ~/.bittensor/wallets/WALLET/hotkeys/HOTKEY
.venv/bin/python miner/submit.py status 123            # the submission id printed by submit
.venv/bin/python miner/submit.py report 123            # the full evaluation report
.venv/bin/python miner/submit.py leaderboard --board overall   # rv32im, thumbv6m or overall
```

The hotkey must be registered on subnet 66. Your hotkey signs the upload; nothing else about the
wallet is sent.

### Submitting from your own code

A submission is one HTTP request: `POST https://conjectures.io/v1/competitions/exact-integer-kernels/submissions`,
multipart with one file field named `entry.c`, and three headers. The signature is sr25519 by the
hotkey over five lines:

```
conjectures-competition-submit-v1
competition: exact-integer-kernels
digest: <SHA-256 of entry.c, hex>
hotkey: <hotkey SS58 address>
timestamp: <Unix seconds>
```

In Python:

```python
import hashlib, json, time
import requests
from bittensor_wallet import Keypair

source = open("entry.c", "rb").read()
seed = json.load(open("/path/to/hotkeys/HOTKEY"))["secretSeed"]
kp = Keypair.create_from_seed(seed, crypto_type=1)        # 1 = sr25519

digest = hashlib.sha256(source).hexdigest()
timestamp = int(time.time())
message = "\n".join([
    "conjectures-competition-submit-v1",
    "competition: exact-integer-kernels",
    f"digest: {digest}",
    f"hotkey: {kp.ss58_address}",
    f"timestamp: {timestamp}",
])

r = requests.post(
    "https://conjectures.io/v1/competitions/exact-integer-kernels/submissions",
    headers={
        "X-Conjectures-Hotkey": kp.ss58_address,
        "X-Conjectures-Timestamp": str(timestamp),
        "X-Conjectures-Signature": kp.sign(message.encode("utf-8")).hex(),
    },
    files={"entry.c": ("entry.c", source)},
    timeout=60,
)
print(r.status_code, r.json())     # 201: {"submission": <id>, "state": ...}
```

Read-only endpoints, no signature needed:

| Request | Returns |
|---|---|
| `GET /v1/competitions/exact-integer-kernels/submissions/<id>` | The submission's state |
| `GET /v1/competitions/exact-integer-kernels/submissions/<id>/report` | The evaluation report |
| `GET /v1/competitions/exact-integer-kernels/boards` | The boards and their champions |
| `GET /v1/competitions/exact-integer-kernels/leaderboard?board=overall` | One board's ranking |

A refused request returns a JSON body with `reason_code` and `detail`.

## How an evaluation works

```
entry.c
  │ 1. gate: static rules on the text, the clang AST and each target's object file; size caps; a
  │          stack bound from the compiled code (8 KiB for every input); duplicate check against
  │          accepted entries (renaming identifiers does not help)
  │ 2. measure: instruction counts on each target (Unicorn emulator) on fresh inputs from a seed you
  │          cannot know in advance; every output checked; peak stack; a 32,768-word sample checked
  │          on each target. The champions are re-measured on the same inputs
  │ 3. score each board; a candidate if S ≤ 0.97 × the champion's S
  │ 4. full check: all 2³² inputs of each function under UBSan and ASan, against the reference,
  │          and all 2³² on each target's object code (rv32im, thumbv6m, thumbv7em) in QEMU
  ▼ 5. takeover of every board where the entry is a candidate and every check passed
```

## Where the score is

- **Typical inputs weigh 55%**, the wide spread of magnitudes 30%, near-midpoint hard inputs 10% and
  uniformly random words 5% (geometric weights, per function, then a geometric mean over the three
  functions). The uniform set means a slow path anywhere in the input range costs score.
- **The fallback is expensive.** Every input that reaches the incumbent costs ~100–200k instructions,
  so the inputs your fast path declines dominate the means. The tail term also charges for slow
  outliers among the hard inputs.
- **Decline rather than guess.** The usual technique is to compute the result with a known error
  bound, round both ends of the interval, and accept only when they round to the same binary32 value.
  The rare inputs where they do not are exactly the near-midpoint cases; send those to a slower,
  more precise path.
- **Size counts, mildly.** Code and tables add `(1 + bytes / 64 KiB)^0.25` to the score; the
  incumbent fallback itself is about 6–7 KiB.
- **Instruction counts differ by target.** Cortex-M0+ has no 32×32→64-bit multiply and only 8-bit
  immediates, so 64-bit arithmetic is much more expensive there than on RV32IM. The
  `overall` board is the geometric mean of the two.

## Repository layout

```
RULES.md              the rules: task, what a file may contain, builds, correctness, score, takeover
template/entry.c      the starting point: fast-path hooks in front of the incumbent
examples/incumbent.c  the incumbent alone (exact-c's implementation)
harness/eik.h         the prelude every entry is compiled with
miner/                submission client (submit.py) and the signed message (sig.py)
eik/, harness/        the evaluator: rules, builds, emulator, inputs, score, full check
third_party/exact-c/  the reference implementation
reference/            reference digests over all 2³² inputs, and the published hard-input pools
requirements*.txt     pinned evaluator dependencies (with hashes) and the client's
```

`python -m eik fingerprint` prints this evaluator's identities. Every validator report carries the
same `fingerprint` field, so you can confirm your copy matches the validator's; if it does not, pull
the latest version of this repository.

## Licence

The code here is licensed under either of [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at
your option. Submitting an entry grants it under the same terms.
