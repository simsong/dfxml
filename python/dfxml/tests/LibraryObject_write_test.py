
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

__version__="0.1.0"

import sys
import logging
import os

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))

import dfxml
import dfxml.objects as Objects

if __name__=="__main__":

    logging.basicConfig(level=logging.DEBUG)
    _logger = logging.getLogger(os.path.basename(__file__))

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
