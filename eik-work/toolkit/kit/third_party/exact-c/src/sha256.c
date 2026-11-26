/* SHA-256 (FIPS 180-4), for the hashes in run records. */
#include <string.h>

#include "exact.h"

static const uint32_t K[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2};

static uint32_t rotr(uint32_t x, int n) { return x >> n | x << (32 - n); }

static void block(uint32_t h[8], const uint8_t b[64])
{
    uint32_t w[64], v[8];
    for (int i = 0; i < 16; i++)
        w[i] = (uint32_t)b[4 * i] << 24 | (uint32_t)b[4 * i + 1] << 16 |
               (uint32_t)b[4 * i + 2] << 8 | b[4 * i + 3];
    for (int i = 16; i < 64; i++) {
        uint32_t s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3);
        uint32_t s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }
    memcpy(v, h, sizeof v);
    for (int i = 0; i < 64; i++) {
        uint32_t t1 = v[7] + (rotr(v[4], 6) ^ rotr(v[4], 11) ^ rotr(v[4], 25)) +
                      ((v[4] & v[5]) ^ (~v[4] & v[6])) + K[i] + w[i];
        uint32_t t2 = (rotr(v[0], 2) ^ rotr(v[0], 13) ^ rotr(v[0], 22)) +
                      ((v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]));
        memmove(v + 1, v, 7 * sizeof *v);
        v[4] += t1;
        v[0] = t1 + t2;
    }
    for (int i = 0; i < 8; i++)
        h[i] += v[i];
}

void er_sha256_init(er_sha256_ctx *c)
{
    static const uint32_t iv[8] = {0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                                   0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19};
    memcpy(c->h, iv, sizeof iv);
    c->len = 0;
}

void er_sha256_update(er_sha256_ctx *c, const void *data, size_t n)
{
    const uint8_t *p = data;
    while (n) {
        size_t used = (size_t)(c->len % 64), take = 64 - used < n ? 64 - used : n;
        memcpy(c->buf + used, p, take);
        c->len += take;
        p += take;
        n -= take;
        if (c->len % 64 == 0)
            block(c->h, c->buf);
    }
}

void er_sha256_final(er_sha256_ctx *c, uint8_t out[32])
{
    uint64_t bits = c->len * 8;
    uint8_t pad = 0x80, zero = 0, len[8];
    er_sha256_update(c, &pad, 1);
    while (c->len % 64 != 56)
        er_sha256_update(c, &zero, 1);
    for (int i = 0; i < 8; i++)
        len[i] = (uint8_t)(bits >> (56 - 8 * i));
    er_sha256_update(c, len, 8);
    for (int i = 0; i < 8; i++)
        for (int j = 0; j < 4; j++)
            out[4 * i + j] = (uint8_t)(c->h[i] >> (24 - 8 * j));
}

void er_sha256(const void *data, size_t n, uint8_t out[32])
{
    er_sha256_ctx c;
    er_sha256_init(&c);
    er_sha256_update(&c, data, n);
    er_sha256_final(&c, out);
}

void er_sha256_words(const er_word *v, size_t n, uint8_t out[32])
{
    er_sha256_ctx c;
    er_sha256_init(&c);
    for (size_t i = 0; i < n; i++) {
        uint8_t b[4] = {(uint8_t)v[i], (uint8_t)(v[i] >> 8), (uint8_t)(v[i] >> 16),
                        (uint8_t)(v[i] >> 24)};
        er_sha256_update(&c, b, 4);
    }
    er_sha256_final(&c, out);
}
