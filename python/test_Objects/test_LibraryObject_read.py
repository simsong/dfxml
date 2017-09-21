
"""
Run test against DFXML file generatd by the _write counterpart script.
"""

import logging
import os
import sys

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(os.path.basename(__file__))

import Objects

dobj = Objects.parse(sys.argv[1])

_logger.debug("dobj.creator_libraries = %r." % dobj.creator_libraries)

assert Objects.LibraryObject("libfoo", "1.2.3") in dobj.creator_libraries
assert Objects.LibraryObject("libbaz", "4.5") in dobj.build_libraries

found = None
for library in dobj.creator_libraries:
    if library.relaxed_eq(Objects.LibraryObject("libfoo")):
        found = True
        break
assert found
