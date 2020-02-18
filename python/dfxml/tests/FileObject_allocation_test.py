
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

def test_all():
    fa1 = Objects.FileObject()
    fa1.alloc = True
    assert fa1.is_allocated() == True

    fa2 = Objects.FileObject()
    fa2.alloc = False
    assert fa2.is_allocated() == False

    fa3 = Objects.FileObject()
    assert fa3.is_allocated() == None

    fin1 = Objects.FileObject()
    fin1.alloc_inode = True
    fin1.alloc_name = True
    assert fin1.is_allocated() == True

    fin2 = Objects.FileObject()
    fin2.alloc_inode = True
    fin2.alloc_name = False
    assert fin2.is_allocated() == False

    fin3 = Objects.FileObject()
    fin3.alloc_inode = True
    fin3.alloc_name = None
    assert fin3.is_allocated() == False

    fin4 = Objects.FileObject()
    fin4.alloc_inode = False
    fin4.alloc_name = True
    assert fin4.is_allocated() == False

    fin5 = Objects.FileObject()
    fin5.alloc_inode = False
    fin5.alloc_name = False
    assert fin5.is_allocated() == False

    fin6 = Objects.FileObject()
    fin6.alloc_inode = False
    fin6.alloc_name = None
    assert fin6.is_allocated() == False

    fin7 = Objects.FileObject()
    fin7.alloc_inode = None
    fin7.alloc_name = True
    assert fin7.is_allocated() == False

    fin8 = Objects.FileObject()
    fin8.alloc_inode = None
    fin8.alloc_name = False
    assert fin8.is_allocated() == False

    fin9 = Objects.FileObject()
    fin9.alloc_inode = None
    fin9.alloc_name = None
    assert fin9.is_allocated() == None

