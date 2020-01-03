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

__version__ = "0.1.0"

import os
import sys
import logging

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

import libtest

_logger = logging.getLogger(os.path.basename(__file__))

def test_empty_object():
    dobj = Objects.DFXMLObject(version="1.2.0")
    pobj = Objects.PartitionObject()
    dobj.append(pobj)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        pobj_reconst = dobj_reconst.partitions[0]
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_cfreds_macwd_properties():
    """
    These were drawn from a CFReDS sample Mac disk image.
    """
    dobj = Objects.DFXMLObject(version="1.2.0")
    pobj = Objects.PartitionObject()
    dobj.append(pobj)

    pobj.ptype_str = "Apple_Boot"
    pobj.partition_index = 8

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        pobj_reconst = dobj_reconst.partitions[0]
        assert pobj_reconst.ptype_str == "Apple_Boot"
        assert pobj_reconst.partition_index == "8"
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_bsd_disklabel_properties():
    """
    These were drawn from a BSD Disk Label sample image.
    """
    dobj = Objects.DFXMLObject(version="1.2.0")
    pobj_a = Objects.PartitionObject()
    pobj_c = Objects.PartitionObject()
    dobj.append(pobj_a)
    dobj.append(pobj_c)

    pobj_a.partition_index = "a"
    pobj_c.partition_index = "c"

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        pobj_a_reconst = dobj_reconst.partitions[0]
        pobj_c_reconst = dobj_reconst.partitions[1]
        assert pobj_a_reconst.partition_index == "a"
        assert pobj_c_reconst.partition_index == "c"
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)
