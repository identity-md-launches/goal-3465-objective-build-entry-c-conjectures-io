# The reference: `exact-c`

These files are the reference the evaluator checks entries against: `exact-c`'s correctly rounded
`er_sigmoid`, `er_tanh` and `er_exp`, an integer-only C implementation using Ziv's strategy on big
binary floats with directed rounding. They build the reference library, the full-check binary
(`harness/check.c`) and the digests in `reference/*.digest`.

An independent implementation on GNU MPFR agrees with them on all 2³² inputs of every function.

Licence: MIT OR Apache-2.0 (`LICENSE-MIT`, `LICENSE-APACHE`).

```
716ed6a99b22590ea00dd09d23ecd490372a59fe62ae3cf699ff1c2fec6aa60a  include/exact.h
e298e01725d6713d3545c1c8874952bd0c041c7ca32ae387679d533b8da36173  src/acc.c
06c4a699955a42ea4ed5bb31918e56b6afe0f1c94373fc5ef2457510e3c1371a  src/act.c
bc11ebad65b150518d906605ac29f5e83947da798390093d2950fc468aaa7b43  src/internal.h
f730216b9453bfa2f3fce37e72a6c47967c908c774781062e7d28a5cb34fa209  src/scalar.c
1db83d0cd496e2a7625f625327f0e026c1684ebe20bbb945368a5f2bafa15d06  src/sha256.c
```

The verifier fingerprint (`python -m eik fingerprint`) hashes these files, so any change to them
shows up there.
