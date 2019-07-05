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

"""
This script confirms that the DFXML pip-managed packaging exposes the dfxml package and the objects.py module.
"""

import sys

import dfxml
import dfxml.objects

def nop(x):
    pass

with open(sys.argv[1], "rb") as fh:
    dfxml.read_dfxml(fh, callback=nop)

for (event, obj) in dfxml.objects.iterparse(sys.argv[1]):
    pass
