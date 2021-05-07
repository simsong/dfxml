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
This program takes a differentially-annotated DFXML file as input, and outputs a DFXML document that contains 'Silent' changes.  For instance, a changed checksum with no changed timestamps would be 'Silent.'
"""

__version__ = "0.2.2"

import os
import logging
import sys

_logger = logging.getLogger(os.path.basename(__file__))

import dfxml.objects as Objects
import make_differential_dfxml

def main():
    d = Objects.DFXMLObject("1.2.0")
    d.program = sys.argv[0]
    d.program_version = __version__
    d.command_line = " ".join(sys.argv)
    d.dc["type"] = "File system silent-change report"
    d.add_creator_library("Python", ".".join(map(str, sys.version_info[0:3]))) #A bit of a bend, but gets the major version information out.
    d.add_creator_library("Objects.py", Objects.__version__)
    d.add_creator_library("dfxml.py", Objects.dfxml.__version__)

    current_appender = d
    tally = 0
    for (event, obj) in Objects.iterparse(args.infile):
        if event == "start":
            #Inherit namespaces
            if isinstance(obj, Objects.DFXMLObject):
                for (prefix, url) in obj.iter_namespaces():
                    d.add_namespace(prefix, url)
            #Group files by volume
            elif isinstance(obj, Objects.VolumeObject):
                d.append(obj)
                current_appender = obj
        elif event == "end":
            if isinstance(obj, Objects.VolumeObject):
                current_appender = d
            elif isinstance(obj, Objects.FileObject):
                if "_changed" not in obj.diffs:
                    if "_modified" in obj.diffs or "_renamed" in obj.diffs:
                        current_appender.append(obj)
                        tally += 1
    print(d.to_dfxml())
    _logger.info("Found %d suspiciously-changed files." % tally)


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
