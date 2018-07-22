
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

import sys
import logging
import os
import copy

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

def test_all():
    t0 = Objects.TimestampObject()
    t0.name = "mtime"
    t0.prec = "2s"

    t1 = copy.deepcopy(t0)

    assert t0 == t1

    t0e = t0.to_Element()
    t2 = Objects.TimestampObject()
    t2.populate_from_Element(t0e)

    assert t0 == t2

    t2.prec = "100"

    assert t0 != t2
