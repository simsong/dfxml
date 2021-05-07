#include "cpuid.h"


CPUID::CPUID(unsigned i)
{
#ifdef HAVE___CPUID
    __cpuid((int *)regs, (int)i);
#else
    asm volatile
      ("cpuid" : "=a" (regs[0]), "=b" (regs[1]), "=c" (regs[2]), "=d" (regs[3])
       : "a" (i), "c" (0));
    // ECX is set to zero for CPUID function 4
#endif
}

std::string CPUID::vendor()
{
    CPUID  cpuID(0);                     // get CPU vendor
    std::string vendor;
    vendor += std::string((const char *)&cpuID.EBX(), 4);
    vendor += std::string((const char *)&cpuID.EDX(), 4);
    vendor += std::string((const char *)&cpuID.ECX(), 4);
    return vendor;
}

