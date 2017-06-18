#!/usr/bin/env python3

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

"""Walk current directory, writing DFXML to stdout."""

__version__ = "0.2.1"

import os
import stat
import hashlib
import traceback
import logging
import sys

_logger = logging.getLogger(os.path.basename(__file__))

import Objects

def filepath_to_fileobject(filepath):
    fobj = Objects.FileObject()

    #Determine type - done in three steps.
    if os.path.islink(filepath):
        fobj.name_type = "l"
    elif os.path.isdir(filepath):
        fobj.name_type = "d"
    elif os.path.isfile(filepath):
        fobj.name_type = "r"
    else:
        #Need to finish type determinations with stat structure.
        pass

    #Prime fileobjects from Stat data (lstat for soft links).
    if fobj.name_type == "l":
        sobj = os.lstat(filepath)
    else:
        sobj = os.stat(filepath)
    #_logger.debug(sobj)
    fobj.populate_from_stat(sobj)

    if fobj.name_type is None:
        if stat.S_ISCHR(fobj.mode):
            fobj.name_type = "c"
        elif stat.S_ISBLK(fobj.mode):
            fobj.name_type = "b"
        elif stat.S_ISFIFO(fobj.mode):
            fobj.name_type = "p"
        elif stat.S_ISSOCK(fobj.mode):
            fobj.name_type = "s"
        elif stat.S_ISWHT(fobj.mode):
            fobj.name_type = "w"
        else:
            raise NotImplementedError("No reporting check written for file type of %r." % filepath)

    #Hard-coded information: Name, and assumed allocation status.
    fobj.filename = filepath
    fobj.alloc = True

    if fobj.name_type == "l":
        fobj.link_target = os.readlink(filepath)

    #Add hashes for regular files.
    if fobj.name_type == "r":
        try:
            with open(filepath, "rb") as in_fh:
                chunk_size = 2**22
                md5obj = hashlib.md5()
                sha1obj = hashlib.sha1()
                any_error = False
                while True:
                    buf = b""
                    try:
                        buf = in_fh.read(chunk_size)
                    except Exception as e:
                        any_error = True
                        fobj.error = "".join(traceback.format_stack())
                        if e.args:
                            fobj.error += "\n" + str(e.args)
                        buf = b""
                    if buf == b"":
                        break

                    md5obj.update(buf)
                    sha1obj.update(buf)

                if not any_error:
                    fobj.md5 = md5obj.hexdigest()
                    fobj.sha1 = sha1obj.hexdigest()
        except Exception as e:
            if fobj.error is None:
                fobj.error = ""
            else:
                fobj.error += "\n"
            fobj.error += "".join(traceback.format_stack())
            if e.args:
                fobj.error += "\n" + str(e.args)
    return fobj

def main():
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

    dobj = Objects.DFXMLObject(version="1.1.1")
    dobj.program = sys.argv[0]
    dobj.program_version = __version__
    dobj.command_line = " ".join(sys.argv)
    dobj.dc["type"] = "File system walk"

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
                fobj = filepath_to_fileobject(filepath)
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
            fobj = filepath_to_fileobject(filepath)
            fileobjects_by_filepath[filepath] = fobj

    #Build output DFXML tree.
    for filepath in sorted(fileobjects_by_filepath.keys()):
        dobj.append(fileobjects_by_filepath[filepath])
    dobj.print_dfxml()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-j", "--jobs", type=int, default=1, help="Number of file-processing threads to run.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if args.jobs <= 0:
        raise ValueError("If requesting multiple jobs, please request 1 or more worker threads.")

    main()
