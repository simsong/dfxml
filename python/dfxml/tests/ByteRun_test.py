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
import copy
import logging
import hashlib

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

import libtest

_logger = logging.getLogger(os.path.basename(__file__))

TEST_BYTE_STRING = b"test"

def test_fill():
    _logger = logging.getLogger(os.path.basename(__file__))
    logging.basicConfig(level=logging.DEBUG)

    br = Objects.ByteRun()
    _logger.debug("br = %r." % br)

    assert br.fill is None

    br.fill = b'\x00'
    _logger.debug("br.fill = %r." % br.fill)
    assert br.fill == b'\x00'

    #Catch current implementation decision.
    multibyte_failed = None
    try:
        br.fill = b'\x00\x01'
    except NotImplementedError as e:
        multibyte_failed = True
    assert multibyte_failed

    br.fill = 0
    _logger.debug("br.fill = %r." % br.fill)
    assert br.fill == b'\x00'

    br.fill = "0"
    _logger.debug("br.fill = %r." % br.fill)
    assert br.fill == b'\x00'

    br.fill = 1
    _logger.debug("br.fill = %r." % br.fill)
    assert br.fill == b'\x01'

def _gen_glom_samples(offset_property="img_offset"):
    """
    Generate three contiguous byte runs.
    """
    br0 = Objects.ByteRun()
    br1 = Objects.ByteRun()
    br2 = Objects.ByteRun()

    br0.len = 20
    br1.len = 30
    br2.len = 10

    if offset_property == "img_offset":
        br0.img_offset = 0
        br1.img_offset = 20
        br2.img_offset = 50
    elif offset_property == "fs_offset":
        br0.fs_offset = 0
        br1.fs_offset = 20
        br2.fs_offset = 50
    elif offset_property == "file_offset":
        br0.file_offset = 0
        br1.file_offset = 20
        br2.file_offset = 50

    return (br0, br1, br2)

def test_glomming_simple():
    for offset_property in [
      "img_offset",
      "fs_offset",
      "file_offset"
    ]:
        (br0, br1, br2) = _gen_glom_samples(offset_property)
        br0_br0      = br0 + br0
        br0_br1      = br0 + br1
        br0_br2      = br0 + br2
        br1_br0      = br1 + br0
        br1_br2      = br1 + br2

        try:
            assert br0_br0 is None
        except:
            _logger.debug("br0_br0 = %r." % br0_br0)
            raise

        try:
            assert getattr(br0_br1, offset_property) == 0
            assert br0_br1.len == 50
        except:
            _logger.debug("br0_br1 = %r." % br0_br1)
            raise

        try:
            assert br0_br2 is None
        except:
            _logger.debug("br0_br2 = %r." % br0_br2)
            raise

        try:
            assert br1_br0 is None
        except:
            _logger.debug("br1_br0  = %r." % br1_br0 )
            raise

        try:
            assert getattr(br1_br2, offset_property) == 20
            assert br1_br2.len == 40
        except:
            _logger.debug("br1_br2 = %r." % br1_br2)
            raise

        try:
            br0__br1_br2 = br0 + br1_br2
            assert getattr(br0__br1_br2, offset_property) == 0
            assert br0__br1_br2.len == 60
        except:
            _logger.debug("br0__br1_br2 = %r." % br0__br1_br2)
            raise

        try:
            br0_br1__br2 = br0_br1 + br2
            assert getattr(br0_br1__br2, offset_property) == 0
            assert br0_br1__br2.len == 60
        except:
            _logger.debug("br0_br1__br2 = %r." % br0_br1__br2)
            raise

def test_glom_fragmented_file_outoforder():
    """
    Three contiguous sectors on disk, i0_i1_i2, contain three out-of-order sectors of the file on disk, f0_f2_f1.
    """

    br0 = Objects.ByteRun()
    br1 = Objects.ByteRun()
    br2 = Objects.ByteRun()

    br0.len = 512
    br1.len = 512
    br2.len = 512

    br0.img_offset = 0 * 512
    br1.img_offset = 1 * 512
    br2.img_offset = 2 * 512

    br0.file_offset = 0 * 512
    br1.file_offset = 2 * 512
    br2.file_offset = 1 * 512

    br0_br1 = br0 + br1
    br1_br2 = br1 + br2

    try:
        assert br0_br1 is None
    except:
        _logger.debug("br0_br1 = %r." % br0_br1)
        raise

    try:
        assert br1_br2 is None
    except:
        _logger.debug("br1_br2 = %r." % br1_br2)
        raise

def test_glom_fragmented_file_discontiguous():
    """
    Three out-of-order sectors of the file on disk, f0_f1_f2, are at discontiguous offsets i0, i0+1KiB, i0+1MiB.
    """

    br0 = Objects.ByteRun()
    br1 = Objects.ByteRun()
    br2 = Objects.ByteRun()

    br0.len = 512
    br1.len = 512
    br2.len = 512

    br0.img_offset = 0
    br1.img_offset = br0.img_offset + 2**10
    br2.img_offset = br0.img_offset + 2**20

    br0.file_offset = 0 * 512
    br1.file_offset = 1 * 512
    br2.file_offset = 2 * 512

    br0_br1 = br0 + br1
    br1_br2 = br1 + br2

    try:
        assert br0_br1 is None
    except:
        _logger.debug("br0_br1 = %r." % br0_br1)
        raise

    try:
        assert br1_br2 is None
    except:
        _logger.debug("br1_br2 = %r." % br1_br2)
        raise

def test_glomming_fill():
    (br0, br1, br2) = _gen_glom_samples()

    br0.fill = b'\x00'
    br1.fill = b'\x01'
    br2.fill = b'\x01'

    br0_br1 = br0 + br1
    br1_br2 = br1 + br2

    try:
        assert br0_br1 is None
    except:
        _logger.debug("br0_br1 = %r." % br0_br1)
        raise

    try:
        assert br1_br2.img_offset == 20
        assert br1_br2.len == 40
    except:
        _logger.debug("br1_br2 = %r." % br1_br2)
        raise

def test_hash_properties():
    dobj = Objects.DFXMLObject(version="1.2.0")

    fobj = Objects.FileObject()
    dobj.append(fobj)

    fobj.byte_runs = Objects.ByteRuns()
    br = Objects.ByteRun()
    fobj.byte_runs.append(br)

    fobj.filesize = len(TEST_BYTE_STRING)
    br.len = len(TEST_BYTE_STRING)

    hash_functions = {
      "md5",
      "sha1",
      "sha224",
      "sha256",
      "sha384",
      "sha512"
    }

    # Key: Hash function.
    # Value: Hash of the byte string b"test".
    hash_values = dict()

    for hash_function in sorted(hash_functions):
        hash_object = getattr(hashlib, hash_function)()
        hash_object.update(TEST_BYTE_STRING)
        hash_values[hash_function] = hash_object.hexdigest()
        _logger.debug("hash_values[%r] = %r." % (hash_function, hash_values[hash_function]))

        setattr(fobj, hash_function, hash_values[hash_function])
        setattr(br, hash_function, hash_values[hash_function])

        assert getattr(fobj, hash_function) == hash_values[hash_function]
        assert getattr(br, hash_function) == hash_values[hash_function]

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        fobj_reconst = dobj_reconst.files[0]
        br_reconst = fobj_reconst.byte_runs[0]
        for hash_function in sorted(hash_functions):
            assert getattr(fobj_reconst, hash_function) == hash_values[hash_function]
            assert getattr(br_reconst, hash_function) == hash_values[hash_function]
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_glomming_hash():
    (br0, br1, br2) = _gen_glom_samples()

    hash_object = hashlib.sha512()
    hash_object.update(TEST_BYTE_STRING)
    br0.sha512 = hash_object.hexdigest()

    br0_br1 = br0 + br1

    try:
        assert br0_br1 is None
    except:
        _logger.debug("br0_br1 = %r." % br0_br1)
        raise

