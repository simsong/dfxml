
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
import logging
import os

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml
import dfxml.objects as Objects

def test_all():
    logging.basicConfig(level=logging.DEBUG)
    _logger = logging.getLogger(os.path.basename(__file__))

    v0 = Objects.VolumeObject()

    v0.sector_size = 512
    v0.block_size = 4096
    v0.partition_offset = 32256
    v0.ftype = -1
    assert v0.ftype == -1
    v0.ftype_str = 1
    v0.block_count = 100000
    v0.allocated_only = False
    v0.first_block = 0
    v0.last_block = v0.block_count

    _logger.debug(repr(v0))
    v1 = eval("Objects." + repr(v0))

    e0 = v0.to_Element()
    _logger.debug("e0 = %r" % e0)

    v2 = Objects.VolumeObject()
    v2.populate_from_Element(e0)

    v1.block_size = 512
    v2.partition_offset = v0.partition_offset + v0.block_count*v0.block_size

    d01 = v0.compare_to_other(v1)
    d02 = v0.compare_to_other(v2)

    _logger.debug("d01 = %r" % d01)
    assert d01 == set(["block_size"])

    _logger.debug("d02 = %r" % d02)
    assert d02 == set(["partition_offset"])
