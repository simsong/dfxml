DFXML
=====
[![Build Status](https://travis-ci.com/simsong/dfxml.svg?branch=master)](https://travis-ci.com/simsong/dfxml)

Welcome to the Digital Forensics XML (DFXML) git repository.

DFXML is a file format designed to capture metadata and provenance information about the operation of software tools in a systematic fashion. The original motivation was to represent the output of digital forensics tools, and specifically the SleuthKit tools. DFXML was expanded to operate with the `bulk_extractor` digital forensics tool. DFXML was then expanded to cover the output of the `tcpflow` tool. With the lessons we learned form handling all of those programs, we were able to separate out use of DFXML for documenting runtime provenance of any program, and the use of DFXML to represent specific digital forensics artifacts like files and hash sets.

This repository contains original DFXML implements in C and Python for writing DFXML files, as well as an assortment of tools (mostly in Python) for reading and processing DFXML files.  The folder layout is as follows:

```
python/            - Python source files
python/dfxml/      - The Python DFXML module
python/dfxml/tests - Unit tests for the DFXML modules.
python/tools       - Tools written in Python for processing DFXML files.
python/tools/tests - Unit tests for the DFXML tools.
schema/            - The DFXML schema.  Not directly tracked; run `make schema-init` to retrieve.
src/               - The C language DFXML implementation for both writing and reading DFXML files. Includes a few tools, mostly demos.
```

Using this as a git submodule
=============================
Typically this DFXML module will be a submodule inside another git module.

We've noticed that people will typically start development in these modules, and then want to push the chages back to the master. This causes a problem with git, because when you've done the development, you weren't at the head. If this happens to you, you will need to create a new branch for your current location, then checkout the master branch, and then merge your branch into the master. You can do that this this sequence of git commands:

## Usage
Typically, this repository will be a submodule in another project. C++ projects will include the files in src/ in their program and manually write a DFXML file using the primitive XML writing tools that are included.
These tools are not guarenteed to create clean XML, but they can handle XML of any size.

Sometimes when working with DFXML as a submodule, you may get off the master and end up with a disconnected head. If so, use this to get back on the master:
```
$ git checkout -b newbranch
$ git checkout master
$ git merge newbranch
$ git branch -d newbranch
```

or, more succinctly:

```
$ git checkout -b tmp  ; git checkout master ; git merge tmp ; git branch -d tmp
```

### Usage with the DFXML Schema
The [DFXML schema](https://github.com/dfxml-working-group/dfxml_schema) is tracked here similarly to a Git submodule, but without using the Git submodule mechanism to avoid some operational deployment issues.  If you would like to check out the tracked schema version, run `make schema-init`.  It is only necessary to check this out if you are testing validation of DFXML content against the schema.

### Building dfxml as a shared library
To build dfxml as a shared library, run the following commands:

```bash
autoreconf -vif
automake
./configure
make
sudo make install
```

Note: If you are on a Linux machine ensure, that the packages specified in `src/requirements-ubuntu.txt` are installed. 

Release Notes
=============
- 2018-07-22 @simsong Significant redesign of the Python library.
  - Configure Python module with a module directory and moved most of `dfxml.py` to `__init__.py`.
  - Renamed `Objects.py` to be `objects.py` since Python3 naming conventions use only lower case filenames.
  - Moved tests to a `test/` subdirectory and redesigned most of them to work with py.test. The tests that require arguments on the python command line were not updated.
  - Removed calls to logging withing files and modules that are not tests, so that using DFXML doesn't inherently start emitting logging messages.
  - Removed calls to logging in Objects tests where the only thing that the test program was logging was the fact that it had run. py.test will provide similar logging now.


DFXML C++ STATUS REPORT
=======================
DFXML has been upgraded to C++17. This project still supports GNU
autotools, but may also support CMake in the future. This package will
remain as a git submodule, rather than a a stand-alone library is linked against.

--- Simson Garfinkel, May 6, 2021
