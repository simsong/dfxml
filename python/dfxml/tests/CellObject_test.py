
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
import sys

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

import logging
import os

def test_all():
    logging.basicConfig(level=logging.DEBUG)
    _logger = logging.getLogger(os.path.basename(__file__))

    co = Objects.CellObject()

    _logger.debug("co = %r" % co)
    _logger.debug("co.to_regxml() = %r" % co.to_regxml())

    co.name_type = "v"

    #Test value-type tolerance of data_type: should be null, strs and ints.

    co.data_type = None
    co.data_type = 0
    co.data_type = "REG_NONE"
    failed = False
    try:
        co.data_type = 0.1
    except:
        failed = True
    assert failed


if __name__=="__main__":
    test_all()

    
