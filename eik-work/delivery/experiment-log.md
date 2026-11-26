# Experiment log

No optimization or source edits were performed during packaging. This is the complete reviewed ledger, including losses and unscored attempts.

Exact records: [experiments.json](experiments.json), copied from the [independent review ledger](../final-validation/review/ledger.json).

## Paired control and all trials

| Trial | Seed | RV32IM S | Thumbv6-M S | Overall S | RV32IM / id50 | Thumbv6-M / id50 | Overall / id50 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| id50 paired control | 1874435642 | 28.522714242420 | 40.515260593492 | 33.994193627226 | 1.000000000000 | 1.000000000000 | 1.000000000000 |
| id50 paired control | 1947282751 | 28.517414314251 | 40.303038973861 | 33.901894645300 | 1.000000000000 | 1.000000000000 | 1.000000000000 |
| m0-exp-layout | 1874435642 | 28.522714242420 | 42.118337476893 | 34.660197694462 | 1.000000000000 | 1.039567236146 | 1.019591700705 |
| m0-exp-layout | 1947282751 | 28.517414314251 | 41.903766813631 | 34.568585154039 | 1.000000000000 | 1.039717298758 | 1.019665287610 |
| m0-exp-reduction | 1874435642 | 28.522714242420 | 41.117853670279 | 34.246062408677 | 1.000000000000 | 1.014873237095 | 1.007409170643 |
| m0-exp-reduction | 1947282751 | 28.517414314251 | 40.919484266949 | 34.160179835095 | 1.000000000000 | 1.015295255861 | 1.007618606349 |
| m0-sigmoid-cell | 1874435642 | 28.522714242420 | 42.187309581038 | 34.688565491188 | 1.000000000000 | 1.041269609600 | 1.020426190178 |
| m0-sigmoid-cell | 1947282751 | 28.517414314251 | 41.979862804710 | 34.599958677104 | 1.000000000000 | 1.041605394371 | 1.020590708546 |
| m0-tanh-refine | 1874435642 | 28.522714242420 | 40.530568943209 | 34.000615230461 | 1.000000000000 | 1.000377841571 | 1.000188902943 |
| m0-tanh-refine | 1947282751 | 28.517414314251 | 40.316224056690 | 33.907439670532 | 1.000000000000 | 1.000327148601 | 1.000163560925 |
| rv-exp-interval | 1874435642 | 32.896202279995 | 40.515260593492 | 36.507508925018 | 1.153333515191 | 1.000000000000 | 1.073933664241 |
| rv-exp-interval | 1947282751 | 32.836443113706 | 40.303038973861 | 36.378681209943 | 1.151452328457 | 1.000000000000 | 1.073057467453 |
| rv-exp-loads | 1874435642 | 28.995332482698 | 40.515260593492 | 34.274676534308 | 1.016569890097 | 1.000000000000 | 1.008250906321 |
| rv-exp-loads | 1947282751 | 28.993482723323 | 40.303038973861 | 34.183701733225 | 1.016693954221 | 1.000000000000 | 1.008312428874 |
| rv-tanh-quadratic | 1874435642 | 30.692301086524 | 40.515260593492 | 35.263388616729 | 1.076065230878 | 1.000000000000 | 1.037335640416 |
| rv-tanh-quadratic | 1947282751 | 30.738935677005 | 40.303038973861 | 35.197620979341 | 1.077900518549 | 1.000000000000 | 1.038219879673 |
| shared-small-sigmoid | 1874435642 | 30.745565922610 | 45.476042482479 | 37.392334268463 | 1.077932684151 | 1.122442304858 | 1.099962384121 |
| shared-small-sigmoid | 1947282751 | 30.820392303525 | 45.345928651655 | 37.384212047490 | 1.080756900464 | 1.125124303432 | 1.102717486401 |

## Techniques and disposition

### m0-exp-layout

Thumb exp high-word layout: the 512 aux words of t_eps rows 0..511 (stride-16 interleaved) copied unchanged into contiguous uint32_t t_hb[512]; the 8 stride-16 loads in t_mt, t_mn, t_exp_res, t_exp_den and the two xrow/xkm/xkq table loads in t_eik_exp now index t_hb. t_eps is untouched, so aliases (t_xrow, t_xkm, t_xkq, t_dkn, tanh/sigmoid row pointers, dead NaN-branch t_eps casts) keep their data. Result: thumbv6m +2084 bytes, S worse; rv32im identical code (EIK_SEL selects the _r path).

Original disposition: eligible loss.

Packet: [eik-work/trials/m0-exp-layout/packet.json](../../eik-work/trials/m0-exp-layout/packet.json).

### m0-exp-reduction

One exact specialization of negative exp reduction for row 10. Thumbv6-M regressed on both seeds; RV32IM text and scores are identical. Exhaustive host and all-target checks passed.

Original disposition: eligible loss.

Packet: [eik-work/trials/m0-exp-reduction/packet.json](../../eik-work/trials/m0-exp-reduction/packet.json).

### m0-sigmoid-cell

Use directly addressable narrow coefficients for the 91 negative Thumb sigmoid cells. The original shared table and rounding path are preserved. Both Thumb targets regress, and RV32IM emits identical scored text and rodata.

Original disposition: eligible loss.

Packet: [eik-work/trials/m0-sigmoid-cell/packet.json](../../eik-work/trials/m0-sigmoid-cell/packet.json).

### m0-tanh-refine

Lower the fast rounding cutoff in the biased-exponent-119 Thumb tanh path using a certified one-sided residual. Both signs and all changed cells are covered. The extra guard cost offsets the refinements saved.

Original disposition: selected fallback.

Packet: [eik-work/trials/m0-tanh-refine/packet.json](../../eik-work/trials/m0-tanh-refine/packet.json).

### rv-exp-interval

Single early unsigned word-range check in eik_exp_r for [0xBF800001,0xC0800000], jumping to the identical original cubic cell and refinement arithmetic. RV32 regresses by about 15.2%; Thumb allocated sections and scores are unchanged under the preserved id50 selector. No takeover recommendation. Full-population stage scores paired with unchanged id50, two-seed quick sanitizer checks, complete all-input host checks and selected object checks retained; bounded evaluate attempts documented separately.

Original disposition: eligible loss.

Packet: [eik-work/trials/rv-exp-interval/packet.json](../../eik-work/trials/rv-exp-interval/packet.json).

### rv-exp-loads

Typed table-row indexing in the two RV32IM positive exp reductions. Same-input comparison with former submission 50. RV32IM regressed and both Thumb images were byte-identical.

Original disposition: eligible loss.

Packet: [eik-work/trials/rv-exp-loads/packet.json](../../eik-work/trials/rv-exp-loads/packet.json).

### rv-tanh-quadratic

Guarded quadratic (degree-reduced) fast path in eik_tanh_r cells_ for tld_r rows 0..27 (t in [0x7B201000,0x7C..), c1!=0): drops the c3*t cubic term via per-row precomputed c2' = c2 + mulhsx(c3, cell-centre t) (new 28-entry int32 table tq_r, 112 bytes), keeps the high-half multiply formulation, returns w-(Vq>>8) only when Vq mod 256 lies in an exhaustively proven window (even rows [4,213], odd rows [44,253]) so the cubic would return the identical value; otherwise falls through to the unchanged cubic/refinement. Result: rv32im S regresses (see ratios); thumbv6m code generation unchanged.

Original disposition: eligible loss.

Packet: [eik-work/trials/rv-tanh-quadratic/packet.json](../../eik-work/trials/rv-tanh-quadratic/packet.json).

### shared-small-sigmoid

Negative trial vs id50 (eligible, distinct normalised source; not a duplicate): one target-independent pre-selector fast path in eik_sigmoid for |x| < 2^-7: returns 0.5 for |x| < 2^-24, else floor(a+1/2) of the affine term a = x*2^22 (x>0, ulp 2^-24) or |x|*2^23 (x<0, ulp 2^-25) in Q15, fast return only when the Q15 fraction exceeds a per-exponent floor of the x^3/48 bound, otherwise the unchanged id50 selector and kernels. Correct on all 2^32 inputs of all three functions (host UBSan/ASan) and on 12 affected sigmoid chunks per target, but S regresses on both boards (rv32im ~1.08x, thumbv6m ~1.12x): the range test runs before id50's first branch on every call (rv32im 4 extra instructions before bltz; thumbv6m ~8 before the original lsls/bmi), and the fast body (~22-26 instr) is slower than id50's own rv32 affine path. See README.md.

Original disposition: rejected: no packet-indexed targetcheck.

Packet: [eik-work/trials/shared-small-sigmoid/packet.json](../../eik-work/trials/shared-small-sigmoid/packet.json).

## Additional measured variants

### shared-small-sigmoid v2

Affine guard for biased exponents 90–114, F nonzero, no table.

Seed 1874435642: rv32im S=31.108404818512, ratio=1.090653734919; thumbv6m S=43.638988061835, ratio=1.077100021636; overall S=36.844800264050, ratio=1.083855692183.

single seed, measured target sample, no retained quick host or targetcheck packet. Verdict: measure-only regression.

### shared-small-sigmoid v3

Narrow v2 to biased exponents 103–114.

Seed 1874435642: rv32im S=30.912174324024, ratio=1.083773937547; thumbv6m S=43.404484719411, ratio=1.071311996606; overall S=36.629591836258, ratio=1.077524951406.

single seed, measured target sample, no retained quick host or targetcheck packet. Verdict: measure-only regression.

## Unscored attempts and evidence discrepancies

The following original attempt records include timeouts; an absent score is never converted to a gain. These records are preserved verbatim as JSON in the reviewed ledger.

```json
[
  {
    "evidence": {
      "path": "eik-work/trials/paired-control/evaluate-attempts.json",
      "sha256": "db4c04aca6a73704fe97d66e85a84666c6eb3ee596256eaf007ed8ab549ea6f7"
    },
    "records": {
      "attempts": [
        {
          "command": "python3 eik-work/toolkit/run.py test/scratch/pc control-1874435642 evaluate-1874435642 evaluate eik-work/baselines/former-50/entry.c --quick --json --seed 1874435642",
          "ended": "2026-11-26T10:37:35+01:00",
          "exit_code": 124,
          "parallel_with": "the same command for seed 1947282751 in case control-1947282751",
          "progress": "fresh hard pools for both seeds were written by 10:28:26; the measurement pool was still running at the cap",
          "run_record": "none (run.py writes LABEL.json only after the evaluator exits)",
          "started": "2026-11-26T10:27:50+01:00",
          "stderr": "",
          "stdout": "",
          "wrapper": "timeout 585"
        },
        {
          "command": "python3 eik-work/toolkit/run.py test/scratch/pc control-1947282751 evaluate-1947282751 evaluate eik-work/baselines/former-50/entry.c --quick --json --seed 1947282751",
          "ended": "2026-11-26T10:37:35+01:00",
          "exit_code": 124,
          "run_record": "none",
          "started": "2026-11-26T10:27:50+01:00",
          "stderr": "",
          "stdout": "",
          "wrapper": "timeout 585"
        },
        {
          "command": "python3 eik-work/toolkit/run.py test/scratch/pc control-1874435642 evaluate-1874435642 evaluate eik-work/baselines/former-50/entry.c --quick --json --seed 1874435642",
          "ended": "2026-11-26T10:47:57+01:00",
          "exit_code": 124,
          "run_record": "none",
          "started": "2026-11-26T10:38:07+01:00",
          "stderr": "",
          "stdout": "",
          "wrapper": "timeout 590, through a scratch shim around run.runner that only raised EIK_THREADS from 2 to 5 (worker pool size; not part of the fingerprint). The shim is not used for any recorded run."
        }
      ],
      "replacement": "Each seed is measured by the stages evaluate is built from (kit/eik/evaluate.py: compare -> _measure_many for the entry, host_check -> fullcheck quick with the evaluation seed): measure-SEED = `eik measure SRC --seed SEED`, fullcheck-SEED-FN = `eik fullcheck SRC --function FN --quick --seed SEED`, all through unmodified run.py with its default settings.",
      "why": "eik evaluate re-measures the locally registered champion (the exact-c incumbent, ~1e5 instructions per call, counted by a Python block hook) on every scored input of rv32im and thumbv6m. That job alone did not finish within the 10-minute cap this worker's sandbox puts on one command, and background processes are killed when a command ends. The incumbent re-measurement only produces the printed incumbent ratio; it does not enter the entry's S. The entry part of the same evaluation (measure stage, every target, with sample) took 9 s."
    }
  },
  {
    "evidence": {
      "path": "eik-work/trials/rv-exp-loads/incumbent-evaluate-attempts.json",
      "sha256": "26903f05de4e9883b30d2dc4c5d4e70c9b81288bd08e620513ef764914390476"
    },
    "records": [
      {
        "argv": [
          "timeout",
          "570",
          "python3",
          "eik-work/toolkit/run.py",
          "test/scratch/rv-exp-loads",
          "incumbent-1874435642",
          "evaluate-1874435642",
          "evaluate",
          "eik-work/trials/rv-exp-loads/entry.c",
          "--quick",
          "--json",
          "--seed",
          "1874435642"
        ],
        "exit_code": 124,
        "files": {
          "incumbent-1874435642.stderr": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "incumbent-1874435642.stdout": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        },
        "source_sha256": "8e5f8332e0fdf6a70edaecd6255c7b11a9920f988329a0b753dd5559e47f5595"
      },
      {
        "argv": [
          "timeout",
          "570",
          "python3",
          "eik-work/toolkit/run.py",
          "test/scratch/rv-exp-loads",
          "incumbent-1947282751",
          "evaluate-1947282751",
          "evaluate",
          "eik-work/trials/rv-exp-loads/entry.c",
          "--quick",
          "--json",
          "--seed",
          "1947282751"
        ],
        "exit_code": 124,
        "files": {
          "incumbent-1947282751.stderr": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "incumbent-1947282751.stdout": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        },
        "source_sha256": "8e5f8332e0fdf6a70edaecd6255c7b11a9920f988329a0b753dd5559e47f5595"
      }
    ]
  },
  {
    "evidence": {
      "path": "eik-work/trials/rv-exp-interval/evaluate-attempt-1874435642.attempt.json",
      "sha256": "3143bc01d5040f372dadf526a098bd7be42df63d1b4480a27e7b343264e275d2"
    },
    "records": {
      "command": [
        "python3",
        "eik-work/toolkit/run.py",
        "test/scratch/rv-exp-interval",
        "rv-exp-interval",
        "evaluate-attempt-1874435642",
        "evaluate",
        "eik-work/trials/rv-exp-interval/entry.c",
        "--quick",
        "--json",
        "--seed",
        "1874435642"
      ],
      "completed_evaluate_report": false,
      "exit_code": -9,
      "kit_verdict": null,
      "observation": "The wrapper terminated the run group at its stated cap without a completed evaluator report; the pinned compare stage includes slow local incumbent remeasurement. This is a timeout observation, not a source rejection.",
      "reason": "Local incumbent remeasurement did not finish within the trial budget; use unchanged measure/fullcheck stages for absolute S and paired id50 ratios.",
      "scores": null,
      "seconds": 180.105,
      "source_sha256": "259751b6c7fd5072a081211b8a11f4e27a5d0e8bda9aaab666ae067dd20a0ea9",
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "timed_out": true,
      "timeout_seconds": 180
    }
  },
  {
    "evidence": {
      "path": "eik-work/trials/rv-exp-interval/evaluate-attempt-1947282751.attempt.json",
      "sha256": "74564b44d1c2bd4ce6a000fab1216642424dbe5089fc20dc5586a50c5279d161"
    },
    "records": {
      "command": [
        "python3",
        "eik-work/toolkit/run.py",
        "test/scratch/rv-exp-interval",
        "rv-exp-interval",
        "evaluate-attempt-1947282751",
        "evaluate",
        "eik-work/trials/rv-exp-interval/entry.c",
        "--quick",
        "--json",
        "--seed",
        "1947282751"
      ],
      "completed_evaluate_report": false,
      "exit_code": -9,
      "kit_verdict": null,
      "observation": "The wrapper terminated the run group at its stated cap without a completed evaluator report; the pinned compare stage includes slow local incumbent remeasurement. This is a timeout observation, not a source rejection.",
      "reason": "Local incumbent remeasurement did not finish within the trial budget; use unchanged measure/fullcheck stages for absolute S and paired id50 ratios.",
      "scores": null,
      "seconds": 180.023,
      "source_sha256": "259751b6c7fd5072a081211b8a11f4e27a5d0e8bda9aaab666ae067dd20a0ea9",
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "timed_out": true,
      "timeout_seconds": 180
    }
  }
]
```

The shared-small-sigmoid supplement has 36 external target reports omitted by its original packet. They do not change selection; missing original report bindings and checker executables remain disclosed in [review.md](../final-validation/review/review.md#shared-small-sigmoid-eligibility-discrepancy).

Original selection minimizes the best-board worst-seed ratio, then worst-seed overall. All seven eligible trials have best-board ratio 1.0; m0-tanh-refine wins the tiebreak despite regressing. No combination was justified by two independent gains.

## Original freeze narrative

The complete original selection narrative remains unchanged in [freeze/experiments.md](../freeze/experiments.md). Its no-takeover statements refer to historical id50; live eligibility remains undetermined. The review ledger above incorporates the later evidence discrepancy and additional variants.
