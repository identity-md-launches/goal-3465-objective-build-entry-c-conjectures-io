/* Single binary32 operations, each correctly rounded to nearest-even with FloatLib's NaN choice
 * (`chooseNaN2`/`chooseNaN3`: the first signalling NaN, quieted, else the first quiet NaN).
 *
 * Addition, multiplication and fused multiply-add are exact dot products of one or two terms,
 * which have exactly these rules (`x + y = x·1 + y·1`, `fma(x, y, z) = x·y + z·1`). */
#include "internal.h"

static er_word dot2(er_word a, er_word b, er_word c, er_word d)
{
    er_acc s;
    er_acc_init(&s);
    er_acc_add(&s, a, b);
    er_acc_add(&s, c, d);
    return er_acc_round(&s);
}

er_word er_add(er_word x, er_word y) { return dot2(x, ER_ONE, y, ER_ONE); }
/* `x + (−y)`: FloatLib negates y first, which flips the sign bit even of a NaN. */
er_word er_sub(er_word x, er_word y) { return er_add(x, y ^ ER_SIGN); }
er_word er_fma(er_word x, er_word y, er_word z) { return dot2(x, y, z, ER_ONE); }

er_word er_mul(er_word x, er_word y)
{
    er_acc s;
    er_acc_init(&s);
    er_acc_add(&s, x, y);
    return er_acc_round(&s);
}

/* The first NaN of two by FloatLib's rule, quieted; 0 if neither is NaN. */
static er_word choose_nan(er_word x, er_word y)
{
    if (er_is_nan(x) && !(x & ER_QUIET))
        return x | ER_QUIET;
    if (er_is_nan(y) && !(y & ER_QUIET))
        return y | ER_QUIET;
    if (er_is_nan(x))
        return x;
    if (er_is_nan(y))
        return y;
    return 0;
}

/* A finite nonzero word as `m · 2^e` with `m`'s top bit at bit 23. */
static void normalize(er_word w, uint64_t *m, int *e)
{
    uint32_t k = (w & ER_EXP) >> 23;
    *m = (w & ER_FRAC) | (k ? 0x800000u : 0);
    *e = (int)(k ? k : 1) - 150;
    while (!(*m & 0x800000u)) {
        *m <<= 1;
        (*e)--;
    }
}

er_word er_div(er_word x, er_word y)
{
    er_word nan = choose_nan(x, y);
    if (nan)
        return nan;
    er_word sign = (x ^ y) & ER_SIGN;
    if ((er_is_inf(x) && er_is_inf(y)) || (er_is_zero(x) && er_is_zero(y)))
        return ER_CANONICAL_NAN;
    if (er_is_inf(x) || er_is_zero(y))
        return sign | ER_EXP;
    if (er_is_inf(y) || er_is_zero(x))
        return sign;
    uint64_t mx, my;
    int ex, ey;
    normalize(x, &mx, &ex);
    normalize(y, &my, &ey);
    uint64_t q = (mx << 40) / my; /* at least 40 significant bits */
    return er_pack(sign, q, ex - ey - 40, (mx << 40) % my != 0);
}

er_word er_maximum(er_word x, er_word y)
{
    er_word nan = choose_nan(x, y);
    if (nan)
        return nan;
    if (er_is_zero(x) && er_is_zero(y))
        return x & y & ER_SIGN; /* -0 only if both are -0 */
    return er_less(x, y) ? y : x;
}

er_word er_nat(uint32_t n)
{
    return n ? er_pack(0, n, 0, 0) : 0;
}
