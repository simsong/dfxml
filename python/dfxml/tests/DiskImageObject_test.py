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

__version__ = "0.3.0"

import os
import sys
import logging

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

import libtest

_logger = logging.getLogger(os.path.basename(__file__))

ERROR_1 = "Error 1"
ERROR_2 = "Error 2"

def test_empty_object():
    dobj = Objects.DFXMLObject(version="1.2.0")
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_sector_size():
    dobj = Objects.DFXMLObject(version="1.2.0")
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.sector_size = 2048

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
        assert diobj_reconst.sector_size == 2048
        assert diobj.sector_size == diobj_reconst.sector_size
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_error():
    #TODO Bump version when feature branch merged into schema.
    dobj = Objects.DFXMLObject(version="1.2.0+")
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.error = ERROR_1

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
        assert diobj_reconst.error == ERROR_1
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_error_after_partition_system():
    #TODO Bump version when feature branch merged into schema.
    dobj = Objects.DFXMLObject(version="1.2.0+")
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.error = ERROR_1

    psobj = Objects.PartitionSystemObject()
    #TODO This should be uncommented after the branch add_partition_system_error is merged.
    #psobj.error = ERROR_2
    diobj.append(psobj)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
        #TODO This should be uncommented after the branch add_partition_system_error is merged.
        #psobj_reconst = diobj_reconst.partitionsystems[0]
        assert diobj_reconst.error == ERROR_1
        #TODO This should be uncommented after the branch add_partition_system_error is merged.
        #assert psobj_reconst.error == ERROR_2
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_error_after_file_system():
    #TODO Bump version when feature branch merged into schema.
    dobj = Objects.DFXMLObject(version="1.2.0+")
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.error = ERROR_1

    vobj = Objects.VolumeObject()
    vobj.error = ERROR_2
    diobj.append(vobj)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
        vobj_reconst = diobj_reconst.volumes[0]
        assert diobj_reconst.error == ERROR_1
        assert vobj_reconst.error == ERROR_2
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_error_after_file():
    #TODO Bump version when feature branch merged into schema.
    dobj = Objects.DFXMLObject(version="1.2.0+")
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.error = ERROR_1

    fobj = Objects.FileObject()
    fobj.alloc_inode = False
    fobj.alloc_name = False
    fobj.error = ERROR_2
    diobj.append(fobj)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
        fobj_reconst = diobj_reconst.files[0]
        assert diobj_reconst.error == ERROR_1
        assert fobj_reconst.error == ERROR_2
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)
