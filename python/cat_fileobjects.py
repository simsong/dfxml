#!/usr/bin/env python3
#Make a new DFXML file of all fileobjects in an input DFXML file.

__version__ = "0.1.0"

import sys
import xml.etree.ElementTree as ET
import dfxml

if sys.version < "3":
    sys.stderr.write("Due to Unicode issues with Python 2's ElementTree, Python 3 and up is required.\n")
    exit(1)

def main():

    print("""\
<?xml version="1.0" encoding="UTF-8"?>
<dfxml xmloutputversion="1.0">
  <creator version="1.0">
    <program>%s</program>
    <version>%s</version>
    <execution_environment>
      <command_line>%s</command_line>
    </execution_environment>
  </creator>
  <source>
    <image_filename>%s</image_filename>
  </source>\
""" % (sys.argv[0], __version__, " ".join(sys.argv), args.filename))

    xs = []
    for fi in dfxml.iter_dfxml(xmlfile=open(args.filename, "rb"), preserve_elements=True):
        if args.cache:
            xs.append(fi.xml_element)
        else:
            print(ET.tostring(fi.xml_element, encoding="unicode"))
    if args.cache:
        for x in xs:
            print(ET.tostring(x, encoding="unicode"))

    print("""</dfxml>""")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("--cache", action="store_true")
    args = parser.parse_args()
    main()
