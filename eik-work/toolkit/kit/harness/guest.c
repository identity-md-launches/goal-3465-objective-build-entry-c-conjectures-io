/* Linked with a submission into a bare-metal image for each target ISA. The emulator calls
 * eik_sigmoid / eik_tanh / eik_exp directly to count instructions, and eik_batch to run many inputs at
 * full emulator speed for the target-side correctness check. Nothing runs at start-up. */
#include "eik.h"

/* The memory functions a submission may call. Their instructions count toward its score, the
 * same for every entry (simple loops; -fno-builtin keeps the compiler from calling itself). */
void *memcpy(void *d, const void *s, size_t n)
{
    uint8_t *a = d;
    const uint8_t *b = s;
    while (n--)
        *a++ = *b++;
    return d;
}

void *memmove(void *d, const void *s, size_t n)
{
    uint8_t *a = d;
    const uint8_t *b = s;
    if (a < b)
        while (n--)
            *a++ = *b++;
    else
        while (n--)
            a[n] = b[n];
    return d;
}

void *memset(void *d, int c, size_t n)
{
    uint8_t *a = d;
    while (n--)
        *a++ = (uint8_t)c;
    return d;
}

/* out[i] = f(in[i]) for i < n; f indexes eik/config.py's FUNCTIONS: 0 sigmoid, 1 tanh, 2 exp. */
void eik_batch(uint32_t f, const uint32_t *in, uint32_t *out, uint32_t n)
{
    for (uint32_t i = 0; i < n; i++)
        out[i] = f == 0 ? eik_sigmoid(in[i]) : f == 1 ? eik_tanh(in[i]) : eik_exp(in[i]);
}
