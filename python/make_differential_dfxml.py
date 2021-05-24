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

"""
make_differential_dfxml.py

Takes two DFXML files as input.
Produces a differential DFXML file as output.

This program's main purpose is matching files correctly.  It only performs enough analysis to determine that a fileobject has changed at all.  (This is half of the work done by idifference.py.)
"""

__version__ = "0.12.1"

import dfxml.objects as Objects
import logging
import xml.etree.ElementTree as ET
import os
import sys
import collections
import dfxml

_logger = logging.getLogger(os.path.basename(__file__))

def _lower_ftype_str(vo):
    """The string labels of file system names might differ by something small like the casing.  Normalize the labels by lower-casing them."""
    Objects._typecheck(vo, Objects.VolumeObject)
    f = vo.ftype_str
    if isinstance(f, str): f = f.lower()
    return f

def ignorable_name(fn):
    """Filter out recognized pseudo-file names."""
    if fn is None:
        return False
    return os.path.basename(fn) in [".", "..", "$FAT1", "$FAT2", "$OrphanFiles"]

def make_differential_dfxml(pre, post, **kwargs):
    """
    Takes as input two paths to DFXML files.  Returns a DFXMLObject.
    @param pre String.
    @param post String.
    @param diff_mode Optional.  One of "all" or "idifference".
    @param retain_unchanged Optional.  Boolean.
    @param ignore_properties Optional.  Set.
    @param annotate_matches Optional.  Boolean.  True -> matched file objects get a "delta:matched='1'" attribute.
    @param rename_requires_hash Optional.  Boolean.  True -> all matches require matching SHA-1's, if present.
    @param ignore_filename_function Optional.  Function, string -> Boolean.  Returns True if a file name (which can be null) should be ignored.
    @param glom_byte_runs Optional.  Boolean.  Joins contiguous-region byte runs together in FileObject byte run lists.
    """

    diff_mode = kwargs.get("diff_mode", "all")
    retain_unchanged = kwargs.get("retain_unchanged", False)
    ignore_properties = kwargs.get("ignore_properties", set())
    annotate_matches = kwargs.get("annotate_matches", False)
    rename_requires_hash = kwargs.get("rename_requires_hash", False)
    ignore_filename_function = kwargs.get("ignore_filename_function", ignorable_name)
    glom_byte_runs = kwargs.get("glom_byte_runs", False)

    _expected_diff_modes = ["all", "idifference"]
    if diff_mode not in _expected_diff_modes:
        raise ValueError("Differencing mode should be in: %r." % _expected_diff_modes)
    diff_mask_set = set()

    if diff_mode == "idifference":
        diff_mask_set |= set([
          "atime",
          "byte_runs",
          "crtime",
          "ctime",
          "filename",
          "filesize",
          "md5",
          "mtime",
          "sha1"
        ])
    _logger.debug("diff_mask_set = " + repr(diff_mask_set))

    #d: The container DFXMLObject, ultimately returned.
    d = Objects.DFXMLObject(version="1.2.0")
    if sys.argv[0] == os.path.basename(__file__):
        d.program = sys.argv[0]
        d.program_version = __version__
    d.command_line = " ".join(sys.argv)
    d.add_namespace("delta", dfxml.XMLNS_DELTA)
    d.dc["type"] = "Disk image difference set"
    d.add_creator_library("Python", ".".join(map(str, sys.version_info[0:3]))) #A bit of a bend, but gets the major version information out.
    d.add_creator_library("Objects.py", Objects.__version__)
    d.add_creator_library("dfxml.py", Objects.dfxml.__version__)

    d.diff_file_ignores |= ignore_properties
    _logger.debug("d.diff_file_ignores = " + repr(d.diff_file_ignores))

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
    old_volumes = None
    new_volumes = None
    matched_volumes = dict()

    #Populated in distinct (offset, file system type as string) encounter order
    volumes_encounter_order = dict()

    for infile in [pre, post]:

        _logger.debug("infile = %r" % infile)
        old_fis = new_fis
        new_fis = dict()

        old_volumes = new_volumes
        new_volumes = dict()
        #Fold in the matched volumes - we're just discarding the deleted volumes
        for k in matched_volumes:
            old_volumes[k] = matched_volumes[k]
        matched_volumes = dict()

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

                #Use the lower-case volume spelling
                ftype_str = _lower_ftype_str(new_obj)

                #Re-capping the general differential analysis algorithm:
                #0. If the volume is in the new list, something's gone wrong.
                if (offset, ftype_str) in new_volumes:
                    _logger.debug("new_obj.partition_offset = %r." % offset)
                    _logger.warning("Encountered a volume that starts at an offset as another volume, in the same disk image.  This analysis is based on the assumption that that doesn't happen.  Check results that depend on partition mappings.")

                #1. If the volume is in the old list, pop it out of the old list - it's matched.
                if old_volumes and (offset, ftype_str) in old_volumes:
                    _logger.debug("Found a volume in post image, at offset %r." % offset)
                    old_obj = old_volumes.pop((offset, ftype_str))
                    new_obj.original_volume = old_obj
                    new_obj.compare_to_original()
                    matched_volumes[(offset, ftype_str)] = new_obj

                #2. If the volume is NOT in the old list, add it to the new list.
                else:
                    _logger.debug("Found a new volume, at offset %r." % offset)
                    new_volumes[(offset, ftype_str)] = new_obj
                    volumes_encounter_order[(offset, ftype_str)] = len(new_volumes) + ((old_volumes and len(old_volumes)) or 0) + len(matched_volumes)

                #3. Afterwards, the old list contains deleted volumes.

                #Record the ID
                new_obj.id = volumes_encounter_order[(offset, ftype_str)]

                #Move on to the next object
                continue
            elif not isinstance(new_obj, Objects.FileObject):
                #The rest of this loop compares only file objects.
                continue

            if ignore_filename_function(new_obj.filename):
                continue

            #Simplify byte runs if requested
            if glom_byte_runs:
                if new_obj.byte_runs:
                    temp_byte_runs = Objects.ByteRuns()
                    for run in new_obj.byte_runs:
                        temp_byte_runs.glom(run)
                    new_obj.byte_runs = temp_byte_runs

            #Normalize the partition number
            if new_obj.volume_object is None:
                new_obj.partition = None
            else:
                vo = new_obj.volume_object
                fts = _lower_ftype_str(vo)
                new_obj.partition = volumes_encounter_order[(vo.partition_offset, fts)]

            #Define the identity key of this file -- affected by the --ignore argument
            _key_partition = None if "partition" in ignore_properties else new_obj.partition
            _key_inode = None if "inode" in ignore_properties else new_obj.inode
            _key_filename = None if "filename" in ignore_properties else new_obj.filename
            key = (_key_partition, _key_inode, _key_filename)

            #Ignore unallocated content comparisons until a later loop.  The unique identification of deleted files needs a little more to work.
            if not new_obj.alloc:
                new_fis_unalloc[key].append(new_obj)
                continue

            #The rest of this loop is irrelevant until the second DFXML file.
            if old_fis is None:
                new_fis[key] = new_obj
                continue


            if key in old_fis:
                #Extract the old fileobject and check for changes
                old_obj = old_fis.pop(key)
                new_obj.original_fileobject = old_obj
                new_obj.compare_to_original(file_ignores=d.diff_file_ignores)

                #_logger.debug("Diffs: %r." % _diffs)
                _diffs = new_obj.diffs - d.diff_file_ignores
                #_logger.debug("Diffs after ignore-set: %r." % _diffs)
                if diff_mask_set:
                    _diffs &= diff_mask_set
                    #_logger.debug("Diffs after mask-set: %r." % _diffs)

                if len(_diffs) > 0:
                    #_logger.debug("Remaining diffs: " + repr(_diffs))
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
        _logger.debug("len(old_fis_unalloc) = %d" % len(old_fis_unalloc))
        _logger.debug("len(new_fis) = %d" % len(new_fis))
        _logger.debug("len(new_fis_unalloc) = %d" % len(new_fis_unalloc))
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
            (partition, inode) = key

            if len(new_inode_names[key]) != 1:
                continue
            if not key in old_inode_names:
                continue
            if len(old_inode_names[key]) != 1:
                continue
            if rename_requires_hash:
                #Peek at the set elements by doing a quite-ephemeral list cast
                old_obj = old_fis[(partition, inode, list(old_inode_names[key])[0])]
                new_obj = new_fis[(partition, inode, list(new_inode_names[key])[0])]
                if old_obj.sha1 != new_obj.sha1:
                    continue

            #Found a match if we're at this point in the loop
            old_name = old_inode_names[key].pop()
            new_name = new_inode_names[key].pop()
            old_obj = old_fis.pop((partition, inode, old_name))
            new_obj = new_fis.pop((partition, inode, new_name))
            new_obj.original_fileobject = old_obj
            new_obj.compare_to_original(file_ignores=d.diff_file_ignores)
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
            #TODO Test for what chaos ensues when filename is in the ignore list.
            new_obj.compare_to_original(file_ignores=d.diff_file_ignores)
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
                    new_obj.compare_to_original(file_ignores=d.diff_file_ignores)
                    #The file might not have changed.  It's interesting if it did, though.

                    _diffs = new_obj.diffs - diff_mask_set
                    #_logger.debug("Diffs: %r." % _diffs)
                    if diff_mask_set:
                        _diffs &= diff_mask_set
                        #_logger.debug("Diffs after mask-set: %r." % _diffs)
                    if len(_diffs) > 0:
                        _logger.debug("Remaining diffs: " + repr(_diffs))
                        fileobjects_changed.append(new_obj)
                    elif retain_unchanged:
                        fileobjects_unchanged.append(new_obj)
            elif key in old_fis:
                #Identified a deletion.
                old_obj = old_fis.pop(key)
                new_obj = new_fis_unalloc[key].pop()
                new_obj.original_fileobject = old_obj
                new_obj.compare_to_original(file_ignores=d.diff_file_ignores)
                fileobjects_deleted.append(new_obj)
        _logger.debug("len(old_fis) -> %d" % len(old_fis))
        _logger.debug("len(old_fis_unalloc) -> %d" % len(old_fis_unalloc))
        _logger.debug("len(new_fis) -> %d" % len(new_fis))
        _logger.debug("len(new_fis_unalloc) -> %d" % len(new_fis_unalloc))
        _logger.debug("len(fileobjects_changed) -> %d" % len(fileobjects_changed))
        _logger.debug("len(fileobjects_deleted) -> %d" % len(fileobjects_deleted))

        #After deletion matching is performed, one might want to look for files migrating to other partitions.
        #However, since between-volume migration creates a new deleted file, this algorithm instead ignores partition migrations.
        #AJN TODO Thinking about it a little more, I can't suss out a reason against trying this match.  It's complicated if we try looking for reallocations in new_fis, strictly from new_fis_unalloc.

        #TODO We might also want to match the unallocated objects based on metadata addresses.  Unfortunately, that requires implementation of additional byte runs, which hasn't been fully designed yet in the DFXML schema.

        #Begin output.
        #First, annotate the volume objects.
        for key in new_volumes:
            v = new_volumes[key]
            v.annos.add("new")
        for key in old_volumes:
            v = old_volumes[key]
            v.annos.add("deleted")
        for key in matched_volumes:
            v = matched_volumes[key]
            if len(v.diffs) > 0:
                v.annos.add("modified")

        #Build list of FileObject appenders, child volumes of the DFXML Document.
        #Key: Partition number, or None
        #Value: Reference to the VolumeObject corresponding with that partition number.  None -> the DFXMLObject.
        appenders = dict()
        for volume_dict in [new_volumes, matched_volumes, old_volumes]:
            for (offset, ftype_str) in volume_dict:
                    veo = volumes_encounter_order[(offset, ftype_str)]
                    if veo in appenders:
                        raise ValueError("This pair is already in the appenders dictionary, which was supposed to be distinct: " + repr((offset, ftype_str)) + ", encounter order " + str(veo) + ".")
                    v = volume_dict[(offset, ftype_str)]
                    appenders[veo] = v
                    d.append(v)

        #Add in the default appender, the DFXML Document itself.
        appenders[None] = d

        #A file should only be considered "modified" if its contents have changed.
        content_diffs = set(["md5", "sha1", "sha256"])

        def _maybe_match_attr(obj):
            """Just adds the 'matched' annotation when called."""
            if annotate_matches:
                obj.annos.add("matched")

        #Populate DFXMLObject.
        for key in new_fis:
            #TODO If this script ever does a series of >2 DFXML files, these diff additions need to be removed for the next round.
            fi = new_fis[key]
            fi.annos.add("new")
            appenders[fi.partition].append(fi)
        for key in new_fis_unalloc:
            for fi in new_fis_unalloc[key]:
                fi.annos.add("new")
                appenders[fi.partition].append(fi)
        for fi in fileobjects_deleted:
            #Independently flag for name, content, and metadata modifications
            if len(fi.diffs - content_diffs) > 0:
                fi.annos.add("changed")
            if len(content_diffs.intersection(fi.diffs)) > 0:
                fi.annos.add("modified")
            if "filename" in fi.diffs:
                fi.annos.add("renamed")
            fi.annos.add("deleted")
            _maybe_match_attr(fi)
            appenders[fi.partition].append(fi)
        for key in old_fis:
            ofi = old_fis[key]
            nfi = Objects.FileObject()
            nfi.original_fileobject = ofi
            nfi.annos.add("deleted")
            appenders[ofi.partition].append(nfi)
        for key in old_fis_unalloc:
            for ofi in old_fis_unalloc[key]:
                nfi = Objects.FileObject()
                nfi.original_fileobject = ofi
                nfi.annos.add("deleted")
                appenders[ofi.partition].append(nfi)
        for fi in fileobjects_renamed:
            #Independently flag for content and metadata modifications
            if len(content_diffs.intersection(fi.diffs)) > 0:
                fi.annos.add("modified")
            if len(fi.diffs - content_diffs) > 0:
                fi.annos.add("changed")
            fi.annos.add("renamed")
            _maybe_match_attr(fi)
            appenders[fi.partition].append(fi)
        for fi in fileobjects_changed:
            #Independently flag for content and metadata modifications
            if len(content_diffs.intersection(fi.diffs)) > 0:
                fi.annos.add("modified")
            if len(fi.diffs - content_diffs) > 0:
                fi.annos.add("changed")
            _maybe_match_attr(fi)
            appenders[fi.partition].append(fi)
        for fi in fileobjects_unchanged:
            _maybe_match_attr(fi)
            appenders[fi.partition].append(fi)

        #Output
        return d

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--idifference-diffs", action="store_true", help="Only consider the modifications idifference had considered (names, hashes, timestamps).")
    parser.add_argument("-i", "--ignore", action="append", help="Object property to ignore in all difference operations.  E.g. pass '-i inode' to ignore inode differences when comparing directory trees on the same file system.  Affects annotation attributes placed on the fileobject element and the named property's elements, and also the properties used to determine file identities for matching.")
    parser.add_argument("--rename-with-hash", action="store_true", help="Require that renamed files must match on a content hash.")
    parser.add_argument("--retain-unchanged", action="store_true", help="Output unchanged files in the resulting DFXML file.", default=False)
    parser.add_argument("--annotate-matches", action="store_true", help="Add a 'delta:matched' Boolean attribute to every produced object.  Useful for some counting purposes, but not always needed.", default=False)
    parser.add_argument("--simplify-byte-runs", action="store_true", help="Join contiguous byte run elements together, if their attributes align.", default=False)
    parser.add_argument("infiles", nargs="+")
    args = parser.parse_args()

    #TODO Add --vignore to ignore volume properties, like ftype_str to compare only file system offsets for partitions
    #TODO Switch --ignore to --fignore
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
            dobj = make_differential_dfxml(
              pre,
              post,
              diff_mode="idifference" if args.idifference_diffs else "all",
              retain_unchanged=args.retain_unchanged,
              ignore_properties=ignore_properties,
              annotate_matches=args.annotate_matches,
              rename_requires_hash=args.rename_with_hash
            )
            dobj.print_dfxml()
