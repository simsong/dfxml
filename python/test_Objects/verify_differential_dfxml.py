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
    d_in_memory = make_differential_dfxml.make_differential_dfxml(
      os.path.join(thisdir, "../../samples/difference_test_2.xml"),
      os.path.join(thisdir, "../../samples/difference_test_3.xml")
    )
    with open(__file__ + "-test.xml", "w") as fh:
        d_in_memory.print_dfxml(output_fh=fh)
    for o in d_in_memory:
        _logger.debug(repr(o))
        if isinstance(o, Objects.VolumeObject):
            expected_partition_annos = {
              1048576: set(["new"]),
              1073741824: set([]),
              2147483648: set(["new"]),
              4294967296: set(["new"])
            }
            if o.annos != expected_partition_annos[o.partition_offset]:
                _logger.info("Partition offset: %r;" % o.partition_offset)
                _logger.info("Expected: %r;" % expected_partition_annos[o.partition_offset])
                _logger.info("Received: %r." % o.annos)
                _logger.info("Diffs: %r." % o.diffs)
                assert False
        else:
            #FileObjects
            pass #TODO
