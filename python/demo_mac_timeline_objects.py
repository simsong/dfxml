#!/usr/bin/env python
# produce a MAC-times timeline using the DFXML Objects interface.
# works under either Python2 or Python3
import Objects
import sys

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
