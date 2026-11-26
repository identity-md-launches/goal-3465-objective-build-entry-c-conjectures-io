/* Supplemental exhaustive word-dispatch proof, independent of the entry's arithmetic.
 * Build: gcc -std=c11 -O2 -Wall -Wextra -Werror dispatch-proof.c -o SCRATCH/dispatch-proof
 * Iterate every uint32 input.  The original cell's three nested predicates and
 * the early unsigned predicate must select the exact same set of words.
 */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>

int main(void)
{
    uint32_t w = 0;
    uint64_t covered = 0, selected = 0, mismatches = 0;
    do {
        unsigned old = ((int32_t)w < 0) && (w > 0xBF800000u)
                     && ((w - 1) <= (0xC0800000u - 1));
        unsigned added = ((w - 0xBF800001u) <= 0x00FFFFFFu);
        mismatches += old != added;
        selected += added;
        covered++;
        w++;
    } while (w != 0);
    printf("words=%" PRIu64 " selected=%" PRIu64 " mismatches=%" PRIu64 "\n",
           covered, selected, mismatches);
    return mismatches != 0 || covered != UINT64_C(4294967296)
        || selected != UINT64_C(16777216);
}
