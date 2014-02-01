#!/usr/bin/env python3

import sys
import os
import logging

sys.path.append("..")
import Objects
import make_differential_dfxml

_logger = logging.getLogger(os.path.basename(__file__))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    thisdir = os.path.dirname(__file__)
    tempxml1_path = __file__ + "-test1.xml"
    tempxml2_path = __file__ + "-test2.xml"

    _logger.info("Building iteration: 0.")
    d_in_memory = make_differential_dfxml.make_differential_dfxml(
      os.path.join(thisdir, "../../samples/difference_test_0.xml"),
      os.path.join(thisdir, "../../samples/difference_test_1.xml")
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
                  ("i_will_be_modified.txt"): set(["filesize","mtime","ctime","atime","byte_runs","md5","sha1"]),
                  ("i_will_be_accessed.txt"): set(["atime", "byte_runs"])
                }
                if o.diffs != expected_fileobject_diffs[_name]:
                    _logger.info("FAILED: %r." % _name)
                    _logger.info("Expected diffs: %r;" % expected_fileobject_diffs[_name])
                    _logger.info("Received diffs: %r." % o.diffs)
                    assert False
                _logger.info("PASSED: %r." % _name)
