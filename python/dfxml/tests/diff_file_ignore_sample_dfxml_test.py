#!/usr/bin/env python

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

__version__ = "0.1.0"

import logging
import os
import sys

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

def main():
    dobj = Objects.DFXMLObject()
    dobj.diff_file_ignores.add("atime")
    dobj.diff_file_ignores.add("crtime")
    with open(args.out_dfxml, "w") as fh:
        dobj.print_dfxml(fh)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("out_dfxml")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    main()
