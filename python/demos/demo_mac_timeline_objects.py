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

# produce a MAC-times timeline using the DFXML Objects interface.
# works under either Python2 or Python3

import os
import sys

sys.path.append( os.path.join(os.path.dirname(__file__), ".."))
import dfxml
import dfxml.objects as Objects


def main():
    if len(sys.argv) < 2:
        print("Usage: {} <filename.xml>".format(sys.argv[0]))
        exit(1)

    timeline = []

    for (event, obj) in Objects.iterparse( sys.argv[1] ):
        #Only work on FileObjects
        if not isinstance(obj, Objects.FileObject):
            continue
        if not obj.mtime is None:  timeline.append([obj.mtime, obj.filename," modified"])
        if not obj.crtime is None: timeline.append([obj.crtime,obj.filename," created"])
        if not obj.ctime is None:  timeline.append([obj.ctime, obj.filename," changed"])
        if not obj.atime is None:  timeline.append([obj.atime, obj.filename," accessed"])

    timeline.sort()

    for record in timeline:
        print("\t".join( map(str, record)) )

if __name__ == "__main__":
    main()
