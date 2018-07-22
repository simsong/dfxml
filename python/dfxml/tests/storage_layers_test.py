#!/usr/bin/env python

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
    dobj = Objects.DFXMLObject(version="1.2.0")

    # Make objects for simple appends.
    diobj_0 = Objects.DiskImageObject()
    psobj_0 = Objects.PartitionSystemObject()
    pobj_0 = Objects.PartitionObject()
    vobj_0 = Objects.VolumeObject()
    vobj_0.ftype_str="hfs"
    fobj_0 = Objects.FileObject()

    # Make objects for more exotic appends.
    psobj_1 = Objects.PartitionSystemObject()
    vobj_1 = Objects.VolumeObject()
    vobj_1.ftype_str = "hfsplus"
    fobj_dobj_1 = Objects.FileObject()
    fobj_dobj_1.alloc_inode = False
    fobj_dobj_1.alloc_name = False
    fobj_psobj_1 = Objects.FileObject()
    fobj_psobj_1.alloc_inode = False
    fobj_psobj_1.alloc_name = False
    fobj_pobj_1 = Objects.FileObject()
    fobj_pobj_1.alloc_inode = False
    fobj_pobj_1.alloc_name = False

    # Do simple appends.
    dobj.append(diobj_0)
    diobj_0.append(psobj_0)
    psobj_0.append(pobj_0)
    pobj_0.append(vobj_0)
    vobj_0.append(fobj_0)

    # Do more exotic appends.
    pobj_0.append(psobj_1)
    vobj_0.append(vobj_1)
    dobj.append(fobj_dobj_1)
    psobj_0.append(fobj_psobj_1)
    pobj_0.append(fobj_pobj_1)


if __name__=="__main__":
    test_all()
    
    
