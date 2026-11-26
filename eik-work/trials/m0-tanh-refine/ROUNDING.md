# Rounding certificate for the exponent-119 Thumb family

The single edit is the guard after the polynomial at the end of the
`t_l998689` path. This family has biased input exponent 119 and magnitude
`x = m · 2^-31`, with `2^23 ≤ m < 2^24`. The path extracts `f = m >> 8`,
independently of the sign. The first cell, `f = 32768`, branches away before
the guard because `f << 17` is zero modulo 2^32. This matters near the lower
binade boundary, where the output spacing can differ. For the first input
of the next cell, the certificate proves `tanh(x) > 1/256`. Monotonicity and
`tanh(x) < x < 1/128` then put the exact magnitude in the input binade
through the last input of the final cell.

For the rest of the family, let `D = (x − tanh(x)) · 2^54 + 2^22`, let
`z` be the existing integer polynomial, and set `U = 2^23`. Each ulp is
`2^-31` and the added constant represents half an ulp. The fast return
subtracts `floor(z/U)` from the input word. That is the nearest binary32
magnitude whenever `D` is strictly inside the same interval
`(kU, (k+1)U)` as `z`. Integer subtraction from the input word preserves
the sign and gives that magnitude for either sign. Negation also preserves
the significand parity used for ties to even.

Run `python3 eik-work/trials/m0-tanh-refine/prove-bound.py` from the root.
It enumerates every cell of 256 consecutive magnitude words. For each
endpoint it evaluates the positive Taylor terms of `exp(2x)` through
degree 14 using separately downward- and upward-rounded integer Q96
recurrences. The omitted tail is at most
`2 · (1/64)^15 / 15! < 2^-96`, since the ratio after degree 15 is below
1/2. Adding one Q96 unit to the upward sum therefore encloses the full
exponential. With `tanh(x) = (exp(2x) − 1)/(exp(2x) + 1)`, the lower
correction uses the upper exponential at the first input and the upper
correction uses the lower exponential at the last input. This works
because `x − tanh(x)` is increasing, with derivative `tanh(x)^2`, and
it decreases with the exponential at fixed `x`. Final division rounds
outward in the same units as `z`. The certificate also checks that the
polynomial products and final sum fit unsigned 32-bit arithmetic over
the domain.

The resulting closed bound on `D − z` is **[−250889, −33522]**. Write
`r = z mod U`. The old test required `r ≥ 262144`. The new test
extracts bits 13 through 22 and requires the extracted integer to be at
least 31, giving `r ≥ 253952`. At that exact lower boundary the
certified lower distance to the midpoint is 3063 units. At the opposite
boundary, `r = U − 1`, even the upper endpoint lies 33523 units below
the next midpoint. Every fast result therefore uses the same integer
correction as the exact nearest rounding, including at binade-adjacent
inputs covered by this guard. The proof also checks the strict
inequalities per cell.

At `r = 253951` and below, the candidate still executes the original
refinement with the original intermediate. This keeps every possible
straddle or midpoint equality within the residual interval on the
refinement path, which retains id50's treatment of ties. The guard
admits 5,632 additional fast results per sign and reduces refinements
from 266,240 to 260,608 per sign, a 2.12% reduction. The affected chunk list and counts are in
`prove-bound.stdout`. The targetcheck ranges include the first-cell
boundary, every affected chunk, and the upper boundary of the family
for both signs.
