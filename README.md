# DFXML
Welcome to the Digital Forensics XML (DFXML) git repository.

DFXML is a file format designed to capture metadata and provenance information about the operation of software tools in a systematic fashion. The original motivation was to represent the output of digital forensics tools, and specifically the SleuthKit tools. DFXML was expanded to operate with the bulk_extractor digital forensics tool. DFXML was then expanded to cover the output of the tcpflow tool. With the lessons we learned form handling all of those programs, we were able to separate out use of DFXML for documenting runtime provenance of any program, and the use of DFXML to represent specific digital forensics artifacts like files and hash sets.

This repository contains original DFXML implements in C and Python for writing DFXML files, as well as an assortment of tools (mostly in Python) for reading and processing DFXML files.  The folder layout is as follows:

```
dtd/    - the DFXML DTD, somewhat out of date.
python/ - Python source files
python/dfxml/ - The Python DFXML module
python/tools  - Tools written in Python for processing DFXML files.
src/    - The C language DFXML implementation for both writing and reading DFXML files. Includes a few tools, mostly demos.
```

# Using this as a git submodule
Typically this DFXML module will be a submodule inside another git module.

We've noticed that people will typically start development in these modules, and then want to push the chages back to the master. This causes a problem with git, because when you've done the development, you weren't at the head. If this happens to you, you will need to create a new branch for your current location, then checkout the master branch, and then merge your branch into the master. You can do that this this sequence of git commands:

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
