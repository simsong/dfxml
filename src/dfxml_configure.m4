#
# mix-ins for be13
#

AC_MSG_NOTICE([Including be13_configure.m4 from be13_api])
AC_CHECK_HEADERS([err.h pwd.h sys/cdefs.h sys/mman.h sys/resource.h sys/utsname.h unistd.h])
AC_CHECK_FUNCS([ishexnumber unistd.h mmap err errx warn warnx pread64 pread _lseeki64 ])

