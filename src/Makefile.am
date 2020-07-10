# (C) 2020 Simson L. Garfinkel
# https://www.gnu.org/licenses/lgpl-3.0.en.html

bin_PROGRAMS = dfxml_demo iblkfind
dfxml_demo_SOURCES = dfxml_demo.cpp dfxml_reader.cpp dfxml_reader.h 
iblkfind_SOURCES = iblkfind.cpp dfxml_reader.cpp dfxml_reader.h 
<<<<<<< HEAD
EXTRA_DIST = README.md
=======
EXTRA_DIST = README.md 

>>>>>>> c1f0cf9cf288838e8e3e433d44af65d7444ccd6c

check_PROGRAMS = testapp_catch2 cpu_stat
TESTS = $(check_PROGRAMS) 

<<<<<<< HEAD

testapp_catch2_SOURCES = testapp_catch2.cpp tests/catch.hpp \
	dfxml_writer.h dfxml_writer.cpp \
	dfxml_reader.h dfxml_reader.cpp \
	hash_t.h 

cpu_stat_SOURCES = cpu_stat.cpp
=======
testapp_catch2_SOURCES = testapp_catch2.cpp tests/catch.hpp \
	cpuid.h \
	hash_t.h \
	dfxml_writer.h dfxml_writer.cpp \
	dfxml_reader.h dfxml_reader.cpp
>>>>>>> c1f0cf9cf288838e8e3e433d44af65d7444ccd6c

# https://stackoverflow.com/questions/15013672/use-autotools-with-readme-md
# We provide README.md instead of README. This prevents autotools from complaining.
README: README.md
