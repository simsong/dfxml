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

__version__="0.1.0"

import os
import logging
import sys

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

def test_all():
    logging.basicConfig(level=logging.DEBUG)
    _logger = logging.getLogger(os.path.basename(__file__))

    s0 = set()

    v0 = Objects.VolumeObject()
    v1 = Objects.VolumeObject()

    s0.add(v0)
    s0.add(v1)

    _logger.debug("len(s0) = %r" % len(s0))
    assert len(s0) == 2

    f0 = Objects.FileObject()
    f1 = Objects.FileObject()
    f0.volume_object = v0
    f1.volume_object = v0

    s1 = set()
    s1.add(f0.volume_object)
    s1.add(f1.volume_object)
    _logger.debug("len(s1) = %r" % len(s1))
    assert len(s1) == 1
