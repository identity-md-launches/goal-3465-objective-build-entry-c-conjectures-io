/* The exact accumulator: FloatLib's `dot` (`Reduction/Runtime.lean`) with nearest-even rounding.
 *
 * A finite word is `M · 2^(k - 150)`, with `k` its exponent field (1 for subnormals) and `M` its
 * significand (with the hidden bit for normals). A product of two is `Ma · Mb · 2^(ka + kb - 300)`:
 * fewer than 48 bits, placed at bit `ka + kb - 2` of an accumulator whose bit 0 weighs 2^-298. */
#include <string.h>

#include "internal.h"

void er_acc_init(er_acc *a)
{
    memset(a, 0, sizeof *a);
    a->all_neg_zero = 1;
}

/* Keeps the first NaN of each kind, quieted with its payload. */
static void capture_nan(er_acc *a, er_word w)
{
    if (!er_is_nan(w))
        return;
    if (!(w & ER_QUIET)) {
        if (!a->have_snan) {
            a->snan = w | ER_QUIET;
            a->have_snan = 1;
        }
    } else if (!a->have_qnan) {
        a->qnan = w;
        a->have_qnan = 1;
    }
}

/* Adds (or subtracts) the 3-limb value `v` at limb `at`, carrying (or borrowing) to the top. */
static void add_at(uint32_t *limb, int at, const uint32_t v[3], int subtract)
{
    uint64_t carry = 0;
    for (int i = at; i < ER_ACC_LIMBS; i++) {
        uint64_t term = i - at < 3 ? v[i - at] : 0;
        if (i - at >= 3 && carry == 0)
            break;
        if (subtract) {
            uint64_t d = (uint64_t)limb[i] - term - carry;
            limb[i] = (uint32_t)d;
            carry = (d >> 32) & 1; /* borrow */
        } else {
            uint64_t s = (uint64_t)limb[i] + term + carry;
            limb[i] = (uint32_t)s;
            carry = s >> 32;
        }
    }
}

void er_acc_add(er_acc *a, er_word x, er_word y)
{
    capture_nan(a, x);
    capture_nan(a, y);
    if (er_is_nan(x) || er_is_nan(y))
        return;
    int negative = ((x ^ y) & ER_SIGN) != 0;
    if ((er_is_inf(x) && er_is_zero(y)) || (er_is_inf(y) && er_is_zero(x))) {
        a->invalid = 1;
        return;
    }
    if (er_is_inf(x) || er_is_inf(y)) {
        if (negative)
            a->neg_inf = 1;
        else
            a->pos_inf = 1;
        return;
    }
    uint32_t ex = (x & ER_EXP) >> 23, ey = (y & ER_EXP) >> 23;
    uint64_t mx = (x & ER_FRAC) | (ex ? 0x800000u : 0), my = (y & ER_FRAC) | (ey ? 0x800000u : 0);
    uint64_t p = mx * my;
    a->all_neg_zero = a->all_neg_zero && p == 0 && negative;
    if (p == 0)
        return;
    uint32_t at = (ex ? ex : 1) + (ey ? ey : 1) - 2; /* bit position of the product's bit 0 */
    uint32_t r = at & 31;
    uint64_t lo = (p & 0xFFFFFFFFu) << r, hi = (p >> 32) << r;
    uint64_t mid = (lo >> 32) + (hi & 0xFFFFFFFFu);
    uint32_t v[3] = {(uint32_t)lo, (uint32_t)mid, (uint32_t)((mid >> 32) + (hi >> 32))};
    add_at(a->limb, (int)(at >> 5), v, negative);
}

/* Index of the highest set bit of the magnitude, or -1 if it is zero. */
static int top_bit(const uint32_t *m)
{
    for (int i = ER_ACC_LIMBS - 1; i >= 0; i--)
        if (m[i])
            for (int b = 31; b >= 0; b--)
                if (m[i] >> b & 1)
                    return 32 * i + b;
    return -1;
}

/* Whether any bit below `i` is set. */
static int any_below(const uint32_t *m, int i)
{
    for (int w = 0; w < (i >> 5); w++)
        if (m[w])
            return 1;
    return (i & 31) && (m[i >> 5] & ((1u << (i & 31)) - 1));
}

er_word er_acc_round(const er_acc *a)
{
    if (a->have_snan)
        return a->snan;
    if (a->have_qnan)
        return a->qnan;
    if (a->invalid || (a->pos_inf && a->neg_inf))
        return ER_CANONICAL_NAN;
    if (a->pos_inf || a->neg_inf)
        return a->neg_inf ? ER_SIGN | ER_EXP : ER_EXP;

    uint32_t m[ER_ACC_LIMBS];
    memcpy(m, a->limb, sizeof m);
    er_word sign = 0;
    if (m[ER_ACC_LIMBS - 1] & ER_SIGN) { /* negative: take the magnitude */
        sign = ER_SIGN;
        uint64_t carry = 1;
        for (int i = 0; i < ER_ACC_LIMBS; i++) {
            uint64_t s = (uint64_t)(uint32_t)~m[i] + carry;
            m[i] = (uint32_t)s;
            carry = s >> 32;
        }
    }
    int h = top_bit(m);
    if (h < 0) /* an exact zero: negative only if every term was a negative zero */
        return a->all_neg_zero ? ER_SIGN : 0;
    /* The top 41 bits (or all, if fewer) and whether anything lies below them. */
    int lo = h > 40 ? h - 40 : 0;
    uint64_t top = 0;
    for (int i = h; i >= lo; i--)
        top = top << 1 | (m[i >> 5] >> (i & 31) & 1);
    return er_pack(sign, top, lo - 298, any_below(m, lo));
}

er_word er_pack(er_word sign, uint64_t m, int e, int sticky)
{
    int t = 63;
    while (!(m >> t & 1))
        t--;
    /* Drop `s` bits: keep 24 significant bits, or down to 2^-149 for subnormal results. */
    int s = t - 23 > -149 - e ? t - 23 : -149 - e;
    uint64_t q;
    if (s <= 0) {
        q = m << -s; /* exact */
    } else {
        uint64_t half = s <= 64 ? m >> (s - 1) & 1 : 0;
        int below = sticky || (s > 1 && (s > 64 || (m & ((UINT64_C(1) << (s - 1)) - 1))));
        q = s < 64 ? m >> s : 0;
        if (half && (below || (q & 1)))
            q++;
    }
    e += s;
    if (q == 0x1000000u) {
        q >>= 1;
        e++;
    }
    if (q < 0x800000u) /* subnormal (e is -149), or zero after rounding */
        return sign | (er_word)q;
    int biased = e + 150;
    if (biased >= 255)
        return sign | ER_EXP;
    return sign | (er_word)biased << 23 | ((er_word)q & ER_FRAC);
}

er_word er_relu(er_word w)
{
    return (w & ER_SIGN) && !er_is_nan(w) ? 0 : w;
}

int er_less(er_word a, er_word b)
{
    if (er_is_nan(a) || er_is_nan(b) || (er_is_zero(a) && er_is_zero(b)))
        return 0;
    /* Map sign-magnitude to an order-preserving unsigned key. */
    uint32_t ka = a & ER_SIGN ? ~a : a | ER_SIGN, kb = b & ER_SIGN ? ~b : b | ER_SIGN;
    return ka < kb;
}
