/* The target-side full check. Linked with an entry's object file for one target (and guest.c, for
 * the memory functions) into a static Linux executable with no C library, run under QEMU user mode:
 *
 *   qemu-riscv32 check.elf <fn> <lo> <hi>        fn: 0 sigmoid, 1 tanh, 2 exp (eik/config.py order)
 *   qemu-arm     check.elf <fn> <lo> <hi>        Thumb code; QEMU runs it on an A-profile CPU
 *
 * It writes the outputs for chunks lo..hi-1 (2^20 words each, inputs in increasing order) to stdout
 * as little-endian words. The host hashes each chunk and compares it with the reference digest, as
 * harness/check.c does on the host. So the code checked is the target object code the emulator
 * scored, byte for byte, not a recompilation.
 *
 * ARMv6-M (Cortex-M0+) and ARMv7E-M (Cortex-M4) instructions are subsets of ARMv7-A Thumb with the
 * same results, so running them on QEMU's A-profile CPU computes what the M-profile core computes.
 * Exit status: 0 done, 2 bad arguments. */
#include "eik.h"

#define CHUNK_WORDS (1u << 20)
#define CHUNKS (1u << 12)

static uint32_t buf[CHUNK_WORDS];

#if defined(__riscv)
#define SYS_WRITE 64
#define SYS_EXIT 93
static int32_t sys3(int32_t n, int32_t a, int32_t b, int32_t c)
{
    register int32_t a0 __asm__("a0") = a, a1 __asm__("a1") = b, a2 __asm__("a2") = c, a7 __asm__("a7") = n;
    __asm__ volatile("ecall" : "+r"(a0) : "r"(a1), "r"(a2), "r"(a7) : "memory");
    return a0;
}
__asm__(".globl _start\n_start:\n  mv a0, sp\n  call eik_cstart\n");
#elif defined(__arm__)
#define SYS_WRITE 4
#define SYS_EXIT 1
static int32_t sys3(int32_t n, int32_t a, int32_t b, int32_t c)
{
    register int32_t r0 __asm__("r0") = a, r1 __asm__("r1") = b, r2 __asm__("r2") = c, r7 __asm__("r7") = n;
    __asm__ volatile("svc 0" : "+r"(r0) : "r"(r1), "r"(r2), "r"(r7) : "memory");
    return r0;
}
__asm__(".globl _start\n.thumb_func\n_start:\n  mov r0, sp\n  bl eik_cstart\n");
#else
#error "target_check.c: unsupported target"
#endif

static __attribute__((noreturn)) void quit(int32_t code)
{
    for (;;)
        sys3(SYS_EXIT, code, 0, 0);
}

static int parse(const char *s, uint32_t *out)
{
    uint32_t v = 0;
    if (!s || !*s)
        return 0;
    for (; *s; s++) {
        if (*s < '0' || *s > '9' || v > 100000u)
            return 0;
        v = v * 10u + (uint32_t)(*s - '0');
    }
    *out = v;
    return 1;
}

static void put(const uint32_t *p, uint32_t bytes)
{
    const uint8_t *b = (const uint8_t *)p;
    while (bytes) {
        int32_t n = sys3(SYS_WRITE, 1, (int32_t)(size_t)b, (int32_t)bytes); /* size_t: 32 bits on every target */
        if (n <= 0)
            quit(3); /* the host stopped reading */
        b += n;
        bytes -= (uint32_t)n;
    }
}

__attribute__((noreturn, used)) void eik_cstart(uint32_t *sp)
{
    uint32_t argc = sp[0], fn, lo, hi;
    const char *const *argv = (const char *const *)(sp + 1);
    if (argc != 4 || !parse(argv[1], &fn) || !parse(argv[2], &lo) || !parse(argv[3], &hi) || fn > 2 || lo >= hi
        || hi > CHUNKS)
        quit(2);
    for (uint32_t c = lo; c < hi; c++) {
        uint32_t base = c << 20;
        if (fn == 0)
            for (uint32_t i = 0; i < CHUNK_WORDS; i++)
                buf[i] = eik_sigmoid(base + i);
        else if (fn == 1)
            for (uint32_t i = 0; i < CHUNK_WORDS; i++)
                buf[i] = eik_tanh(base + i);
        else
            for (uint32_t i = 0; i < CHUNK_WORDS; i++)
                buf[i] = eik_exp(base + i);
        put(buf, sizeof buf);
    }
    quit(0);
}
