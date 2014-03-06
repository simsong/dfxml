#!/usr/bin/env python3
#Make a new DFXML file of all fileobjects in an input DFXML file.

__version__ = "0.2.1"

import sys
import xml.etree.ElementTree as ET
import dfxml
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

if sys.version < "3":
    _logger.error("Due to Unicode issues with Python 2's ElementTree, Python 3 and up is required.\n")
    exit(1)

def main():

    print("""\
<?xml version="1.0" encoding="UTF-8"?>
<dfxml
  xmlns="%s"
  xmlns:delta="%s"
  version="1.1.0">
  <creator>
    <program>%s</program>
    <version>%s</version>
    <execution_environment>
      <command_line>%s</command_line>
    </execution_environment>
  </creator>
  <source>
    <image_filename>%s</image_filename>
  </source>\
""" % (dfxml.XMLNS_DFXML, dfxml.XMLNS_DELTA, sys.argv[0], __version__, " ".join(sys.argv), args.filename))

    ET.register_namespace("delta", dfxml.XMLNS_DELTA)

    xs = []
    for fi in dfxml.iter_dfxml(xmlfile=open(args.filename, "rb"), preserve_elements=True):
        _logger.debug("Processing: %s" % str(fi))
        if args.cache:
            xs.append(fi.xml_element)
        else:
            _logger.debug("Printing without cache: %s" % str(fi))
            print(dfxml.ET_tostring(fi.xml_element, encoding="unicode"))
    if args.cache:
        for x in xs:
            _logger.debug("Printing with cache: %s" % str(fi))
            print(dfxml.ET_tostring(x, encoding="unicode"))

    print("""</dfxml>""")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("--cache", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
