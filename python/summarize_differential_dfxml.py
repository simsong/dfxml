#!/usr/bin/env python3

__version__ = "0.3.0"

import os
import logging
import Objects
import idifference
import copy
import collections
import make_differential_dfxml

_logger = logging.getLogger(os.path.basename(__file__))

def enumerated_changes(filelist):
    res = set()
    for fi in filelist:
        diffs_remaining = copy.copy(fi.diffs)
        if "filename" in diffs_remaining:
            diffs_remaining.pop("filename")
        res.add((fi.filename, "renamed to", fi.original_fileobject.filename))
    return sorted(res)

class FOCounter(object):
    "Counter for FileObjects.  Does not count differences (differential annotations)."

    def __init__(self):
        self._inodes = set()
        self._fo_tally = 0
        self._fo_unalloc_unmatch_tally = 0
        self._fo_allocation_tallies_inode = {True:0, False:0, None:0}
        self._fo_allocation_tallies_name = {True:0, False:0, None:0}

    def add(self, obj):
        assert isinstance(obj, Objects.FileObject)
        self._inodes.add((obj.partition, obj.inode))
        self._fo_tally += 1

        self._fo_allocation_tallies_inode[obj.alloc_inode] += 1
        self._fo_allocation_tallies_name[obj.alloc_name] += 1
        if not (obj.alloc_name and obj.alloc_inode) and obj.original_fileobject is None:
            self._fo_unalloc_unmatch_tally += 1

    @property
    def inode_tally(self):
        return len(self._inodes)

    @property
    def fo_tally(self):
        return self._fo_tally

    @property
    def fo_unalloc_unmatch_tally(self):
        return self._fo_unalloc_unmatch_tally

    @property
    def fo_tally_alloc_inode(self):
        return self._fo_allocation_tallies_inode[True]

    @property
    def fo_tally_alloc_name(self):
        return self._fo_allocation_tallies_name[True]

    @property
    def fo_tally_nullalloc_inode(self):
        return self._fo_allocation_tallies_inode[None]

    @property
    def fo_tally_nullalloc_name(self):
        return self._fo_allocation_tallies_name[None]

    @property
    def fo_tally_unalloc_inode(self):
        return self._fo_allocation_tallies_inode[False]

    @property
    def fo_tally_unalloc_name(self):
        return self._fo_allocation_tallies_name[False]

def main():
    global args
    new_files = []
    deleted_files = []
    deleted_files_matched = []
    deleted_files_unmatched = []
    renamed_files = []
    renamed_files_directory = []
    renamed_files_regular = []
    renamed_files_other = []
    renamed_files_type_changed = []
    renamed_files_type_changes = collections.defaultdict(int) #Key: (old name_type, new name_type); value: counter
    modified_files = []
    changed_files = []
    unchanged_files = []

    obj_alloc_counters = [FOCounter(), FOCounter()]
    matched_files_tally = 0

    def _is_matched(obj):
        _matched = "_matched" in obj.diffs
        return _matched

    for (event, obj) in Objects.iterparse(args.infile):
        if isinstance(obj, Objects.FileObject):
            if "_matched" in obj.diffs:
                matched_files_tally += 1

            #_logger.debug("Inspecting %s for changes" % obj)
            if "_new" in obj.diffs:
                new_files.append(obj)
            elif "_deleted" in obj.diffs:
                deleted_files.append(obj)
                if _is_matched(obj):
                    deleted_files_matched.append(obj)
                else:
                    deleted_files_unmatched.append(obj)
            elif "_renamed" in obj.diffs:
                renamed_files.append(obj)
                if obj.name_type != obj.original_fileobject.name_type:
                    renamed_files_type_changed.append(obj)
                    renamed_files_type_changes[(obj.original_fileobject.name_type, obj.name_type)] += 1
                elif obj.name_type == "r":
                    renamed_files_regular.append(obj)
                elif obj.name_type == "d":
                    renamed_files_directory.append(obj)
                else:
                    renamed_files_other.append(obj)
            elif "_modified" in obj.diffs:
                modified_files.append(obj)
            elif "_changed" in obj.diffs:
                changed_files.append(obj)
            else:
                unchanged_files.append(obj)

            #Count files of the post image
            if "_deleted" in obj.diffs:
                #Don't count the "Ghost" files created for deleted files that weren't matched between images
                if _is_matched(obj):
                    obj_alloc_counters[1].add(obj)
            else:
                obj_alloc_counters[1].add(obj)
            #Count files of the baseline image
            if obj.original_fileobject:
                obj_alloc_counters[0].add(obj.original_fileobject)
        elif isinstance(obj, Objects.VolumeObject):
            #TODO
            pass

    idifference.h2("New files:")
    res = [(obj.mtime, obj.filename or "", obj.filesize) for obj in new_files]
    idifference.table(sorted(res))

    idifference.h2("Deleted files:")
    res = [(obj.mtime, obj.filename or "", obj.filesize) for obj in deleted_files]
    idifference.table(sorted(res))

    idifference.h2("Renamed files:")
    res = enumerated_changes(renamed_files)
    idifference.table(res, break_on_change=True)

    idifference.h2("Summary:")
    summ_recs = [
      ("Prior image's file (file object) tally", str(obj_alloc_counters[0].fo_tally)),
      ("  Inode allocation", ""),
      ("    Allocated", str(obj_alloc_counters[0].fo_tally_alloc_inode)),
      ("    Unallocated", str(obj_alloc_counters[0].fo_tally_unalloc_inode)),
      ("    Unknown", str(obj_alloc_counters[0].fo_tally_nullalloc_inode)),
      ("  Name allocation", ""),
      ("    Allocated", str(obj_alloc_counters[0].fo_tally_alloc_name)),
      ("    Unallocated", str(obj_alloc_counters[0].fo_tally_unalloc_name)),
      ("    Unknown", str(obj_alloc_counters[0].fo_tally_nullalloc_name)),
      ("  Unallocated, unmatched", obj_alloc_counters[0].fo_unalloc_unmatch_tally),
      ("Prior image's file (inode) tally", str(obj_alloc_counters[0].inode_tally)),
      ("Current image's file (file object) tally", str(obj_alloc_counters[1].fo_tally)),
      ("  Inode allocation", ""),
      ("    Allocated", str(obj_alloc_counters[1].fo_tally_alloc_inode)),
      ("    Unallocated", str(obj_alloc_counters[1].fo_tally_unalloc_inode)),
      ("    Unknown", str(obj_alloc_counters[1].fo_tally_nullalloc_inode)),
      ("  Name allocation", ""),
      ("    Allocated", str(obj_alloc_counters[1].fo_tally_alloc_name)),
      ("    Unallocated", str(obj_alloc_counters[1].fo_tally_unalloc_name)),
      ("    Unknown", str(obj_alloc_counters[1].fo_tally_nullalloc_name)),
      ("  Unallocated, unmatched", obj_alloc_counters[1].fo_unalloc_unmatch_tally),
      ("Current image's file (inode) tally", str(obj_alloc_counters[1].inode_tally)),
      ("Matched files", str(matched_files_tally)),
      ("", ""),
      ("New files", str(len(new_files))),
      ("Deleted files", str(len(deleted_files))),
      ("  Unmatched", str(len(deleted_files_unmatched))),
      ("  Matched", str(len(deleted_files_matched))),
      ("Renamed files", str(len(renamed_files))),
      ("  Directories", str(len(renamed_files_directory))),
      ("  Regular files", str(len(renamed_files_regular))),
      ("  Other", str(len(renamed_files_other))),
      ("  Type changed", str(len(renamed_files_type_changed))),
    ]
    for key in sorted(renamed_files_type_changes.keys()):
        summ_recs.append(("    %s -> %s" % key, str(renamed_files_type_changes[key])))
    summ_recs += [
      ("Files with modified content", str(len(modified_files))),
      ("Files with changed file properties", str(len(changed_files)))
    ]

    idifference.table(summ_recs)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("infile", help="A differential DFXML file.  Should include the optional 'delta:matched' attributes for counts to work correctly.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if not args.infile.endswith("xml"):
        raise Exception("Input file should be a DFXML file, and should end with 'xml': %r." % args.infile)

    if not os.path.exists(args.infile):
        raise Exception("Input file does not exist: %r." % args.infile)

    main()
