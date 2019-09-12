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
import xml.etree.ElementTree as ET

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects


def test_all():


    _logger = logging.getLogger(os.path.basename(__file__))
    logging.basicConfig(level=logging.DEBUG)

    br1 = Objects.ByteRun(img_offset=1, len=1)
    br2 = Objects.ByteRun(img_offset=2, len=2)
    br3 = Objects.ByteRun(img_offset=4, len=3)

    dbr = Objects.ByteRuns()
    ibr = Objects.ByteRuns()
    nbr = Objects.ByteRuns()

    dbr.append(br1)
    ibr.append(br2)
    nbr.append(br3)

    dbr.facet = "data"
    ibr.facet = "inode"
    nbr.facet = "name"

    f1 = Objects.FileObject()
    f1.data_brs = dbr
    f1.inode_brs = ibr
    f1.name_brs = nbr

    assert f1.data_brs[0].img_offset == 1
    assert f1.inode_brs[0].img_offset == 2
    assert f1.name_brs[0].img_offset == 4

    e1 = f1.to_Element()
    #_logger.debug(f1)
    #_logger.debug(ET.tostring(e1))

    f2 = Objects.FileObject()

    f2.populate_from_Element(e1)
    #_logger.debug(f2)

    assert f2.data_brs[0].img_offset == 1
    assert f2.inode_brs[0].img_offset == 2
    assert f2.name_brs[0].img_offset == 4
