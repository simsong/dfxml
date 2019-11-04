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

__version__ = "0.1.1"

import os
import sys
import logging
import subprocess
import tempfile

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

_logger = logging.getLogger(os.path.basename(__file__))

# TODO This script includes two functions that could stand to be in a shared library supporting the pytest tests.
# * XML Schema conformance.
# * File round-tripping.

def _test_schema_conformance(dfxml_path):
    # Handle the desired error not existing before Python 3.3.
    #   Via: https://stackoverflow.com/a/21368457
    if sys.version_info < (3,3):
        _FileNotFoundError = IOError
    else:
        _FileNotFoundError = FileNotFoundError

    top_srcdir = os.path.join(os.path.dirname(__file__), "..", "..", "..")
    if not os.path.exists(os.path.join(top_srcdir, "dfxml_schema_commit.txt")):
        raise _FileNotFoundError("This script (%r) tries to refer to the top Git-tracked DFXML directory, but could not find it based on looking for dfxml_schema_commit.txt." % os.path.basename(__file__))
    schema_path = os.path.join(top_srcdir, "schema", "dfxml.xsd")
    if not os.path.exists(schema_path):
        raise _FileNotFoundError("Tracked DFXML schema not found.  To retrieve it, run 'make schema-init' in the top-level source directory.")
    command = ["xmllint", "--noout", "--schema", schema_path, dfxml_path]
    try:
        subprocess.check_call(command, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except:
        subprocess.check_call(command)

def _file_round_trip_dfxmlobject(dobj):
    """
    Serializes the DFXMLObject (dobj) to a temporary file.  Parses that temporary file into a new DFXMLObject.
    For debugging review, the temporary file is left in place, and it is the caller's responsibility to delete this file (if OS cleanup is not expected to automatically handle it).

    Returns pair:
    * Path of temporary file.  
    * DFXMLObject, reconstituted from parsing that temporary file.
    """
    tmp_filename = None
    dobj_reconst = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dfxml", delete=False) as out_fh:
            tmp_filename = out_fh.name
            dobj.print_dfxml(output_fh=out_fh)
        _test_schema_conformance(tmp_filename)
        dobj_reconst = Objects.parse(tmp_filename)
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    return (tmp_filename, dobj_reconst)

def test_sector_size():
    dobj = Objects.DFXMLObject(version="1.2.0")
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.sector_size = 2048

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = _file_round_trip_dfxmlobject(dobj)
    diobj_reconst = dobj_reconst.disk_images[0]
    try:
        assert diobj_reconst.sector_size == 2048
        assert diobj.sector_size == diobj_reconst.sector_size
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)
