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

import logging
import os
import xml.etree.ElementTree as ET
import sys

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

import libtest

# Only register one of these namespaces in ET.
XMLNS_TEST_CLAMSCAN = "file:///opt/local/bin/clamscan"
XMLNS_TEST_UNREGGED = "file:///dev/random"
ET.register_namespace("clam", XMLNS_TEST_CLAMSCAN)

def test_externals():
    _logger = logging.getLogger(os.path.basename(__file__))
    logging.basicConfig(level=logging.DEBUG)

    vobj = Objects.VolumeObject()

    # Try and fail to add a non-Element to the list.
    failed = None
    _logger.debug("Before:  " + repr(vobj.externals))
    try:
        vobj.externals.append(1)
        failed = False
    except TypeError:
        failed = True
    except:
        # There's only one kind of error expected here.  Raise anything else.
        failed = True
        raise
    _logger.debug("After:  " + repr(vobj.externals))
    assert failed
    failed = None

    # Dummy up a non-DFXML namespace element.  This should be appendable.
    e = ET.Element("{%s}scan_results" % XMLNS_TEST_CLAMSCAN)
    e.text = "Clean file system"
    vobj.externals.append(e)

    # Dummy up a DFXML namespace element.  This should not be appendable (the schema specifies other namespaces).
    e = ET.Element("{%s}filename" % Objects.dfxml.XMLNS_DFXML)
    e.text = "Superfluous name"
    _logger.debug("Before:  " + repr(vobj.externals))
    try:
        vobj.externals.append(e)
        failed = False
    except ValueError:
        failed = True
    except:
        failed = True
        raise
    _logger.debug("After:  " + repr(vobj.externals))
    assert failed
    failed = None

    # Add an element with the colon prefix style.
    e = ET.Element("clam:version")
    e.text = "20140101"
    vobj.externals.append(e)

    # Add an element that doesn't have an ET-registered namespace prefix.
    e = ET.Element("{%s}test2" % XMLNS_TEST_UNREGGED)
    e.text = "yes"
    vobj.externals.append(e)

    # Test serialization to Element (file I/O done in separate test).
    s = Objects._ET_tostring(vobj.to_Element()) #TODO Maybe this should be more than an internal function.
    _logger.debug(s)
    if s.find("scan_results") == -1:
        raise ValueError("Serialization did not output other-namespace element 'scan_results'.")
    if s.find("clam:version") == -1:
        raise ValueError("Serialization did not output prefixed element 'clam:version'.")
    if s.find("test2") == -1:
        raise ValueError("Serialization did not output unregistered-prefix element 'test2'.")

    # Test de-serialization.
    vor = Objects.VolumeObject()
    x = ET.XML(s)
    vor.populate_from_Element(x)
    _logger.debug("De-serialized: %r." % vor.externals)
    assert len(vor.externals) == 3

def test_prefixed_externals_round_trip():
    dobj = Objects.DFXMLObject(version="1.2.0")
    vobj = Objects.VolumeObject()
    dobj.append(vobj)

    # Add an element with the qualified style, using the registered-prefix namespace.
    e = ET.Element("{%s}scan_results" % XMLNS_TEST_CLAMSCAN)
    e.text = "Clean file system"
    vobj.externals.append(e)

    # Add an element with the colon prefix style.
    e = ET.Element("clam:version")
    e.text = "20140101"
    vobj.externals.append(e)

    # NOTE: This *does not work* with ElementTree.  ET creates an XML document with the namespace prefix "ns1", but then cannot read that document because "ns1" is a reserved prefix.
    # TODO AJN 2019-11-18: I have not inspected yet whether this is an intended behavior or a bug.
    if False:
        # Add an element with the qualified style, using the unregistered-prefix namespace.
        e = ET.Element("{%s}test2" % XMLNS_TEST_UNREGGED)
        e.text = "yes"
        vobj.externals.append(e)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    vobj_reconst = dobj_reconst.volumes[0]
    try:
        assert len(vobj_reconst.externals) == 2
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

if __name__ == "__main__":
    test_externals()
    test_prefixed_externals_round_trip()

