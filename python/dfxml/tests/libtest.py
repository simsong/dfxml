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

"""
This library provides functions for supporting the unit tests in this directory.
"""

__version__ = "0.1.0"

import os
import sys
import logging
import subprocess
import tempfile

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

_logger = logging.getLogger(os.path.basename(__file__))

def confirm_schema_conformance(dfxml_path):
    """
    This function takes a path to a DFXML file, and tests its conformance to the DFXML schema at the version tracked in this Git repository.
    This function is potentially a NOP - if the schema is not downloaded (with 'make schema-init' run at the top of this repository), then to keep local unit testing operating smoothly, the test *will not* fail because of schema absence.  However, testing in the CI environment *will* use the schema.  If the schema is present, schema conformance will be checked regardless of the environment.

    Environment variables:
    PYTEST_REQUIRES_DFXML_SCHEMA - checked for the string value "1".  Set in .travis.yml.
    """

    # Handle the desired error not existing before Python 3.3.
    #   Via: https://stackoverflow.com/a/21368457
    if sys.version_info < (3,3):
        _FileNotFoundError = IOError
    else:
        _FileNotFoundError = FileNotFoundError

    # Confirm this function is acting from the expected directory relative to the repository root.
    top_srcdir = os.path.join(os.path.dirname(__file__), "..", "..", "..")
    if not os.path.exists(os.path.join(top_srcdir, "dfxml_schema_commit.txt")):
        raise _FileNotFoundError("This script (%r) tries to refer to the top Git-tracked DFXML directory, but could not find it based on looking for dfxml_schema_commit.txt." % os.path.basename(__file__))

    # Use the schema file if it is present.
    #   - Testing in the CI environment should require the file be present.
    #   - Offline testing does not necessarily need to fail if the file wasn't downloaded.
    schema_path = os.path.join(top_srcdir, "schema", "dfxml.xsd")
    if os.path.exists(schema_path):
        command = ["xmllint", "--noout", "--schema", schema_path, dfxml_path]
        try:
            subprocess.check_call(command, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except:
            subprocess.check_call(command)
    else:
        # This variable is set in .travis.yml.
        if os.environ.get("PYTEST_REQUIRES_DFXML_SCHEMA") == "1":
            raise _FileNotFoundError("Tracked DFXML schema not found.  To retrieve it, run 'make schema-init' in the top-level source directory.")

def file_round_trip_dfxmlobject(dobj):
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
        confirm_schema_conformance(tmp_filename)
        dobj_reconst = Objects.parse(tmp_filename)
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    return (tmp_filename, dobj_reconst)
