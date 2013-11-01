#!/usr/bin/env python3

__version__ = "0.0.1"

import os
import logging
import dfxml

def main():
    global args
    with open(args.infile, "rb") as xmlfile:
        for fi in dfxml.iter_dfxml(xmlfile, preserve_elements=True):
            print(dir(fi.original_fileobject))

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
