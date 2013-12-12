#!/usr/bin/env python3

"""
For a disk image or DFXML file, this program produces a cross-tabulation of the allocation state of each file's inode and name.
"""

__version__ = "0.1.1"
#Version 0.2.0:
# * Tabular output in HTML
# * Tabular output in LaTeX

import Objects
import make_differential_dfxml

import collections
import logging
import sys
import xml.etree.ElementTree as ET
import os

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    counter = collections.defaultdict(lambda: 0)
    prev_obj = None
    for (event, obj) in Objects.iterparse(args.input_image):
        if isinstance(obj, Objects.FileObject):
            if args.ignore_virtual_files and make_differential_dfxml.ignorable_name(obj.filename):
                continue
            counter[(obj.alloc_inode, obj.alloc_name)] += 1

            #Inspect weird data
            if args.debug and obj.alloc_inode is None and obj.alloc_name is None:
                _logger.debug("Encountered a file with all-null allocation.")
                _logger.debug("Event: %r." % event)
                _logger.debug("Previous object: %s." % ET.tostring(prev_obj.to_Element()))
                _logger.debug("Current  object: %s." % ET.tostring(obj.to_Element()))
        prev_obj = obj
    print(repr(counter))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ignore-virtual-files", action="store_true", help="Use the same file-ignoring rules as make_differential_dfxml.py.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug printing.")
    parser.add_argument("input_image", help="Disk image, or DFXML file.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
