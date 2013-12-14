#!/usr/bin/env python3

"""
make_differential_dfxml.py

Takes two DFXML files as input.
Produces a differential DFXML file as output.

This program's main purpose is matching files correctly.  It only performs enough analysis to determine that a fileobject has changed at all.  (This is half of the work done by idifference.py.)
"""

__version__ = "0.5.0"

import Objects
import logging
import xml.etree.ElementTree as ET
import os
import sys
import collections
import dfxml

_logger = logging.getLogger(os.path.basename(__file__))

def ignorable_name(fn):
    """Filter out recognized pseudo-file names."""
    if fn is None:
        return False
    return os.path.basename(fn) in [".", "..", "$FAT1", "$FAT2", "$OrphanFiles"]

def make_differential_dfxml(pre, post, diff_mode="all", retain_unchanged=False, ignore_properties=set()):
    """
    Takes as input two paths to DFXML files.  Returns a DFXMLObject.
    @param pre String.
    @param post String.
    @param diff_mode Optional.  One of "all" or "idifference".
    @param retain_unchanged Optional.  Boolean.
    @param ignore_properties Optiona.  Must be a Set.
    """

    _expected_diff_modes = ["all", "idifference"]
    if diff_mode not in _expected_diff_modes:
        raise ValueError("Differencing mode should be in: %r." % _expected_diff_modes)
    diff_mask_set = set()
    if diff_mode == "idifference":
        diff_mask_set |= set([
          "atime",
          "byte_runs"
          "crtime",
          "ctime",
          "filename",
          "filesize",
          "md5",
          "mtime",
          "sha1"
        ])
    diff_mask_set |= ignore_properties
    _logger.debug("diff_mask_set = " + repr(diff_mask_set))
        

    #d: The container DFXMLObject, ultimately returned.
    d = Objects.DFXMLObject(version="1.1.0")
    d.command_line = " ".join(sys.argv)
    d.add_namespace("delta", dfxml.XMLNS_DELTA)

    #The list most of this function is spent on building
    fileobjects_changed = []

    #Unmodified files; only retained if requested.
    fileobjects_unchanged = []

    #Key: (partition, inode, filename); value: FileObject
    old_fis = None
    new_fis = None

    #Key: (partition, inode, filename); value: FileObject list
    old_fis_unalloc = None
    new_fis_unalloc = None

    #Key: Partition byte offset within the disk image, paired with the file system type
    #Value: VolumeObject
    volumes = dict()
    #Populated in distinct (offset, file system type as string) encounter order
    volumes_encounter_order = dict()

    for infile in [pre, post]:

        _logger.debug("infile = %r" % infile)
        old_fis = new_fis
        new_fis = dict()

        old_fis_unalloc = new_fis_unalloc
        new_fis_unalloc = collections.defaultdict(list)

        d.sources.append(infile)

        for (i, (event, new_obj)) in enumerate(Objects.iterparse(infile)):
            if isinstance(new_obj, Objects.DFXMLObject):
                #Inherit desired properties from the source DFXMLObject.

                #Inherit namespaces
                for (prefix, url) in new_obj.iter_namespaces():
                    d.add_namespace(prefix, url)

                continue
            elif isinstance(new_obj, Objects.VolumeObject):
                if event == "end":
                    #This algorithm doesn't yet need to know when a volume is concluded.  On to the next object.
                    continue

                offset = new_obj.partition_offset
                if offset is None:
                    raise AttributeError("To perform differencing with volumes, the <volume> elements must have a <partition_offset>.  Either re-generate your DFXML with partition offsets, or run this program again with the --ignore-volumes flag.")
                ftype_str = new_obj.ftype_str
                if (offset, ftype_str) in volumes:
                    _logger.debug("Found a volume again, at offset %r." % offset)
                    if infile == pre:
                        _logger.debug("new_obj.partition_offset = %r." % offset)
                        _logger.warning("Encountered a volume that starts at an offset as another volume, in the same disk image.  This analysis is based on the assumption that that doesn't happen.  Check results that depend on partition mappings.")
                    else:
                        #New volume; compare
                        _logger.debug("Found a volume in post image, at offset %r." % offset)
                        old_obj = volumes[(offset, ftype_str)]
                        new_obj.original_volume = old_obj
                        new_obj.compare_to_original()
                        if len(new_obj.diffs) > 0:
                            new_obj.diffs.add("_modified")
                        volumes[(offset, ftype_str)] = new_obj
                else:
                    _logger.debug("Found a new volume, at offset %r." % offset)
                    new_obj.diffs.add("_new")
                    volumes[(offset, ftype_str)] = new_obj
                    volumes_encounter_order[(offset, new_obj.ftype_str)] = len(volumes)
                continue
            elif not isinstance(new_obj, Objects.FileObject):
                #The rest of this loop compares only file objects.
                continue

            if ignorable_name(new_obj.filename):
                continue

            #Normalize the partition number
            if new_obj.volume_object is None:
                new_obj.partition = None
            else:
                vo = new_obj.volume_object
                new_obj.partition = volumes_encounter_order[(vo.partition_offset, vo.ftype_str)]

            #Define the identity key of this file -- affected by the --ignore argument
            _key_partition = None if "partition" in ignore_properties else new_obj.partition
            _key_inode = None if "inode" in ignore_properties else new_obj.inode
            _key_filename = None if "filename" in ignore_properties else new_obj.filename
            key = (_key_partition, _key_inode, _key_filename)

            #Ignore unallocated content comparisons until a later loop.  The unique identification of deleted files needs a little more to work.
            if not new_obj.alloc:
                new_fis_unalloc[key].append(new_obj)
                continue

            #The rest of this loop is irrelevant until the second file.
            if old_fis is None:
                new_fis[key] = new_obj
                continue


            if key in old_fis:
                #Extract the old fileobject and check for changes
                old_obj = old_fis.pop(key)
                new_obj.original_fileobject = old_obj
                new_obj.compare_to_original()

                if len(new_obj.diffs - diff_mask_set) > 0:
                    _logger.debug("Remaining diffs: " + repr(new_obj.diffs - diff_mask_set))
                    fileobjects_changed.append(new_obj)
                else:
                    #Unmodified file; only keep if requested.
                    if retain_unchanged:
                        fileobjects_unchanged.append(new_obj)
            else:
                #Store the new object
                new_fis[key] = new_obj

        #The rest of the files loop is irrelevant until the second file.
        if old_fis is None:
            continue


        _logger.debug("len(old_fis) = %d" % len(old_fis))
        _logger.debug("len(new_fis) = %d" % len(new_fis))
        _logger.debug("len(fileobjects_changed) = %d" % len(fileobjects_changed))

        #Identify renames - only possible if 1-to-1.  Many-to-many renames are just left as new and deleted files.
        _logger.debug("Detecting renames...")
        fileobjects_renamed = []
        def _make_name_map(d):
            """Returns a dictionary, mapping (partition, inode) -> {filename}."""
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
            old_name = old_inode_names[key].pop()
            new_name = new_inode_names[key].pop()
            old_obj = old_fis.pop((partition, inode, old_name))
            new_obj = new_fis.pop((partition, inode, new_name))
            new_obj.original_fileobject = old_obj
            new_obj.compare_to_original()
            fileobjects_renamed.append(new_obj)
        _logger.debug("len(old_fis) -> %d" % len(old_fis))
        _logger.debug("len(new_fis) -> %d" % len(new_fis))
        _logger.debug("len(fileobjects_changed) -> %d" % len(fileobjects_changed))
        _logger.debug("len(fileobjects_renamed) = %d" % len(fileobjects_renamed))

        #Identify files that just changed inode number - basically, doing the rename detection again
        _logger.debug("Detecting inode number changes...")
        def _make_inode_map(d):
            """Returns a dictionary, mapping (partition, filename) -> inode."""
            retdict = dict()
            for (partition, inode, filename) in d.keys():
                if (partition, filename) in retdict:
                    _logger.warning("Multiple instances of the file path %r were found in partition %r; this violates an assumption of this program, that paths are unique within partitions." % (filename, partition))
                retdict[(partition, filename)] = inode
            return retdict
        old_name_inodes = _make_inode_map(old_fis)
        new_name_inodes = _make_inode_map(new_fis)
        for key in new_name_inodes.keys():
            if not key in old_name_inodes:
                continue
            (partition, name) = key
            old_obj = old_fis.pop((partition, old_name_inodes[key], name))
            new_obj = new_fis.pop((partition, new_name_inodes[key], name))
            new_obj.original_fileobject = old_obj
            new_obj.compare_to_original()
            fileobjects_changed.append(new_obj)
        _logger.debug("len(old_fis) -> %d" % len(old_fis))
        _logger.debug("len(new_fis) -> %d" % len(new_fis))
        _logger.debug("len(fileobjects_changed) -> %d" % len(fileobjects_changed))
        #And that's the end of the allocated-only, per-volume analysis.

        #We may be able to match files that aren't allocated against files we think are deleted
        _logger.debug("Detecting modifications from unallocated files...")
        fileobjects_deleted = []
        for key in new_fis_unalloc:
            #1 partition; 1 inode number; 1 name, repeated:  Too ambiguous to compare.
            if len(new_fis_unalloc[key]) != 1:
                continue

            if key in old_fis_unalloc:
                if len(old_fis_unalloc[key]) == 1:
                    #The file was unallocated in the previous image, too.
                    old_obj = old_fis_unalloc[key].pop()
                    new_obj = new_fis_unalloc[key].pop()
                    new_obj.original_fileobject = old_obj
                    new_obj.compare_to_original()
                    #The file might not have changed.  It's interesting if it did, though.
                    if len(new_obj.diffs - diff_mask_set) > 0:
                        _logger.debug("Remaining diffs: " + repr(new_obj.diffs - diff_mask_set))
                        fileobjects_changed.append(new_obj)
                    elif retain_unchanged:
                        fileobjects_unchanged.append(new_obj)
            elif key in old_fis:
                #Identified a deletion.
                old_obj = old_fis.pop(key)
                new_obj = new_fis_unalloc[key].pop()
                new_obj.original_fileobject = old_obj
                new_obj.compare_to_original()
                fileobjects_deleted.append(new_obj)
        _logger.debug("len(old_fis) -> %d" % len(old_fis))
        _logger.debug("len(new_fis) -> %d" % len(new_fis))
        _logger.debug("len(fileobjects_changed) -> %d" % len(fileobjects_changed))
        _logger.debug("len(fileobjects_deleted) -> %d" % len(fileobjects_deleted))

        #After deletion matching is performed, one might want to look for files migrating to other partitions.
        #However, since between-volume migration creates a new deleted file, this algorithm instead ignores partition migrations.
        #AJN TODO Thinking about it a little more, I can't suss out a reason against trying this match.  It's complicated if we try looking for reallocations in new_fis, strictly from new_fis_unalloc.

        #TODO We might also want to match the unallocated objects based on metadata addresses.  Unfortunately, that requires implementation of additional byte runs, which hasn't been fully designed yet in the DFXML schema.

        #Begin output.

        #Key: Partition number, or None
        #Value: Reference to the VolumeObject corresponding with that partition number.  None -> the DFXMLObject.
        appenders = dict()
        for (offset, ftype_str) in volumes_encounter_order:
            appenders[volumes_encounter_order[(offset, ftype_str)]] = volumes[(offset, ftype_str)]
        appenders[None] = d

        for (voffset, vftype_str) in sorted(volumes.keys()):
            d.append(volumes[(voffset, vftype_str)])

        #Populate DFXMLObject.
        for key in new_fis:
            #TODO If this script ever does a series of >2 DFXML files, these diff additions need to be removed for the next round.
            fi = new_fis[key]
            fi.diffs.add("_new")
            appenders[fi.partition].append(fi)
        for key in new_fis_unalloc:
            for fi in new_fis_unalloc[key]:
                fi.diffs.add("_new")
                appenders[fi.partition].append(fi)
        for fi in fileobjects_deleted:
            fi.diffs.add("_deleted")
            appenders[fi.partition].append(fi)
        for key in old_fis:
            ofi = old_fis[key]
            nfi = Objects.FileObject()
            nfi.original_fileobject = ofi
            nfi.diffs.add("_deleted")
            appenders[ofi.partition].append(nfi)
        for key in old_fis_unalloc:
            for ofi in old_fis_unalloc[key]:
                nfi = Objects.FileObject()
                nfi.original_fileobject = ofi
                nfi.diffs.add("_deleted")
                appenders[ofi.partition].append(nfi)
        for fi in fileobjects_renamed:
            fi.diffs.add("_renamed")
            appenders[fi.partition].append(fi)
        for fi in fileobjects_changed:
            content_diffs = set(["md5", "sha1", "mtime"])
            #Independently flag for content and metadata modifications
            if len(content_diffs.intersection(fi.diffs)) > 0:
                fi.diffs.add("_modified")
            if len(fi.diffs - content_diffs) > 0:
                fi.diffs.add("_changed")
            appenders[fi.partition].append(fi)
        for fi in fileobjects_unchanged:
            appenders[fi.partition].append(fi)

        #Output
        return d

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--idifference-diffs", action="store_true", help="Only consider the modifications idifference had considered (names, hashes, timestamps).")
    parser.add_argument("-i", "--ignore", action="append", help="Object property to ignore in all difference operations.  E.g. pass '-i inode' to ignore inode differences when comparing directory trees on the same file system.")
    parser.add_argument("--retain-unchanged", action="store_true", help="Output unchanged files in the resulting DFXML file.", default=False)
    parser.add_argument("infiles", nargs="+")
    args = parser.parse_args()

    #TODO Allow --ignore to ignore ftype_str, to compare only file system offsets for partitions
    #TODO Add --ignore-volumes.  It should (probably) strip all volume information from each file.

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if len(args.infiles) != 2:
        raise ValueError("This script requires exactly two DFXML files as input.")

    pre = None
    post = None

    if len(args.infiles) > 2:
        raise NotImplementedError("This program only analyzes two files at the moment.")

    ignore_properties = set()
    if not args.ignore is None:
        for i in args.ignore:
            ignore_properties.add(i)

    for infile in args.infiles:
        pre = post
        post = infile
        if not pre is None:
            print(make_differential_dfxml(
              pre,
              post,
              diff_mode="idifference" if args.idifference_diffs else "all",
              retain_unchanged=args.retain_unchanged,
              ignore_properties=ignore_properties
            ).to_dfxml())
            
