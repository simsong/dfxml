#
# mix-ins for be13
#

AC_MSG_NOTICE([Including dfxml_configure.m4 from dfxml])
AC_CHECK_HEADERS([afflib/afflib.h err.h expat.h exiv2/image.hpp libewf.h pwd.h sys/cdefs.h sys/mman.h sys/resource.h sys/utsname.h unistd.h openssl/hmac.h openssl/evp.h])
AC_CHECK_FUNCS([fork localtime_r getuid gethostname getwpuid getrusage mkstemp vasprintf regcomp ])

# Determine UTC date offset
CPPFLAGS="$CPPFLAGS -DUTC_OFFSET=`date +%z`"

# Get the GIT version
AC_CHECK_PROG([git],[git],[yes],[no])
AM_CONDITIONAL([FOUND_GIT],[test "x$git" = xyes])
AM_COND_IF([FOUND_GIT],
        [GIT_COMMIT=`git describe --dirty --always`
         CPPFLAGS="$CPPFLAGS -DGIT_COMMIT=$GIT_COMMIT "
         AC_MSG_NOTICE([git commit $GIT_COMMIT])],
        [AC_MSG_WARN([git not found])])


# Do we have the CPUID instruction?
AC_TRY_COMPILE([#define cpuid(id) __asm__( "cpuid" : "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx) : "a"(id), "b"(0), "c"(0), "d"(0))],
			[unsigned long eax, ebx, ecx, edx;cpuid(0);],
			have_cpuid=yes,
			have_cpuid=no)
if test "$have_cpuid" = yes; then
 AC_DEFINE(HAVE_ASM_CPUID, 1, [define to 1 if __asm__ CPUID is available])
fi

# Does GCC have the diagnostic pragma?
AC_TRY_COMPILE([#pragma GCC diagnostic ignored "-Wredundant-decls"],
    	       [],
	       AC_DEFINE([DFXML_GNUC_HAS_DIAGNOSTIC_PRAGMA],[1],[GCC supports #pragma GCC diagnostic]),
	       )

