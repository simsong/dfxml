// https://stackoverflow.com/questions/1666093/cpuid-implementations-in-c
#ifndef CPUID_H
#define CPUID_H

#ifdef _WIN32
#include <limits.h>
#include <intrin.h>
typedef unsigned __int32  uint32_t;
#endif

#include <cstdint>
#include <string>

class CPUID {
    uint32_t regs[4];

public:
    explicit CPUID(unsigned i) {
#ifdef _WIN32
        __cpuid((int *)regs, (int)i);
#elif HAVE_ASM_CPUID
        asm volatile
            ("cpuid" : "=a" (regs[0]), "=b" (regs[1]), "=c" (regs[2]), "=d" (regs[3])
             : "a" (i), "c" (0));
        // ECX is set to zero for CPUID function 4
#else
        for(auto it:regs){
            it = 0xff;
        }
#endif
    }

    const uint32_t &EAX() const {return regs[0];}
    const uint32_t &EBX() const {return regs[1];}
    const uint32_t &ECX() const {return regs[2];}
    const uint32_t &EDX() const {return regs[3];}

    static std::string vendor() {
        CPUID  cpuID(0);                     // get CPU vendor
        std::string vendor;
        vendor += std::string((const char *)&cpuID.EBX(), 4);
        vendor += std::string((const char *)&cpuID.EDX(), 4);
        vendor += std::string((const char *)&cpuID.ECX(), 4);
        return vendor;
    }
};

#endif // CPUID_H
