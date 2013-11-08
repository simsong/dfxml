#!/usr/bin/env python3

__version__ = "0.0.1"

import dfxml
import Objects
import logging
import sys
import xml.etree.ElementTree as ET

def main():
    d = Objects.DFXMLObject()

    d.command_line = " ".join(sys.argv)

    #TODO These samples will do for development.
    for sample_path in [
      "../samples/difference_test_0.xml",
      "../samples/difference_test_1.xml"
    ]:
      with open(sample_path, "rb") as fh:
        v = Objects.VolumeObject()
        for (event, elem) in ET.iterparse(fh, events=("start-ns", "end")):
            #logging.debug("(event, elem) = " + repr((event, elem)))
            if event == "start-ns":
                d.add_namespace(*elem)
            elif event == "end":
                qn = Objects._qsplit(elem.tag)
                if qn[1] in ["fileobject", "original_fileobject"]:
                    nfi = Objects.FileObject()
                    nfi.populate_from_Element(elem)
                    v.append(nfi)
        d.append(v)
    d.print_dfxml()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
