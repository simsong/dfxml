#!/usr/bin/env python3

"""
This program takes a differentially-annotated DFXML file as input, and outputs a DFXML document that contains 'Silent' changes.  For instance, a changed checksum with no changed timestamps would be 'Silent.'
"""

__version__ = "0.1.0"

import os
import logging
import Objects
import make_differential_dfxml

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    d = Objects.DFXMLObject()
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
