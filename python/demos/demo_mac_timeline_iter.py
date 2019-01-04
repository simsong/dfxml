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

# produce a MAC-times timeline using the iterative DFXML interface.
# works under either Python2 or Python3

import os
import sys

sys.path.append( os.path.join(os.path.dirname(__file__), ".."))
import dfxml

def main():
    if len(sys.argv) < 2:
        print("Usage: {} <filename.xml>".format(sys.argv[0]))
        exit(1)

    timeline = []

    for fi in dfxml.iter_dfxml( xmlfile=open(sys.argv[1],"rb") ):
        if fi.mtime()!=None: timeline.append([fi.mtime(),fi.filename()," modified"])
        if fi.crtime()!=None: timeline.append([fi.crtime(),fi.filename()," created"])
        if fi.ctime()!=None: timeline.append([fi.ctime(),fi.filename()," changed"])
        if fi.atime()!=None: timeline.append([fi.atime(),fi.filename()," accessed"])

    timeline.sort()

    for record in timeline:
        print("\t".join( map(str, record)) )

if __name__ == "__main__":
    main()
