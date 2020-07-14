# (C) 2020 Simson L. Garfinkel
# https://www.gnu.org/licenses/lgpl-3.0.en.html

bin_PROGRAMS = dfxml_demo iblkfind
dfxml_demo_SOURCES = dfxml_demo.cpp dfxml_reader.cpp dfxml_reader.h  cpuid.h cpuid.cpp
iblkfind_SOURCES = iblkfind.cpp dfxml_reader.cpp dfxml_reader.h 
EXTRA_DIST = README.md

check_PROGRAMS = testapp_catch2 cpu_stat
TESTS = $(check_PROGRAMS) 


testapp_catch2_SOURCES = testapp_catch2.cpp tests/catch.hpp \
	dfxml_writer.h dfxml_writer.cpp \
	dfxml_reader.h dfxml_reader.cpp \
	cpuid.h cpuid.cpp \
	hash_t.h 

cpu_stat_SOURCES = cpu_stat.cpp


# https://stackoverflow.com/questions/15013672/use-autotools-with-readme-md
# We provide README.md instead of README. This prevents autotools from complaining.
README: README.md
