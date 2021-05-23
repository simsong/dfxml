/* -*- mode: C++; c-basic-offset: 4; indent-tabs-mode: nil -*- */
/**
 * implementation for C++ XML generation class
 *
 * The software provided here is released by the Naval Postgraduate
 * School, an agency of the U.S. Department of Navy.  The software
 * bears no warranty, either expressed or implied. NPS does not assume
 * legal liability nor responsibility for a User's use of the software
 * or the results of such use.
 *
 * Please note that within the United States, copyright protection,
 * under Section 105 of the United States Code, Title 17, is not
 * available for any work of the United States Government and/or for
 * any works created by United States Government employees. User
 * acknowledges that this software contains work which was created by
 * NPS government employees and is therefore in the public domain and
 * not subject to copyright.
 */


#include "config.h"
#include "dfxml_writer.h"

#include <sys/param.h>
#include <sys/time.h>
#include <unistd.h>
#include <fcntl.h>

#include <cassert>
#include <cerrno>
#include <cstdarg>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <iostream>
#include <stack>
#include <streambuf>


#include "dfxml_writer.h"
#include "cpuid.h"



#if (!defined(HAVE_VASPRINTF)) || defined(_WIN32)
#ifndef _WIN32
#define ms_printf __print
#define __MINGW_ATTRIB_NONNULL(x)
#endif
extern "C" {
    /**
     * We do not have vasprintf.
     * We have determined that vsnprintf() does not perform properly on windows.
     * So we just allocate a huge buffer and then strdup() and hope!
     */
    int vasprintf(char **ret,const char *fmt,va_list ap)
        __attribute__((__format__(ms_printf, 2, 0)))
        __MINGW_ATTRIB_NONNULL(2) ;
    int vasprintf(char **ret,const char *fmt,va_list ap)
    {
        /* Figure out how long the result will be */
        char buf[65536];
        int size = vsnprintf(buf,sizeof(buf),fmt,ap);
        if(size<0) return size;
        /* Now allocate the memory */
        *ret = strcpy((char *) malloc(strlen(buf)+1), buf);
        return size;
    }
}
#endif
