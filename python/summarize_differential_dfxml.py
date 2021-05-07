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

__version__ = "0.8.2"

import os
import logging
import dfxml.objects as Objects
import idifference
import copy
import collections
import make_differential_dfxml
import operator

_logger = logging.getLogger(os.path.basename(__file__))

#Only issue a potentially verbose warning once
_nagged_timestamp_format = False

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

def report(dfxmlobject, sort_by=None, summary=None, timestamp=None):
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
    renamed_files_content_matches = []
    modified_files = []
    changed_files = []
    unchanged_files = []

    obj_alloc_counters = [FOCounter(), FOCounter()]
    matched_files_tally = 0

    def _is_matched(obj):
        _matched = "matched" in obj.annos
        return _matched

    #Group objects by differential annotations
    for obj in dfxmlobject:
        if isinstance(obj, Objects.FileObject):
            if "matched" in obj.annos:
                matched_files_tally += 1

            #_logger.debug("Inspecting %s for changes" % obj)
            if "new" in obj.annos:
                new_files.append(obj)
            elif "deleted" in obj.annos:
                deleted_files.append(obj)
                if _is_matched(obj):
                    deleted_files_matched.append(obj)
                else:
                    deleted_files_unmatched.append(obj)
            elif "renamed" in obj.annos:
                #Count content matches
                if obj.original_fileobject.sha1 == obj.sha1:
                    renamed_files_content_matches.append(obj)

                renamed_files.append(obj)
                if obj.name_type != obj.original_fileobject.name_type:
                    renamed_files_type_changed.append(obj)
                    renamed_files_type_changes[(obj.original_fileobject.name_type or "", obj.name_type or "")] += 1
                elif obj.name_type == "r":
                    renamed_files_regular.append(obj)
                elif obj.name_type == "d":
                    renamed_files_directory.append(obj)
                else:
                    renamed_files_other.append(obj)
            elif "modified" in obj.annos:
                modified_files.append(obj)
            elif "changed" in obj.annos:
                changed_files.append(obj)
            else:
                unchanged_files.append(obj)

            #Count files of the post image
            if "deleted" in obj.annos:
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

    def _sortkey_singlefi():
        """Return a sorting key function, fit for use in sorted() on a list of FileObjects."""
        def _key_by_path(fi):
            return (
              fi.filename or "",
              str(fi.mtime) or "n/a",
              (fi.original_fileobject and fi.original_fileobject.filename) or "",
              (fi.original_fileobject and str(fi.original_fileobject.mtime)) or "n/a"
            )
        def _key_by_times(fi):
            return (
              str(fi.mtime) or "n/a",
              str(fi.crtime) or "n/a",
              fi.filename,
              (fi.original_fileobject and str(fi.original_fileobject.mtime)) or "n/a",
              (fi.original_fileobject and str(fi.original_fileobject.crtime)) or "n/a",
              (fi.original_fileobject and fi.original_fileobject.filename) or ""
            )
        if sort_by == "path":
            return _key_by_path
        else: #Default: "times"
            return _key_by_times

    def _format_timestamp(t):
        """Takes a timestamp, returns a string."""
        if t is None:
            return "n/a"
        if timestamp:
            if t.timestamp:
                return str(t.timestamp)
            else:
                if not _nagged_timestamp_format:
                    _nagged_timestamp_format = True
                    _logger.warning("Tried to format a Unix timestamp, but failed.")
                return "n/a"
        else:
            return str(t)

    idifference.h2("New files:")
    new_files_sorted = sorted(new_files, key=_sortkey_singlefi())
    res = [(_format_timestamp(obj.mtime), obj.filename or "", obj.filesize) for obj in new_files_sorted]
    idifference.table(res)

    idifference.h2("Deleted files:")
    deleted_files_sorted = sorted(deleted_files, key=_sortkey_singlefi())
    res = [(
      obj.original_fileobject.mtime,
      obj.original_fileobject.filename or "",
      obj.original_fileobject.filesize
    ) for obj in deleted_files_sorted]
    idifference.table(res)

    def _sortkey_renames():
        def _key_by_path(fi):
            return (
              fi.original_fileobject.filename or "",
              fi.filename or "",
              str(fi.mtime) or "",
              str(fi.original_fileobject.mtime) or ""
            )
        def _key_by_times(fi):
            return (
              str(fi.mtime) or "n/a",
              str(fi.ctime) or "n/a",
              str(fi.atime) or "n/a",
              str(fi.dtime) or "n/a",
              str(fi.crtime) or "n/a",
              fi.original_fileobject.filename or "",
              fi.filename or ""
            )
        if sort_by == "path":
            return _key_by_path
        else: #Default: "times"
            return _key_by_times

    def _enumerated_changes(filelist):
        res = []
        for fi in filelist:
            diffs_remaining = copy.deepcopy(fi.diffs)
            if "filename" in diffs_remaining:
                diffs_remaining -= {"filename"}
                res.append(("Renamed", "", fi.original_fileobject.filename, "renamed to", fi.filename))
            for timeattr in Objects.TimestampObject.timestamp_name_list:
                if timeattr in diffs_remaining:
                    diffs_remaining -= {timeattr}
                    res.append((
                      fi.filename or "",
                      "%s changed, " % timeattr, 
                      _format_timestamp(getattr(fi.original_fileobject, timeattr)),
                      "->", 
                      _format_timestamp(getattr(fi, timeattr))
                    ))
            for diff in sorted(diffs_remaining):
                diffs_remaining -= {diff}
                res.append((
                  fi.filename or "",
                  "%s changed, " % diff, 
                  getattr(fi.original_fileobject, diff) or ""
                  "->", 
                  getattr(fi, diff) or "", 
                ))
        return res

    idifference.h2("Renamed files:")
    renamed_files_sorted = sorted(renamed_files, key=_sortkey_renames())
    res = _enumerated_changes(renamed_files_sorted)
    idifference.table(res, break_on_change=True)

    idifference.h2("Files with modified contents:")
    modified_files_sorted = sorted(modified_files, key=_sortkey_singlefi())
    res = _enumerated_changes(modified_files_sorted)
    idifference.table(res, break_on_change=True)

    idifference.h2("Files with changed properties:")
    changed_files_sorted = sorted(changed_files, key=_sortkey_singlefi())
    res = _enumerated_changes(changed_files_sorted)
    idifference.table(res, break_on_change=True)

    if summary:
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
          ("  Content matches", str(len(renamed_files_content_matches))),
          ("Files with modified content", str(len(modified_files))),
          ("Files with changed file properties", str(len(changed_files)))
        ]

        idifference.table(summ_recs)

def main():
    global args
    dfxmlobject = Objects.parse(args.infile)
    report(dfxmlobject, sort_by=args.sort_by, summary=args.summary)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--sort-by", help="Sorts file lists.  Pass one of these arguments: \"times\" or \"path\".")
    parser.add_argument("--summary",help="output summary statistics of file system changes",action="store_true", default=False)
    parser.add_argument("infile", help="A differential DFXML file.  Should include the optional 'delta:matched' attributes for counts to work correctly.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if not args.infile.endswith("xml"):
        raise Exception("Input file should be a DFXML file, and should end with 'xml': %r." % args.infile)

    if not os.path.exists(args.infile):
        raise Exception("Input file does not exist: %r." % args.infile)

    main()
