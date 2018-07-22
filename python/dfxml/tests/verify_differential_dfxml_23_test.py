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

SAMPLES_DIR="../../../samples"

__version__="0.1.0"

import sys
import sys
import os
import logging

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append( os.path.join(os.path.dirname(__file__), ".."))

import dfxml.objects as Objects
import make_differential_dfxml


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _logger = logging.getLogger(os.path.basename(__file__))

    thisdir = os.path.dirname(__file__)
    tempxml1_path = __file__ + "-test1.xml"
    tempxml2_path = __file__ + "-test2.xml"
    d_in_memory = make_differential_dfxml.make_differential_dfxml(
      os.path.join(thisdir, SAMPLES_DIR+"/difference_test_2.xml"),
      os.path.join(thisdir, SAMPLES_DIR+"/difference_test_3.xml")
    )

    #Write and read the DFXML stream a couple times to ensure consistent serialization and deserialization
    with open(tempxml1_path, "w") as fh:
        d_in_memory.print_dfxml(output_fh=fh)
    d_from_disk = Objects.parse(tempxml1_path)
    with open(tempxml2_path, "w") as fh:
        d_from_disk.print_dfxml(output_fh=fh)
    d_from_disk_again = Objects.parse(tempxml2_path)

    for d in (d_in_memory, d_from_disk, d_from_disk_again):
        for o in d:
            _logger.debug(repr(o))
            if isinstance(o, Objects.VolumeObject):
                expected_partition_annos = {
                  (1048576,"FAT16"): set(["deleted"]),
                  (1073741824,"FAT32"): set([]),
                  (2147483648,"FAT32"): set(["deleted"]),
                  (2147483648,"NTFS"): set(["new"]),
                  (4294967296,"FAT32"): set(["new"])
                }
                if o.annos != expected_partition_annos[(o.partition_offset, o.ftype_str)]:
                    _logger.info("Partition offset: %r;" % o.partition_offset)
                    _logger.info("Partition ftype_str: %r;" % o.ftype_str)
                    _logger.info("Expected: %r;" % expected_partition_annos[o.partition_offset])
                    _logger.info("Received: %r." % o.annos)
                    _logger.info("Diffs: %r." % o.diffs)
                    assert False
            else:
                #FileObjects
                pass #TODO
