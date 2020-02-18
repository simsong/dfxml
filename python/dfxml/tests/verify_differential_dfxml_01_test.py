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

__version__="0.1.0"

import sys
import sys
import os
import os.path
import logging
import argparse

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append( os.path.join(os.path.dirname(__file__), ".."))

import dfxml.objects as Objects
import make_differential_dfxml

SAMPLES_DIR=os.path.dirname(__file__)+"../../../samples"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    tempxml1_path = __file__ + "-test1.xml"
    tempxml2_path = __file__ + "-test2.xml"

    _logger = logging.getLogger(os.path.basename(__file__))
    _logger.info("Building iteration: 0.")
    d_in_memory = make_differential_dfxml.make_differential_dfxml(
      os.path.join(SAMPLES_DIR, "difference_test_0.xml"),
      os.path.join(SAMPLES_DIR, "difference_test_1.xml")
    )

    #Write and read the DFXML stream a couple times to ensure consistent serialization and deserialization
    with open(tempxml1_path, "w") as fh:
        d_in_memory.print_dfxml(output_fh=fh)
    _logger.info("Building iteration: 1.")
    d_from_disk = Objects.parse(tempxml1_path)
    with open(tempxml2_path, "w") as fh:
        d_from_disk.print_dfxml(output_fh=fh)
    _logger.info("Building iteration: 2.")
    d_from_disk_again = Objects.parse(tempxml2_path)

    for (iteration, d) in enumerate((d_in_memory, d_from_disk, d_from_disk_again)):
        _logger.info("Checking iteration: %d." % iteration)
        for o in d:
            #_logger.debug(repr(o))
            if isinstance(o, Objects.FileObject):
                if "deleted" in o.annos:
                    _name = o.original_fileobject.filename
                else:
                    _name = o.filename
                expected_fileobject_diffs = {
                  ("i_am_new.txt"): set([]),
                  ("i_will_be_deleted.txt"): set([]),
                  ("i_will_be_modified.txt"): set(["filesize","mtime","ctime","atime","data_brs","md5","sha1","sha256"]),
                  ("i_will_be_accessed.txt"): set(["atime", "data_brs"])
                }
                if o.diffs != expected_fileobject_diffs[_name]:
                    _logger.info("FAILED: %r." % _name)
                    _logger.info("Expected diffs: %r;" % expected_fileobject_diffs[_name])
                    _logger.info("Received diffs: %r." % o.diffs)
                    assert False
                _logger.info("PASSED: %r." % _name)

    #TODO Once the old idifference.py is retired, remove the Python3-only bit.
    if sys.version_info >= (3,1):
        import summarize_differential_dfxml
        for sortby in "times", "path":
            _logger.info("Summarizing, sorting by %s." % sortby)
            summarize_differential_dfxml.report(d_from_disk_again, sort_by=sortby)
