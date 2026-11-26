/* The full correctness check: every one of the 2^32 binary32 inputs, on the host.
 *
 * The input space is split into 4096 chunks of 2^20 words. For each chunk the outputs are hashed
 * (SHA-256 over the little-endian words) and compared with the reference digest of that chunk.
 * Only a chunk whose digest differs is recomputed with the reference, to report the inputs that
 * are wrong. So a check costs about one evaluation of the submission per input.
 *
 * Built two ways:
 *   -DREF  the reference digests from exact-c's er_sigmoid / er_tanh / er_exp:
 *          ref <fn> <out.digest> [threads]
 *   else   linked with a submission built under UBSan and ASan (abort on the first error):
 *          check <fn> <ref.digest> [threads] [max_chunks] [seed] [lo hi]
 *          max_chunks limits a quick check to a random subset of chunks (seeded); 0 means all.
 *          lo hi (0 <= lo < hi <= 4096) check exactly chunks lo..hi-1, in order: one shard of a
 *          full check split across jobs. max_chunks and seed are then ignored.
 * Output: one JSON line on stdout. Exit 0 when every checked word matches, 1 on a wrong output,
 * 2 on a usage or input error. A sanitizer report aborts with the sanitizer's exit code. */
#define _POSIX_C_SOURCE 200809L
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "exact.h"

#define CHUNK_BITS 20
#define CHUNKS (1u << (32 - CHUNK_BITS))
#define CHUNK (1u << CHUNK_BITS)

#ifndef REF
uint32_t eik_sigmoid(uint32_t x);
uint32_t eik_tanh(uint32_t x);
uint32_t eik_exp(uint32_t x);
#endif

typedef uint32_t (*fn_t)(uint32_t);

/* The functions, in eik/config.py's FUNCTIONS order. */
static const char *const names[] = {"sigmoid", "tanh", "exp"};
static const fn_t refs[] = {er_sigmoid, er_tanh, er_exp};
#ifndef REF
static const fn_t subs[] = {eik_sigmoid, eik_tanh, eik_exp};
#endif
#define N_FUNCTIONS (sizeof names / sizeof names[0])

static fn_t ref_f, sub_f;
static uint8_t (*digest)[32];
static uint32_t order[CHUNKS], n_order;
static atomic_uint next_job;
static atomic_ullong words_done, n_bad;
static atomic_int stop;
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
static uint32_t examples[8][3];
static int n_examples;

static void *work(void *arg)
{
    (void)arg;
    uint32_t *out = malloc(sizeof(uint32_t) * CHUNK);
    for (;;) {
        unsigned j = atomic_fetch_add(&next_job, 1);
        if (j >= n_order || atomic_load(&stop))
            break;
        uint32_t c = order[j], base = c << CHUNK_BITS;
#ifdef REF
        for (uint32_t i = 0; i < CHUNK; i++)
            out[i] = ref_f(base + i);
        er_sha256(out, sizeof(uint32_t) * CHUNK, digest[c]);
#else
        for (uint32_t i = 0; i < CHUNK; i++)
            out[i] = sub_f(base + i);
        uint8_t h[32];
        er_sha256(out, sizeof(uint32_t) * CHUNK, h);
        if (memcmp(h, digest[c], 32) != 0) {
            for (uint32_t i = 0; i < CHUNK; i++) {
                uint32_t want = ref_f(base + i);
                if (out[i] != want) {
                    atomic_fetch_add(&n_bad, 1);
                    pthread_mutex_lock(&lock);
                    if (n_examples < 8)
                        examples[n_examples][0] = base + i, examples[n_examples][1] = out[i],
                        examples[n_examples++][2] = want;
                    pthread_mutex_unlock(&lock);
                }
            }
            atomic_store(&stop, 1); /* fail fast: one bad chunk rejects the entry */
        }
#endif
        atomic_fetch_add(&words_done, CHUNK);
    }
    free(out);
    return NULL;
}

int main(int argc, char **argv)
{
    if (argc < 3 || argc == 7 || argc > 8) {
        fprintf(stderr, "usage: %s sigmoid|tanh|exp <digest file> [threads] [max_chunks] [seed] [lo hi]\n", argv[0]);
        return 2;
    }
    size_t k = 0;
    while (k < N_FUNCTIONS && strcmp(argv[1], names[k]) != 0)
        k++;
    if (k == N_FUNCTIONS) { /* never a default: an unknown name must not check another function */
        fprintf(stderr, "unknown function %s (sigmoid, tanh or exp)\n", argv[1]);
        return 2;
    }
    ref_f = refs[k];
#ifndef REF
    sub_f = subs[k];
#endif
    int threads = argc > 3 ? atoi(argv[3]) : 8;
    unsigned max_chunks = argc > 4 ? (unsigned)atoi(argv[4]) : 0;
    unsigned long long seed = argc > 5 ? strtoull(argv[5], NULL, 10) : 1;
    if (threads < 1 || threads > 256)
        threads = 8;
    digest = calloc(CHUNKS, 32);

    /* chunk order: a seeded shuffle, so a quick check samples and a failing full check stops early */
    for (uint32_t i = 0; i < CHUNKS; i++)
        order[i] = i;
    for (uint32_t i = CHUNKS - 1; i > 0; i--) {
        seed = seed * 6364136223846793005ull + 1442695040888963407ull;
        uint32_t k = (uint32_t)(seed >> 33) % (i + 1), t = order[i];
        order[i] = order[k], order[k] = t;
    }
    n_order = max_chunks && max_chunks < CHUNKS ? max_chunks : CHUNKS;
    unsigned long lo = 0, hi = CHUNKS;
    if (argc == 8) { /* one shard: chunks lo..hi-1 in order */
        char *e1, *e2;
        lo = strtoul(argv[6], &e1, 10), hi = strtoul(argv[7], &e2, 10);
        if (*e1 || *e2 || lo >= hi || hi > CHUNKS) {
            fprintf(stderr, "bad chunk range %s %s (0 <= lo < hi <= %u)\n", argv[6], argv[7], CHUNKS);
            return 2;
        }
        for (uint32_t i = 0; i < hi - lo; i++)
            order[i] = (uint32_t)(lo + i);
        n_order = (uint32_t)(hi - lo);
    }

#ifndef REF
    FILE *f = fopen(argv[2], "rb");
    if (!f || fread(digest, 32, CHUNKS, f) != CHUNKS) {
        fprintf(stderr, "cannot read %s\n", argv[2]);
        return 2;
    }
    fclose(f);
#endif
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    pthread_t th[256];
    for (int i = 0; i < threads; i++)
        pthread_create(&th[i], NULL, work, NULL);
    for (int i = 0; i < threads; i++)
        pthread_join(th[i], NULL);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double secs = (double)(t1.tv_sec - t0.tv_sec) + 1e-9 * (double)(t1.tv_nsec - t0.tv_nsec);

#ifdef REF
    FILE *o = fopen(argv[2], "wb");
    if (!o || fwrite(digest, 32, CHUNKS, o) != CHUNKS)
        return 2;
    fclose(o);
    printf("{\"fn\":\"%s\",\"reference_digests\":\"%s\",\"words\":%llu,\"seconds\":%.1f}\n", argv[1], argv[2],
           (unsigned long long)atomic_load(&words_done), secs);
    return 0;
#else
    unsigned long long bad = atomic_load(&n_bad), done = atomic_load(&words_done);
    int all_in_order = done == (unsigned long long)n_order * CHUNK && !bad;
    if (argc != 8 && n_order != CHUNKS)
        all_in_order = 0; /* a quick check samples chunks; it completes no range */
    printf("{\"fn\":\"%s\",\"complete\":%s,\"range_complete\":%s,\"chunk_lo\":%lu,\"chunk_hi\":%lu,"
           "\"words_checked\":%llu,\"mismatches\":%llu,\"seconds\":%.1f,\"examples\":[",
           argv[1], n_order == CHUNKS && all_in_order ? "true" : "false", all_in_order ? "true" : "false",
           argc == 8 ? lo : 0, argc == 8 ? hi : (unsigned long)CHUNKS, done, bad, secs);
    for (int i = 0; i < n_examples; i++)
        printf("%s[\"%08x\",\"%08x\",\"%08x\"]", i ? "," : "", examples[i][0], examples[i][1], examples[i][2]);
    printf("]}\n");
    return bad != 0;
#endif
}
