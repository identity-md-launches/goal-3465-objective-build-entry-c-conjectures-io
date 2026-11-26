/* Shared by the library's source files; not part of the API. */
#ifndef EXACT_INTERNAL_H
#define EXACT_INTERNAL_H

#include "exact.h"

#define ER_SIGN 0x80000000u
#define ER_EXP 0x7F800000u
#define ER_FRAC 0x007FFFFFu
#define ER_QUIET 0x00400000u
#define ER_CANONICAL_NAN 0x7FC00000u
#define ER_ONE 0x3F800000u

static inline int er_is_nan(er_word w) { return (w & ER_EXP) == ER_EXP && (w & ER_FRAC) != 0; }
static inline int er_is_inf(er_word w) { return (w & ~ER_SIGN) == ER_EXP; }
static inline int er_is_zero(er_word w) { return (w & ~ER_SIGN) == 0; }

/* Rounds `m · 2^e` to binary32, nearest-even; `sticky` says nonzero bits lie below `m`'s bit 0.
 * `m` must be nonzero. Handles subnormal results and overflow to infinity. */
er_word er_pack(er_word sign, uint64_t m, int e, int sticky);

/* Correctly rounded tanh (`fn` 0), sigmoid (1) or exp (2) of `w`. `*level` is the index of the
 * precision that settled it, -1 if none was needed (special values and saturated inputs), and
 * past the last precision if none settled (the tests show none does). */
er_word er_activation(int fn, er_word w, int *level);

#endif
