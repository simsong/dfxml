#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.
# Order is largely irrelevant, although it must start with AC_INIT and end with AC_OUTPUT
# See http://autotoolset.sourceforge.net/tutorial.html
# and http://www.openismus.com/documents/linux/automake/automake.shtml

#
# This file is public domain
#

AC_PREREQ([2.69])
AC_INIT([DFXML],[1.0.1],[bugs@digitalcorpora.org])
AC_CONFIG_MACRO_DIR(m4)
m4_include([m4/ax_cxx_compile_stdcxx.m4])

AC_CONFIG_FILES([Makefile])
AC_CONFIG_HEADERS([config.h])
AM_INIT_AUTOMAKE
AM_MAINTAINER_MODE

# Initialize libtool support
LT_PREREQ([2.4.6])
LT_INIT([shared])
LT_LANG([C++])

# Programs we will be using
AC_PROG_CC
AC_PROG_CXX
AM_PROG_CC_C_O                    dnl allow per-produce flags
AC_PROG_INSTALL

# Must use C++17 mode. (mandatory)

AC_LANG_PUSH(C++)
AX_CXX_COMPILE_STDCXX([17], [noext], [mandatory])
AC_LANG_POP()

m4_include([dfxml_configure.m4])


################################################################
## Expat
## Required for S3 and Digital Signatures
##
AC_ARG_WITH(expat,
  AS_HELP_STRING([--with-expat=PATH], [where libexpat is compiled (if it isn't installed); required for S3 and Digital Signatures]),
  [LDFLAGS="-L${with_expat} $LDFLAGS" ;
   CPPFLAGS="-I${with_expat}/lib $CPPFLAGS"])

have_expat=yes
AC_CHECK_HEADER([expat.h])
AC_CHECK_LIB([expat],[XML_ParserCreate],,[have_expat="no ";AC_MSG_WARN([expat not found; S3 and Digital Signatures not enabled])])

################################################################
#
# Enable all the compiler debugging we can find
#
# This is originally from PhotoRec, but modified substantially by Simson
# Figure out which flags we can use with the compiler.
#
# These I don't like:
# -Wdeclaration-after-statement -Wconversion
# doesn't work: -Wunreachable-code
# causes configure to crash on gcc-4.2.1: -Wsign-compare-Winline
# causes warnings with unistd.h:  -Wnested-externs
# Just causes too much annoyance: -Wmissing-format-attribute

# Check GCC
GCC_WARNINGS_TO_TEST="-MD -Wpointer-arith -Wmissing-declarations -Wmissing-prototypes \
    -Wshadow -Wwrite-strings -Wcast-align -Waggregate-return \
    -Wbad-function-cast -Wcast-qual -Wundef -Wredundant-decls -Wdisabled-optimization \
    -Wfloat-equal -Wmultichar -Wc++-compat -Wmissing-noreturn -Wno-deprecated-declarations \
    -Wno-unknown-warning-option"

if test x"${mingw}" != "xyes" ; then
  # add the warnings we do not want to do on mingw
  GCC_WARNINGS_TO_TEST="$GCC_WARNINGS_TO_TEST -Wall -Wstrict-prototypes"
fi

echo "Warnings to test: $GCC_WARNINGS_TO_TEST"

for option in $GCC_WARNINGS_TO_TEST
do
  SAVE_CFLAGS="$CFLAGS"
  CFLAGS="$CFLAGS $option"
  AC_MSG_CHECKING([whether gcc understands $option])
  AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[]], [[]])],
      [has_option=yes],
      [has_option=no; CFLAGS="$SAVE_CFLAGS"])
  AC_MSG_RESULT($has_option)
  unset has_option
  unset SAVE_CFLAGS
  if test $option = "-Wmissing-format-attribute" ; then
    AC_DEFINE(HAVE_MISSING_FORMAT_ATTRIBUTE_WARNING,1,
		[Indicates that we have the -Wmissing-format-attribute G++ warning])
  fi
done
unset option


# Check G++
# We don't use these warnings:
# -Waggregate-return -- aggregate returns are GOOD; they simplify code design
# We can use these warnings after ZLIB gets upgraded:
# -Wundef  --- causes problems with zlib
# -Wcast-qual
# -Wmissing-format-attribute  --- Just too annoying
# 2020-06-04 removed ‘-Wno-unknown-warning-option’
AC_LANG_PUSH(C++)

CXX_WARNINGS_TO_TEST="-Wall -MD -Wpointer-arith \
    -Wshadow -Wwrite-strings -Wcast-align  \
    -Wredundant-decls -Wdisabled-optimization \
    -Wfloat-equal -Wmultichar -Wmissing-noreturn \
    -Wstrict-null-sentinel -Woverloaded-virtual -Wsign-promo \
    -Wno-deprecated-declarations \
    -funit-at-a-time"

if test x"${mingw}" != "xyes" ; then
  # add the warnings we don't want to do on mingw
  CXX_WARNINGS_TO_TEST="$CXX_WARNINGS_TO_TEST  -Weffc++"
fi

echo "Warnings to test: $CXX_WARNINGS_TO_TEST"

for option in $CXX_WARNINGS_TO_TEST
do
  SAVE_CXXFLAGS="$CXXFLAGS"
  CXXFLAGS="$CXXFLAGS $option"
  AC_MSG_CHECKING([whether g++ understands $option])
  AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[]], [[]])],
      [has_option=yes],
      [has_option=no; CXXFLAGS="$SAVE_CXXFLAGS"])
  AC_MSG_RESULT($has_option)
  unset has_option
  unset SAVE_CXXFLAGS
done
unset option

AC_LANG_POP()

################################################################
# Specify our other headers
#
# Autoupdate added the next two lines to ensure that your configure
# script's behavior did not change.  They are probably safe to remove.
AC_CHECK_INCLUDES_DEFAULT
AC_PROG_EGREP



################################################################
## os-specific fixups
# AC_CANONICAL_HOST is needed to access the 'host_os' variable
AC_CANONICAL_HOST
case "${host_os}" in
    linux*)
        ;;
    cygwin*|mingw*)
        ;;
    darwin*)
      CXXFLAGS="-Wno-unknown-warning-option $CXXFLAGS"
        ;;
    *)
        ;;
esac


############## drop optimization flags if requested ################
AC_ARG_WITH(no_optimize, AS_HELP_STRING([--with-no_optimize],[Drop -O C flags]))
if test x"${NO_OPTIMIZE}" != "x" ; then
   with_no_optimize="yes";
fi

if test "${with_no_optimize}" = "yes" ; then
  CFLAGS=`echo "$CFLAGS" | sed s/-O[[0-9]]//`             # note the double quoting!
  CXXFLAGS=`echo "$CXXFLAGS" | sed s/-O[[0-9]]//`
fi

AC_OUTPUT
