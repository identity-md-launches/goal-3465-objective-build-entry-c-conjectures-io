/* The only header a submission sees. The build force-includes it (-include eik.h), and a
 * submission may not #include anything itself. It defines fixed-width integer types identically
 * on every target (RV32IM, Thumb, and the x86-64 host used for the full check), declares the three
 * memory functions the harness provides, and declares the entry points the submission defines.
 * There is no float type anywhere in the translation unit. */
#ifndef EIK_H
#define EIK_H

typedef signed char int8_t;
typedef unsigned char uint8_t;
typedef short int16_t;
typedef unsigned short uint16_t;
typedef int int32_t;
typedef unsigned int uint32_t;
typedef long long int64_t;
typedef unsigned long long uint64_t;
typedef __SIZE_TYPE__ size_t;
typedef _Bool bool;

#define true 1
#define false 0
#define NULL ((void *)0)
#define INT32_C(c) c
#define UINT32_C(c) c##u
#define INT64_C(c) c##ll
#define UINT64_C(c) c##ull
#define INT32_MAX 0x7fffffff
#define UINT32_MAX 0xffffffffu
#define INT64_MAX 0x7fffffffffffffffll
#define UINT64_MAX 0xffffffffffffffffull

void *memcpy(void *dst, const void *src, size_t n);
void *memmove(void *dst, const void *src, size_t n);
void *memset(void *dst, int c, size_t n);

/* Entry points: binary32 word in, binary32 word out. They must equal the specification
 * (sigmoidCR, tanhCR in ExactToolkit/Activation.lean; expW in ContractExact.lean, FloatLib's
 * CorrectlyRounded.exp) on all 2^32 inputs. */
uint32_t eik_sigmoid(uint32_t x);
uint32_t eik_tanh(uint32_t x);
uint32_t eik_exp(uint32_t x);

#endif
