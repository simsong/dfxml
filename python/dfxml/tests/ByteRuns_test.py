
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
import copy

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

def test_all():
    br0 = Objects.ByteRun()
    br0.img_offset = 0
    br0.len = 20

    br1 = Objects.ByteRun()
    br1.img_offset = 20
    br1.len = 30

    br2 = Objects.ByteRun()
    br2.img_offset = 50
    br2.len = 20


    brs_contiguous = Objects.ByteRuns()
    brs_contiguous.append(br0)
    brs_contiguous.append(br1)
    brs_contiguous.append(br2)

    brs_glommed = Objects.ByteRuns()
    brs_glommed.glom(br0)
    brs_glommed.glom(br1)
    brs_glommed.glom(br2)

    brs_discontig = Objects.ByteRuns()
    brs_discontig.glom(br0)
    brs_discontig.glom(br2)

    brs_backward = Objects.ByteRuns()
    brs_backward.glom(br1)
    brs_backward.glom(br0)

    assert len(brs_contiguous) == 3
    assert len(brs_glommed) == 1
    assert len(brs_discontig) == 2
    assert len(brs_backward) == 2

    assert brs_glommed[0].len == 70
    assert brs_backward[0].len == 30
    assert brs_backward[1].len == 20

    br_facet_data = Objects.ByteRuns(facet="data")
    br_facet_name = Objects.ByteRuns(facet="name")
    br_facet_default = Objects.ByteRuns()
    assert br_facet_data == br_facet_default
    assert br_facet_name != br_facet_data
    assert br_facet_name != br_facet_default
