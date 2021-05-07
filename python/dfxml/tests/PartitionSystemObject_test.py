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
    psobj = Objects.PartitionSystemObject()
    dobj.append(psobj)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        psobj_reconst = dobj_reconst.partition_systems[0]
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_error_element_order():
    #TODO When schema 1.3.0 is released, update version.
    dobj = Objects.DFXMLObject(version="1.2.0+")
    psobj = Objects.PartitionSystemObject()
    fobj = Objects.FileObject()

    psobj.pstype_str = "gpt"

    # The error element should come after the fileobject stream.
    psobj.error = "foo"

    # Add a unallocated file object found floating in the partition system.
    fobj.alloc_inode = False
    fobj.alloc_name = False

    dobj.append(psobj)
    psobj.append(fobj)

    el = dobj.to_Element()

    # Confirm error comes after file stream.
    assert el[-1][0].tag.endswith("pstype_str")
    assert el[-1][-2].tag.endswith("fileobject")
    assert el[-1][-1].tag.endswith("error")

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    psobj_reconst = dobj_reconst.partition_systems[0]
    try:
        assert psobj_reconst.pstype_str == "gpt"
        assert psobj_reconst.error == "foo"
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)
