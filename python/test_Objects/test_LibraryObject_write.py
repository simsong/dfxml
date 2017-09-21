
import logging
import os
import sys

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(os.path.basename(__file__))

import Objects

lobj = Objects.LibraryObject()

_logger.debug("lobj = %r" % lobj)
_logger.debug("lobj.to_Element() = %r" % lobj.to_Element())

dobj = Objects.DFXMLObject()
dobj.add_creator_library(lobj)
dobj.add_creator_library("libfoo", "1.2.3")
dobj.add_creator_library("Python", ".".join(map(str, sys.version_info[0:3]))) #A bit of a bend, but gets the major version information out.
try:
    dobj.add_creator_library("libbar", None)
except ValueError:
    _logger.info("Caught expected value error from passing in incorrect types.")
    pass
dobj.add_build_library("libbaz", "4.5")

with open(sys.argv[1], "w") as fh:
    dobj.print_dfxml(fh)
