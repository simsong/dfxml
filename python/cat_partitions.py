#!/usr/bin/env python3

__version__ = "0.0.3"

import dfxml
import Objects
import logging
import sys
import xml.etree.ElementTree as ET

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    d = Objects.DFXMLObject(version="1.1.0")

    d.command_line = " ".join(sys.argv)

    #TODO These samples will do for development.
    for (sample_path_index, sample_path) in enumerate([
      "../samples/difference_test_0.xml",
      "../samples/difference_test_1.xml"
    ]):
      _logger.debug("Running on path %r" % sample_path)
      with open(sample_path, "rb") as fh:
        v = Objects.VolumeObject()
        for (event, elem) in ET.iterparse(fh, events=("start-ns", "end")):
            #_logger.debug("(event, elem) = " + repr((event, elem)))
            if event == "start-ns":
                d.add_namespace(*elem)
            elif event == "end":
                qn = Objects._qsplit(elem.tag)
                if qn[1] in ["fileobject", "original_fileobject"]:
                    nfi = Objects.FileObject()
                    nfi.populate_from_Element(elem)
                    nfi.partition = sample_path_index + 1
                    v.append(nfi)
        d.append(v)
    d.print_dfxml()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
