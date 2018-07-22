
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
import os.path

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

def test_all():
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

if __name__=="__main__":
    test_all()
    
