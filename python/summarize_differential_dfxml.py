#!/usr/bin/env python3

__version__ = "0.0.2"

import os
import logging
import Objects
import idifference

def main():
    global args
    new_files = []
    deleted_files = []
    renamed_files = []
    modified_files = []
    changed_files = []
    for obj in Objects.objects_from_file(args.infile):
        if isinstance(obj, Objects.FileObject):
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

    idifference.h2("New files:")
    res = [(obj.mtime, str(obj.filesize, obj.filename)) for obj in new_files]
    idifference.table(sorted(res))

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
