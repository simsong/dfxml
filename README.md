# DFXML
Welcome to the Digital Forensics XML (DFXML) git repository.

DFXML is a file format designed to capture metadata and provenance information about the operation of software tools in a systematic fashion. The original motivation was to represent the output of digital forensics tools, and specifically the SleuthKit tools. DFXML was expanded to operate with the bulk_extractor digital forensics tool. DFXML was then expanded to cover the output of the tcpflow tool. With the lessons we learned form handling all of those programs, we were able to separate out use of DFXML for documenting runtime provenance of any program, and the use of DFXML to represent specific digital forensics artifacts like files and hash sets.

This repository contains original DFXML implements in C and Python for writing DFXML files, as well as an assortment of tools (mostly in Python) for reading and processing DFXML files.  The folder layout is as follows:

```
dtd/               - the DFXML DTD, somewhat out of date.
python/            - Python source files
python/dfxml/      - The Python DFXML module
python/dfxml/tests - Unit tests for the DFXML modules.
python/tools       - Tools written in Python for processing DFXML files.
python/tools/tests - Unit tests for the DFXML tools.
src/               - The C language DFXML implementation for both writing and reading DFXML files. Includes a few tools, mostly demos.
```

# Release Notes
- 2018-07-22 @simsong Significant redesign of the Python library.
  - Configure Python module with a module directory and moved most of `dfxml.py` to `__init__.py`.
  - Renamed `Objects.py` to be `objects.py` since Python3 naming conventions use only lower case filenames.
  - Moved tests to a `test/` subdirectory and redesigned most of them to work with py.test. The tests that require arguments on the python command line were not updated.
  - Removed calls to logging withing files and modules that are not tests, so that using DFXML doesn't inherently start emitting logging messages.
  - Removed calls to logging in Objects tests where the only thing that the test program was logging was the fact that it had run. py.test will provide similar logging now.
