#!/usr/bin/env python3

__version__ = "0.0.3"

import os
import logging
import Objects
import idifference
import copy

def enumerated_changes(filelist):
    res = set()
    for fi in filelist:
        diffs_remaining = copy.copy(fi.diffs)
        if "filename" in diffs_remaining:
            diffs_remaining.pop("filename")
        res.add((fi.filename, "renamed to", fi.original_fileobject.filename))
    return sorted(res)

def main():
    global args
    new_files = []
    deleted_files = []
    renamed_files = []
    modified_files = []
    changed_files = []
    for obj in Objects.objects_from_file(args.infile):
        if isinstance(obj, Objects.FileObject):
            #logging.debug("Inspecting %s for changes" % obj)
            if "_new" in obj.diffs:
                new_files.append(obj)
            elif "_deleted" in obj.diffs:
                deleted_files.append(obj)
            elif "_renamed" in obj.diffs:
                renamed_files.append(obj)
            elif "_modified" in obj.diffs:
                modified_files.append(obj)
            elif "_changed" in obj.diffs:
                changed_files.append(obj)
        elif isinstance(obj, Objects.VolumeObject):
            #TODO
            pass
        elif isinstance(obj, Objects.DFXMLObject):
            #TODO Implement yielding this
            pass

    idifference.h2("New files:")
    res = [(obj.mtime, obj.filesize, obj.filename) for obj in new_files]
    idifference.table(sorted(res))

    idifference.h2("Deleted files:")
    res = [(obj.mtime, obj.filesize, obj.filename) for obj in deleted_files]
    idifference.table(sorted(res))

    idifference.h2("Renamed files:")
    res = enumerated_changes(renamed_files)
    idifference.table(res, break_on_change=True)

    idifference.h2("Summary:")
    idifference.table([
      #("Prior image's file (file object) tally", str(self.fi_tally)),
      #("Prior image's file (inode) tally", str(len(self.inodes))),
      #("Current image's file (file object) tally", str(self.new_fi_tally)),
      #("Current image's file (inode) tally", str(len(self.new_inodes))),
      ("New files", str(len(new_files))),
      ("Deleted files", str(len(deleted_files))),
      ("Renamed files", str(len(renamed_files))),
      ("Files with modified content", str(len(modified_files))),
      ("Files with changed file properties", str(len(changed_files)))
    ])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("infile")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if not args.infile.endswith("xml"):
        raise Exception("Input file should be a DFXML file, and should end with 'xml': %r." % args.infile)

    if not os.path.exists(args.infile):
        raise Exception("Input file does not exist: %r." % args.infile)

    main()
