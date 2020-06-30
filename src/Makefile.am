# (C) 2020 Simson L. Garfinkel
# https://www.gnu.org/licenses/lgpl-3.0.en.html

SUBDIRS = tests

bin_PROGRAMS = dfxml_demo iblkfind
dfxml_demo_SOURCES = dfxml_demo.cpp dfxml_reader.cpp dfxml_reader.h 
iblkfind_SOURCES = iblkfind.cpp dfxml_reader.cpp dfxml_reader.h 
EXTRA_DIST = \
	beregex.cpp \
	beregex.h \
	cppmutex.h \
	cpu_info.c \
	cpu_stat.cpp \
	dfxml_generator.cpp \
	dfxml_generator.h \
	dfxml_reader.cpp \
	dfxml_reader.h


# https://stackoverflow.com/questions/15013672/use-autotools-with-readme-md
# We provide README.md instead of README. This prevents autotools from complaining.
README: README.md
