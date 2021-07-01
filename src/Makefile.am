# (C) 2020 Simson L. Garfinkel
# https://www.gnu.org/licenses/lgpl-3.0.en.html

DFXML_SRC_DIR = 
ACLOCAL_AMFLAGS = -I m4

include Makefile.defs

# Build dfxml as a library
lib_LTLIBRARIES = libdfxml.la
libdfxml_la_SOURCES = $(DFXML_WRITER) $(DFXML_READER)
libdfxml_la_LDFLAGS = -version-info 0:0:0
include_HEADERS  = dfxml_reader.h dfxml_writer.h

# Build demo programs
bin_PROGRAMS = dfxml_demo iblkfind
dfxml_demo_SOURCES = dfxml_demo.cpp cpuid.h
dfxml_demo_LDADD = ./libdfxml.la

iblkfind_SOURCES = iblkfind.cpp
iblkfind_LDADD = ./libdfxml.la

EXTRA_DIST = README.md 

check_PROGRAMS = testapp_catch2
TESTS = $(check_PROGRAMS)

testapp_catch2_SOURCES = testapp_catch2.cpp tests/catch.hpp
testapp_catch2_LDADD = ./libdfxml.la

# https://stackoverflow.com/questions/15013672/use-autotools-with-readme-md
# We provide README.md instead of README. This prevents autotools from complaining.
README: README.md
