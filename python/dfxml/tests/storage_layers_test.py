#!/usr/bin/env python

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

__version__ = "0.2.0"

import os
import sys
import hashlib
import logging

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

import libtest

_logger = logging.getLogger(os.path.basename(__file__))

TEST_BYTE_STRING_1 = b"Test string 1"
TEST_BYTE_STRING_2 = b"Test string 2"
TEST_BYTE_STRING_3 = b"Test string 3"
TEST_BYTE_STRING_4 = b"Test string 4"

tmphash = hashlib.sha512()
tmphash.update(TEST_BYTE_STRING_1)
TEST_HASH_1 = tmphash.hexdigest()

tmphash = hashlib.sha512()
tmphash.update(TEST_BYTE_STRING_2)
TEST_HASH_2 = tmphash.hexdigest()

tmphash = hashlib.sha512()
tmphash.update(TEST_BYTE_STRING_3)
TEST_HASH_3 = tmphash.hexdigest()

tmphash = hashlib.sha512()
tmphash.update(TEST_BYTE_STRING_4)
TEST_HASH_4 = tmphash.hexdigest()

def test_file_in_non_fs_levels_deep():
    """
    This test follows a simple, vertical storage layer stack, but adds a file at each layer.
    """
    dobj = Objects.DFXMLObject(version="1.2.0")

    # Add file to top-level document.
    fobj_dobj = Objects.FileObject()
    fobj_dobj.alloc_inode = False
    fobj_dobj.alloc_name = False
    fobj_dobj.sha512 = TEST_HASH_1
    dobj.append(fobj_dobj)

    # Add disk image to top-level document.
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    # Add file to disk image.
    fobj_diobj = Objects.FileObject()
    fobj_diobj.alloc_inode = False
    fobj_diobj.alloc_name = False
    fobj_diobj.sha512 = TEST_HASH_2
    diobj.append(fobj_diobj)

    # Add partition system to disk image.
    psobj = Objects.PartitionSystemObject()
    diobj.append(psobj)

    # Add file to partition system.
    fobj_psobj = Objects.FileObject()
    fobj_psobj.alloc_inode = False
    fobj_psobj.alloc_name = False
    fobj_psobj.sha512 = TEST_HASH_3
    psobj.append(fobj_psobj)

    # Add partition to partition system.
    pobj = Objects.PartitionObject()
    psobj.append(pobj)

    # Add file to partition.
    fobj_pobj = Objects.FileObject()
    fobj_pobj.alloc_inode = False
    fobj_pobj.alloc_name = False
    fobj_pobj.sha512 = TEST_HASH_4
    pobj.append(fobj_pobj)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
        psobj_reconst = diobj_reconst.partition_systems[0]
        pobj_reconst = psobj_reconst.partitions[0]
        assert dobj_reconst.files[0].sha512 == TEST_HASH_1
        assert diobj_reconst.files[0].sha512 == TEST_HASH_2
        assert psobj_reconst.files[0].sha512 == TEST_HASH_3
        assert pobj_reconst.files[0].sha512 == TEST_HASH_4
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_file_in_non_fs_levels_flat():
    """
    This test follows a simple, horizontal storage layer stack (every container attached to top document object), and adds a file for each container.
    """
    dobj = Objects.DFXMLObject(version="1.2.0")

    # Add file to top-level document.
    fobj_dobj = Objects.FileObject()
    fobj_dobj.alloc_inode = False
    fobj_dobj.alloc_name = False
    fobj_dobj.sha512 = TEST_HASH_1
    dobj.append(fobj_dobj)

    # Add disk image.
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    # Add file to disk image.
    fobj_diobj = Objects.FileObject()
    fobj_diobj.alloc_inode = False
    fobj_diobj.alloc_name = False
    fobj_diobj.sha512 = TEST_HASH_2
    diobj.append(fobj_diobj)

    # Add partition system.
    psobj = Objects.PartitionSystemObject()
    dobj.append(psobj)

    # Add file to partition system.
    fobj_psobj = Objects.FileObject()
    fobj_psobj.alloc_inode = False
    fobj_psobj.alloc_name = False
    fobj_psobj.sha512 = TEST_HASH_3
    psobj.append(fobj_psobj)

    # Add partition.
    pobj = Objects.PartitionObject()
    dobj.append(pobj)

    # Add file to partition.
    fobj_pobj = Objects.FileObject()
    fobj_pobj.alloc_inode = False
    fobj_pobj.alloc_name = False
    fobj_pobj.sha512 = TEST_HASH_4
    pobj.append(fobj_pobj)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
        psobj_reconst = dobj_reconst.partition_systems[0]
        pobj_reconst = dobj_reconst.partitions[0]
        assert dobj_reconst.files[0].sha512 == TEST_HASH_1
        assert diobj_reconst.files[0].sha512 == TEST_HASH_2
        assert psobj_reconst.files[0].sha512 == TEST_HASH_3
        assert pobj_reconst.files[0].sha512 == TEST_HASH_4
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_solaris_ps_in_partition():
    dobj = Objects.DFXMLObject(version="1.2.0")

    psobj_outer = Objects.PartitionSystemObject()
    dobj.append(psobj_outer)

    # Add file to outer partition system.
    fobj_psobj_outer = Objects.FileObject()
    fobj_psobj_outer.alloc_inode = False
    fobj_psobj_outer.alloc_name = False
    fobj_psobj_outer.sha512 = TEST_HASH_1
    psobj_outer.append(fobj_psobj_outer)

    pobj = Objects.PartitionObject()
    psobj_outer.append(pobj)

    # Add file to partition.
    fobj_pobj = Objects.FileObject()
    fobj_pobj.alloc_inode = False
    fobj_pobj.alloc_name = False
    fobj_pobj.sha512 = TEST_HASH_2
    pobj.append(fobj_pobj)

    psobj_inner = Objects.PartitionSystemObject()
    pobj.append(psobj_inner)

    # Add file to inner partition system.
    fobj_psobj_inner = Objects.FileObject()
    fobj_psobj_inner.alloc_inode = False
    fobj_psobj_inner.alloc_name = False
    fobj_psobj_inner.sha512 = TEST_HASH_3
    psobj_inner.append(fobj_psobj_inner)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        psobj_outer_reconst = dobj_reconst.partition_systems[0]
        pobj_reconst = psobj_outer_reconst.partitions[0]
        psobj_inner_reconst = pobj_reconst.partition_systems[0]
        assert psobj_outer_reconst.files[0].sha512 == TEST_HASH_1
        assert pobj_reconst.files[0].sha512 == TEST_HASH_2
        assert psobj_inner_reconst.files[0].sha512 == TEST_HASH_3
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_hfsplus_in_hfs():
    dobj = Objects.DFXMLObject(version="1.2.0")
    vobj_outer = Objects.VolumeObject()
    vobj_outer.ftype_str = "hfs"
    dobj.append(vobj_outer)

    vobj_inner = Objects.VolumeObject()
    vobj_inner.ftype_str = "hfsplus"
    vobj_outer.append(vobj_inner)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        vobj_outer_reconst = dobj_reconst.volumes[0]
        vobj_inner_reconst = vobj_outer_reconst.volumes[0]
        assert isinstance(vobj_inner_reconst, Objects.VolumeObject)
        assert vobj_outer_reconst.ftype_str == "hfs"
        assert vobj_inner_reconst.ftype_str == "hfsplus"
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_disk_image_in_file_system():
    dobj = Objects.DFXMLObject(version="1.2.0")

    vobj = Objects.VolumeObject()
    vobj.ftype_str = "iso9660"
    dobj.append(vobj)

    fobj_vobj = Objects.FileObject()
    fobj_vobj.sha512 = TEST_HASH_1
    vobj.append(fobj_vobj)

    diobj = Objects.DiskImageObject()
    vobj.append(diobj)

    fobj_diobj = Objects.FileObject()
    fobj_diobj.alloc_inode = False
    fobj_diobj.alloc_name = False
    fobj_diobj.sha512 = TEST_HASH_2
    diobj.append(fobj_diobj)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        vobj_reconst = dobj_reconst.volumes[0]
        diobj_reconst = vobj_reconst.disk_images[0]
        assert vobj_reconst.files[0].sha512 == TEST_HASH_1
        assert diobj_reconst.files[0].sha512 == TEST_HASH_2
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)
