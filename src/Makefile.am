# (C) 2020 Simson L. Garfinkel
# https://www.gnu.org/licenses/lgpl-3.0.en.html

DFXML_SRC_DIR =
include Makefile.defs

bin_PROGRAMS = dfxml_demo iblkfind
dfxml_demo_SOURCES = dfxml_demo.cpp cpuid.h $(DFXML_READER)
iblkfind_SOURCES = iblkfind.cpp $(DFXML_READER)
EXTRA_DIST = README.md 

check_PROGRAMS = testapp_catch2
TESTS = $(check_PROGRAMS)

testapp_catch2_SOURCES = testapp_catch2.cpp tests/catch.hpp $(DFXML_WRITER) $(DFXML_READER)

# https://stackoverflow.com/questions/15013672/use-autotools-with-readme-md
# We provide README.md instead of README. This prevents autotools from complaining.
README: README.md
