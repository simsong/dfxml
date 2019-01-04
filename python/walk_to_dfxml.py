#!/usr/bin/env python3

# This software was developed at the National Institute of Standards
# and Technology in whole or in part by employees of the Federal
# Government in the course of their official duties. Pursuant to
# title 17 Section 105 of the United States Code portions of this
# software authored by NIST employees are not subject to copyright
# protection and are in the public domain. For portions not authored
# by NIST employees, NIST has been granted unlimited rights. NIST
# assumes no responsibility whatsoever for its use by other parties,
# and makes no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

"""Walk current directory, writing DFXML to stdout."""

__version__ = "0.4.1"

import os
import stat
import hashlib
import traceback
import logging
import sys
import collections
import functools

_logger = logging.getLogger(os.path.basename(__file__))

import dfxml.objects as Objects

#Exclude md6 from hash list borrowed from Objects.py - hashlib doesn't support md6.
walk_default_hashes = Objects.FileObject._hash_properties - {"md6"}

def filepath_to_fileobject(filepath, **kwargs):
    """
    Optional arguments:
    * ignore_properties - dictionary of property names to exclude from FileObject.
    """
    global walk_default_hashes
    fobj = Objects.FileObject()

    ignore_properties = kwargs.get("ignore_properties", dict())
    #_logger.debug("ignore_properties = %r." % ignore_properties)

    #Determine type - done in three steps.
    if os.path.islink(filepath):
        name_type = "l"
    elif os.path.isdir(filepath):
        name_type = "d"
    elif os.path.isfile(filepath):
        name_type = "r"
    else:
        #Nop. Need to finish type determinations with stat structure.
        name_type = None

    # Retrieve stat struct for file to finish determining name type, and later to populate properties.
    if name_type == "l":
        sobj = os.lstat(filepath)
    else:
        sobj = os.stat(filepath)
    #_logger.debug(sobj)

    if name_type is None:
        if stat.S_ISCHR(sobj.st_mode):
            name_type = "c"
        elif stat.S_ISBLK(sobj.st_mode):
            name_type = "b"
        elif stat.S_ISFIFO(sobj.st_mode):
            name_type = "p"
        elif stat.S_ISSOCK(sobj.st_mode):
            name_type = "s"
        elif stat.S_ISWHT(sobj.st_mode):
            name_type = "w"
        else:
            raise NotImplementedError("No reporting check written for file type of %r." % filepath)

    _should_ignore = lambda x: Objects.FileObject._should_ignore_property(ignore_properties, name_type, x)

    if not _should_ignore("name_type"):
        fobj.name_type = name_type

    #Prime fileobjects from Stat data (lstat for soft links).
    fobj.populate_from_stat(sobj, ignore_properties=ignore_properties, name_type=name_type)

    #Hard-coded information: Name, and assumed allocation status.
    if not _should_ignore("filename"):
        fobj.filename = filepath
    if not _should_ignore("alloc"):
        fobj.alloc = True

    if not _should_ignore("link_target"):
        if name_type == "l":
            fobj.link_target = os.readlink(filepath)

    #Add hashes for (mostly regular) files.
    if name_type in ["-", "r", "v"]:
        # Check total OR
        if functools.reduce(
          lambda y, z: y or z,
          map(
            lambda x: not _should_ignore(x),
            walk_default_hashes
          )
        ):
            try:
                with open(filepath, "rb") as in_fh:
                    chunk_size = 2**22
                    md5obj = hashlib.md5()
                    sha1obj = hashlib.sha1()
                    sha224obj = hashlib.sha224()
                    sha256obj = hashlib.sha256()
                    sha384obj = hashlib.sha384()
                    sha512obj = hashlib.sha512()
                    any_error = False
                    while True:
                        buf = b""
                        try:
                            buf = in_fh.read(chunk_size)
                        except Exception as e:
                            any_error = True
                            if not _should_ignore("error"):
                                fobj.error = "".join(traceback.format_stack())
                                if e.args:
                                    fobj.error += "\n" + str(e.args)
                            buf = b""
                        if buf == b"":
                            break

                        if not _should_ignore("md5"):
                            md5obj.update(buf)
                        if not _should_ignore("sha1"):
                            sha1obj.update(buf)
                        if not _should_ignore("sha224"):
                            sha224obj.update(buf)
                        if not _should_ignore("sha256"):
                            sha256obj.update(buf)
                        if not _should_ignore("sha384"):
                            sha384obj.update(buf)
                        if not _should_ignore("sha512"):
                            sha512obj.update(buf)

                    if not any_error:
                        if not _should_ignore("md5"):
                            fobj.md5 = md5obj.hexdigest()
                        if not _should_ignore("sha1"):
                            fobj.sha1 = sha1obj.hexdigest()
                        if not _should_ignore("sha224"):
                            fobj.sha224 = sha224obj.hexdigest()
                        if not _should_ignore("sha256"):
                            fobj.sha256 = sha256obj.hexdigest()
                        if not _should_ignore("sha384"):
                            fobj.sha384 = sha384obj.hexdigest()
                        if not _should_ignore("sha512"):
                            fobj.sha512 = sha512obj.hexdigest()
            except Exception as e:
                if not _should_ignore("error"):
                    if fobj.error is None:
                        fobj.error = ""
                    else:
                        fobj.error += "\n"
                    fobj.error += "".join(traceback.format_stack())
                    if e.args:
                        fobj.error += "\n" + str(e.args)
    return fobj

def main():
    global walk_default_hashes
    #Determine whether we're going in threading mode or not.  (Some modules are not available by default.)
    using_threading = False
    if args.jobs > 1:
        using_threading = True  #(unless supporting modules are absent)
        try:
            import threading
        except:
            using_threading = False
            _logger.warning("Threading support not available.  Running in single thread only.")

        try:
            import queue
        except:
            using_threading = False
            _logger.warning("Python queue support not available.  (If running Ubuntu, this is in package python3-queuelib.)  Running in single thread only.")

    dobj = Objects.DFXMLObject(version="1.2.0")
    dobj.program = sys.argv[0]
    dobj.program_version = __version__
    dobj.command_line = " ".join(sys.argv)
    dobj.dc["type"] = "File system walk"
    dobj.add_creator_library("Python", ".".join(map(str, sys.version_info[0:3]))) #A bit of a bend, but gets the major version information out.
    dobj.add_creator_library("Objects.py", Objects.__version__)
    dobj.add_creator_library("dfxml.py", Objects.dfxml.__version__)

    # Key: property.
    # Value: set of name_types that should have the property ignored.  "*" indicates all.  No sets should be empty by the end of this setup.
    ignore_properties = collections.defaultdict(set)
    if args.ignore:
        for property_descriptor in args.ignore:
            property_descriptor_parts = property_descriptor.split("@")
            property_name = property_descriptor_parts[0]
            if len(property_descriptor_parts) == 1:
                ignore_properties[property_name].add("*")
            else:
                ignore_properties[property_name].add(property_descriptor_parts[-1])
    if args.ignore_hashes:
        for property_name in walk_default_hashes:
            ignore_properties[property_name].add("*")
    #_logger.debug("ignore_properties = %r." % ignore_properties)

    filepaths = set()
    filepaths.add(".")
    for (dirpath, dirnames, filenames) in os.walk("."):
        dirent_names = set()
        for dirname in dirnames:
            dirent_names.add(dirname)
        for filename in filenames:
            dirent_names.add(filename)
        for dirent_name in sorted(dirent_names):
            #The relpath wrapper removes "./" from the head of the path.
            filepath = os.path.relpath(os.path.join(dirpath, dirent_name))
            filepaths.add(filepath)

    fileobjects_by_filepath = dict()

    if using_threading:
        #Threading syntax c/o: https://docs.python.org/3.5/library/queue.html
        q = queue.Queue()
        threads = []

        def _worker():
            while True:
                filepath = q.get()
                if filepath is None:
                    break
                try:
                    fobj = filepath_to_fileobject(filepath, ignore_properties=ignore_properties)
                except FileNotFoundError as e:
                    fobj = Objects.FileObject()
                    fobj.filename = filepath
                    fobj.error = "".join(traceback.format_stack())
                    if e.args:
                        fobj.error += "\n" + str(e.args)
                fileobjects_by_filepath[filepath] = fobj
                q.task_done()

        for i in range(args.jobs):
            t = threading.Thread(target=_worker)
            t.start()
            threads.append(t)

        for filepath in filepaths:
            q.put(filepath)

        # block until all tasks are done
        q.join()

        # stop workers
        for i in range(args.jobs):
            q.put(None)
        for t in threads:
            t.join()
    else: #Not threading.
        for filepath in sorted(filepaths):
            fobj = filepath_to_fileobject(filepath, ignore_properties=ignore_properties)
            fileobjects_by_filepath[filepath] = fobj

    #Build output DFXML tree.
    for filepath in sorted(fileobjects_by_filepath.keys()):
        dobj.append(fileobjects_by_filepath[filepath])
    dobj.print_dfxml()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-i", "--ignore", action="append", help="Do not track named property on file objects.  E.g. '-i inode' will exclude inode numbers from DFXML manifest.  Can be given multiple times.  To exclude a fileobject property of a specific file type (e.g. regular, directory, device), supply the name_type value in addition; for example, to ignore mtime of a directory, '-i mtime@d'.")
    parser.add_argument("--ignore-hashes", action="store_true", help="Do not calculate any hashes.  Equivalent to passing -i for each of %s." % (", ".join(sorted(walk_default_hashes))))
    parser.add_argument("-j", "--jobs", type=int, default=1, help="Number of file-processing threads to run.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if args.jobs <= 0:
        raise ValueError("If requesting multiple jobs, please request 1 or more worker threads.")

    main()
