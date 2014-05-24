/*
 * Revision History:
 * 2012 - Simson L. Garfinkel - Created for bulk_extractor.
 *
 * Test program for cpuid program.
 */

#include <stdint.h>
#include <stdio.h>
#include <limits.h>


#define cpuid(id) __asm__( "cpuid" : "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx) : "a"(id), "b"(0), "c"(0), "d"(0))
#define b(val, base, end) ((val << (__WORDSIZE-end-1)) >> (__WORDSIZE-end+base-1))

int main(int argc, char **argv)
{
        unsigned long eax, ebx, ecx, edx;

        cpuid(0);
        printf("identification: \"%.4s%.4s%.4s\"\n", (char *)&ebx, (char *)&edx, (char *)&ecx);

        printf("cpu information:\n");

        cpuid(1);
        printf(" family %ld model %ld stepping %ld efamily %ld emodel %ld\n",
                        b(eax, 8, 11), b(eax, 4, 7), b(eax, 0, 3), b(eax, 20, 27), b(eax, 16, 19));
        printf(" brand %ld cflush sz %ld*8 nproc %ld apicid %ld\n",
                        b(ebx, 0, 7), b(ebx, 8, 15), b(ebx, 16, 23), b(ebx, 24, 31));

        cpuid(0x80000006);
        printf("L1 cache size (per core): %ld KB\n", b(ecx, 16, 31));

        return(0);
}
