#!/usr/bin/env python3

import sys
import os
import logging

sys.path.append("..")
import Objects
import make_differential_dfxml

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    thisdir = os.path.dirname(__file__)
    d = make_differential_dfxml.make_differential_dfxml(
      os.path.join(thisdir, "../../samples/difference_test_2.xml"),
      os.path.join(thisdir, "../../samples/difference_test_3.xml")
    )
    print(d.to_dfxml(), file=open("junk.xml","w"))
    for o in d:
        logging.debug(repr(o))
        if isinstance(o, Objects.VolumeObject):
            expected_partition_diffs = {
              1048576: set(["_new"]),
              1073741824: set([]),
              2147483648: set(["_modified", "ftype_str"]),
              4294967296: set(["_new"])
            }
            if o.diffs != expected_partition_diffs[o.partition_offset]:
                logging.info("Partition offset: %r;" % o.partition_offset)
                logging.info("Expected: %r;" % expected_partition_diffs[o.partition_offset])
                logging.info("Received: %r." % o.diffs)
                assert False
        else:
            #FileObjects
            pass #TODO
