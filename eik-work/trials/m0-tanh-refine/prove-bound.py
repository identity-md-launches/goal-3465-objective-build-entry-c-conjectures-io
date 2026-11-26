#!/usr/bin/env python3
"""Integer certificate for the exponent-119 Thumb tanh guard."""
from collections import Counter

Q = 1 << 96
SCALE = 1 << 54
HALF = 1 << 22
UNIT = 1 << 23
OLD = 1 << 18
NEW = 31 << 13


def ceildiv(a, b):
    return -(-a // b)


def exp_bounds(m):
    # x = m / 2**31. Evaluate exp(2x) through degree 14, rounded
    # outwards in Q96. Since 2x < 1/64, the tail is less than 2**-96.
    lo = hi = Q
    term_lo = term_hi = Q
    for k in range(1, 15):
        den = k << 30
        term_lo = term_lo * m // den
        term_hi = ceildiv(term_hi * m, den)
        lo += term_lo
        hi += term_hi
    return lo, hi + 1


def scaled_correction(m, exp_q, upper):
    # x - (exp(2x)-1)/(exp(2x)+1), in units of 2**-54.
    den = exp_q + Q
    num = (m << 23) * den - SCALE * (exp_q - Q)
    return ceildiv(num, den) if upper else num // den


def main():
    residual_lo = 0
    residual_hi = -(1 << 32)
    changed = Counter()
    slow = 0
    for f in range(32769, 65536):
        first, last = f << 8, (f << 8) + 255
        first_lo, first_hi = exp_bounds(first)
        last_lo, _ = exp_bounds(last)
        # tanh is increasing. Prove one endpoint is already in the
        # input binade, and tanh(x) < x keeps the other endpoint there.
        if f == 32769:
            assert (first_lo - Q) * 256 > first_lo + Q

        # x - tanh(x) is increasing, and decreases with exp_q when x
        # is held fixed. Endpoints therefore bound all 256 words.
        lo = scaled_correction(first, first_hi, False) + HALF
        hi = scaled_correction(last, last_lo, True) + HALF
        coefficient = 2 * 257 * 17 * ((f * f) >> 16) * 5
        assert coefficient < 1 << 32
        z = (coefficient >> 16) * f + 4419000
        assert 0 <= z < 1 << 32
        residual_lo = min(residual_lo, lo - z)
        residual_hi = max(residual_hi, hi - z)

        r = z % UNIT
        if r >= NEW:
            assert lo > (z - r) and hi < (z - r + UNIT)
            if r < OLD:
                word = (119 << 23) + first - (1 << 23)
                assert word >> 23 == 119
                changed[word >> 20] += 256
        else:
            slow += 256

    assert -NEW < residual_lo <= residual_hi < 0
    print(f"Global outward residual [{residual_lo}, {residual_hi}] in units of 2^-54")
    print(f"Magnitude words in changed guard domain: {(65536 - 32769) * 256}")
    print(f"New fast returns per sign: {sum(changed.values())}")
    print(f"Refinements retained per sign: {slow}")
    print(f"New fast returns by positive targetcheck chunk: {dict(sorted(changed.items()))}")
    print("Negative chunks = positive chunks + 2048")


if __name__ == "__main__":
    main()
