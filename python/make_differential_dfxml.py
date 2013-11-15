#!/usr/bin/env python3

"""
make_differential_dfxml.py

Takes two DFXML files as input.
Produces a differential DFXML file as output.

This program's main purpose is matching files correctly.  It only performs enough analysis to determine that a fileobject has changed at all.  (This is half of the work done by idifference.py.)
"""

__version__ = "0.2.0"

import Objects
import logging
import xml.etree.ElementTree as ET
import sys
import collections
import dfxml

def make_differential_dfxml(pre, post):
    """
    Takes as input two paths to DFXML files.  Returns a DFXMLObject.
    @param pre String.
    @param post String.
    """

    fileobjects_changed = []

    #Key: (partition, inode, filename); value: FileObject
    old_fis = None
    new_fis = None

    d = Objects.DFXMLObject(version="1.1.0")
    d.add_namespace("delta", dfxml.XMLNS_DELTA)

    for infile in [pre, post]:

        logging.debug("infile = %r" % infile)
        old_fis = new_fis
        new_fis = dict()

        d.sources.append(infile)

        for (i, obj) in enumerate(Objects.objects_from_file(infile, dfxmlobject=d)):
            #logging.debug("%d. obj = %r" % (i, obj))
            if not isinstance(obj, Objects.FileObject):
                continue

            #Ignore unallocated content comparisons for now.  The unique identification needs a little more to work.
            if obj.alloc == False:
                continue

            key = (obj.partition, obj.inode, obj.filename)

            #The rest of this loop is irrelevant until the second file.
            if old_fis is None:
                new_fis[key] = obj
                continue

            #Extract the old fileobject and check for changes
            if key in old_fis:
                prior_obj = old_fis.pop(key)
                obj.original_fileobject = prior_obj
                obj.compare_to_original()
                #TODO the old idifference just checked a few fields.  Add flag logic for this more stringent check.
                if len(obj.diffs) > 0:
                    fileobjects_changed.append(obj)
                else:
                    #Reclaim memory
                    del obj
            else:
                new_fis[key] = obj

        #The rest of the files loop is irrelevant until the second file.
        if old_fis is None:
            continue

        #Identify renames - only possible if 1-to-1.  Many-to-many renames are just left as new and deleted files.
        fileobjects_renamed = []
        def _make_name_map(d):
            retdict = collections.defaultdict(lambda: set())
            for (partition, inode, filename) in d.keys():
                retdict[(partition, inode)].add(filename)
            return retdict
        old_inode_names = _make_name_map(old_fis)
        new_inode_names = _make_name_map(new_fis)
        for key in new_inode_names.keys():
            if len(new_inode_names[key]) != 1:
                continue
            if not key in old_inode_names:
                continue
            if len(old_inode_names[key]) != 1:
                continue
            (partition, inode) = key
            old_obj = old_fis.pop((partition, inode, old_inode_names[key][0]))
            new_obj = new_fis.pop((partition, inode, new_inode_names[key][0]))
            new_obj.original_fileobject = old_obj
            new_obj.compare_to_original()
            fileobjects_renamed.append(new_obj)

        #TODO Identify files that just changed inode number - basically, doing the rename detection again, though it'll be simpler.

        #TODO Group outputs by volume

        #Populate DFXMLObject.
        for key in new_fis:
            #TODO If this script ever does a series of >2 DFXML files, these diff additions need to be removed for the next round.
            fi = new_fis[key]
            fi.diffs.add("_new")
            d.append(fi)
        for key in old_fis:
            fi = old_fis[key]
            fi.diffs.add("_deleted")
            d.append(fi)
        for fi in fileobjects_renamed:
            fi.diffs.add("_renamed")
            d.append(fi)
        for fi in fileobjects_changed:
            if len(set(["md5", "sha1", "ctime", "mtime"]).intersection(fi.diffs)) > 0:
                fi.diffs.add("_modified")
            else:
                fi.diffs.add("_changed")
            d.append(fi)

        #Output
        return d

def main():
    global args

    pre = None
    post = None

    if len(args.infiles) > 2:
        raise NotImplementedError("This program only analyzes two files at the moment.")

    for infile in args.infiles:
        pre = post
        post = infile
        if not pre is None:
            print(make_differential_dfxml(pre, post).to_dfxml())
            
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("infiles", nargs="+")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if len(args.infiles) != 2:
        raise ValueError("This script requires exactly two DFXML files as input.")

    main()
