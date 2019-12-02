#!/usr/bin/env python

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

__version__ = "0.1.0"

import os
import logging
import sys
import xml.etree.ElementTree as ET

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

import libtest

ERROR_STRING_V = "Volume test error"
ERROR_STRING_F = "File test error"

XMLNS_TEST_EXTRA = "http://example.org/testextra#"

_logger = logging.getLogger(os.path.basename(__file__))

def test_volume_error_roundtrip_without_file():
    dobj = Objects.DFXMLObject(version="1.2.0")
    vobj = Objects.VolumeObject()
    dobj.append(vobj)

    vobj.error = ERROR_STRING_V

    assert vobj.error == ERROR_STRING_V

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        vobj_reconst = dobj_reconst.volumes[0]
        assert vobj_reconst.error == ERROR_STRING_V
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_file_error_roundtrip():
    dobj = Objects.DFXMLObject(version="1.2.0")
    fobj = Objects.FileObject()
    dobj.append(fobj)

    fobj.error = ERROR_STRING_F

    assert fobj.error == ERROR_STRING_F

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        fobj_reconst = dobj_reconst.files[0]
        assert fobj_reconst.error == ERROR_STRING_F
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_volume_error_roundtrip_with_file():
    dobj = Objects.DFXMLObject(version="1.2.0")
    vobj = Objects.VolumeObject()
    dobj.append(vobj)

    vobj.error = ERROR_STRING_V

    assert vobj.error == ERROR_STRING_V

    fobj = Objects.FileObject()
    vobj.append(fobj)

    fobj.error = ERROR_STRING_F

    assert fobj.error == ERROR_STRING_F
    assert vobj.error == ERROR_STRING_V

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        vobj_reconst = dobj_reconst.volumes[0]
        fobj_reconst = vobj_reconst.files[0]
        assert vobj_reconst.error == ERROR_STRING_V
        assert fobj_reconst.error == ERROR_STRING_F
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_volume_error_roundtrip_with_file_and_extns():
    dobj = Objects.DFXMLObject(version="1.2.0")
    vobj = Objects.VolumeObject()
    dobj.append(vobj)

    ET.register_namespace("testextra", XMLNS_TEST_EXTRA)

    vobj.error = ERROR_STRING_V

    # Dummy up a non-DFXML namespace element.  This should be appendable.
    e = ET.Element("{%s}extra_element" % XMLNS_TEST_EXTRA)
    e.text = "Extra content"
    vobj.externals.append(e)

    # Dummy up a non-DFXML namespace 'error' element.  This should be appendable.
    e = ET.Element("{%s}error" % XMLNS_TEST_EXTRA)
    e.text = "Extra error"
    vobj.externals.append(e)

    assert vobj.error == ERROR_STRING_V

    fobj = Objects.FileObject()
    vobj.append(fobj)

    fobj.error = ERROR_STRING_F

    assert fobj.error == ERROR_STRING_F
    assert vobj.error == ERROR_STRING_V

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        vobj_reconst = dobj_reconst.volumes[0]
        fobj_reconst = vobj_reconst.files[0]
        assert vobj_reconst.error == ERROR_STRING_V
        assert fobj_reconst.error == ERROR_STRING_F
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)
