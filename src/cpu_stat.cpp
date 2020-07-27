/*
 * Test program for cpustat instruction.
 *
 *
 * Based on cpustat.h -- Header for cpustat.cpp. Copyright (c) 2004 Brad Fish.
 */

#include <cstdio>
#include <vector>
#include <iostream>


#ifdef HAS_WINDOWS_H
#include <windows.h>

// missing Windows processor power information struct
typedef struct _PROCESSOR_POWER_INFORMATION {
    ULONG  Number;
    ULONG  MaxMhz;
    ULONG  CurrentMhz;
    ULONG  MhzLimit;
    ULONG  MaxIdleState;
    ULONG  CurrentIdleState;
} PROCESSOR_POWER_INFORMATION , *PPROCESSOR_POWER_INFORMATION;


extern "C" {
#include <powrprof.h>
}

int main (int argc, char *argv[])
{
    typedef std::vector<PROCESSOR_POWER_INFORMATION> PPIVector;

    SYSTEM_INFO sys_info;
    PPIVector ppis;
    SYSTEM_POWER_CAPABILITIES spc;

    // find out how many processors we have in the system
    GetSystemInfo(&sys_info);
    ppis.resize(sys_info.dwNumberOfProcessors);

    // get CPU stats
    if (CallNtPowerInformation(ProcessorInformation, NULL, 0, &ppis[0],
        sizeof(PROCESSOR_POWER_INFORMATION) * ppis.size()) != ERROR_SUCCESS)
    {
        perror("main: ");
        return -1;
    }

    // print out CPU stats
    for (PPIVector::iterator it = ppis.begin(); it != ppis.end(); ++it)
    {
        std::cout << "stats for CPU " << it->Number << ':' << std::endl;
        std::cout << "  maximum MHz: " << it->MaxMhz << std::endl;
        std::cout << "  current MHz: " << it->CurrentMhz << std::endl;
        std::cout << "  MHz limit: " << it->MhzLimit << std::endl;
        std::cout << "  maximum idle state: " << it->MaxIdleState << std::endl;
        std::cout << "  current idle state: " << it->CurrentIdleState <<
            std::endl;
    }

    // get system power settings
    if (!GetPwrCapabilities(&spc))
    {
        perror("main: ");
        return -2;
    }

    // print power settings
    std::cout << "system power capabilities:" << std::endl;
    std::cout << "  processor throttle: " <<
        (spc.ProcessorThrottle ? "enabled" : "disabled") << std::endl;
    std::cout << "  processor minimum throttle: " <<
        static_cast<int>(spc.ProcessorMinThrottle) << '%' << std::endl;
    std::cout << "  processor maximum throttle: " <<
        static_cast<int>(spc.ProcessorMaxThrottle) << '%' << std::endl;
    exit(0);
}
#else
int main(int argc,char **argv)
{
    std::cerr << "This program only runs under Windows." << std::endl;
    exit(0);
}
#endif
