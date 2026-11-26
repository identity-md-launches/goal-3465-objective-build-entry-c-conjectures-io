/* Builds the pool of hard inputs: words whose real result lies very close to the midpoint between
 * two binary32 values. A fast path with a loose error bound cannot decide the rounding there and
 * must fall back, so the scorer draws its hard set from this pool.
 *
 * Host-only tool (it may use floating point; submissions may not). The closeness estimate uses x87
 * long double (64-bit significand), accurate to about 2^-60 relative, far finer than the 2^-18 ulp
 * threshold used here. Correctness never depends on this file: it only chooses inputs to time.
 *
 *   hardscan <sigmoid|tanh|exp> <samples> <log2_threshold_ulps> [seed]
 * prints "word distance_in_ulps" for every sampled word whose result is within 2^t ulps of a
 * rounding midpoint (t negative, e.g. -18). */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static long double word_to_ld(uint32_t w)
{
    float f;
    memcpy(&f, &w, 4);
    return (long double)f;
}

int main(int argc, char **argv)
{
    if (argc < 4)
        return 2;
    int fn = !strcmp(argv[1], "sigmoid") ? 0 : !strcmp(argv[1], "tanh") ? 1 : !strcmp(argv[1], "exp") ? 2 : -1;
    if (fn < 0) {
        fprintf(stderr, "unknown function %s (sigmoid, tanh or exp)\n", argv[1]);
        return 2;
    }
    unsigned long long n = strtoull(argv[2], NULL, 10), seed = argc > 4 ? strtoull(argv[4], NULL, 10) : 7;
    long double thr = ldexpl(1.0L, atoi(argv[3]));
    for (unsigned long long i = 0; i < n; i++) {
        seed = seed * 6364136223846793005ull + 1442695040888963407ull;
        uint32_t r = (uint32_t)(seed >> 32);
        /* exponents 96..134: |x| from 2^-31 to 2^8, where the evaluation actually runs */
        uint32_t w = (r & 0x80000000u) | (96u + (r >> 23 & 0xFF) % 39u) << 23 | (r & 0x7FFFFFu);
        long double x = word_to_ld(w);
        long double y = fn == 0 ? 1.0L / (1.0L + expl(-x)) : fn == 1 ? fabsl(tanhl(x)) : expl(x);
        /* sigmoid and |tanh| below 1; exp below the binary32 overflow (2^128), and positive */
        if (!(y > 0) || (fn < 2 && y >= 1.0L) || y >= 0x1p128L)
            continue;
        int e;
        frexpl(y, &e); /* y = m * 2^e, m in [0.5, 1) */
        int ulp_exp = e - 24 < -149 ? -149 : e - 24;
        long double scaled = ldexpl(y, -ulp_exp), frac = scaled - floorl(scaled);
        long double d = fabsl(frac - 0.5L);
        if (d < thr)
            printf("%08x %.3Le\n", w, d);
    }
    return 0;
}
