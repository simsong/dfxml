// https://stackoverflow.com/questions/1666093/cpuid-implementations-in-c
#ifndef CPUID_H
#define CPUID_H

#include <cstdint>
#include <string>

class CPUID {
    uint32_t regs[4];

public:
    static std::string vendor();        // get CPU vendor
    explicit CPUID(unsigned i);
    const uint32_t &EAX() const {return regs[0];}
    const uint32_t &EBX() const {return regs[1];}
    const uint32_t &ECX() const {return regs[2];}
    const uint32_t &EDX() const {return regs[3];}
};

#endif // CPUID_H
