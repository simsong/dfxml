#!/usr/bin/env python

__version__="0.1.0"

import os
import sys

# "dfxml/python" directory where dfxml is the directory where repo is cloned
# should be added to sys.path for when these files are run by themselves from Makefile
dfxml_python_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if dfxml_python_dir not in sys.path:
    sys.path.append(dfxml_python_dir)
# sys.path.append( os.path.join(os.path.dirname(__file__), ".."))
import dfxml.objects as Objects

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    for (event, obj) in Objects.iterparse(args.file):
        if not isinstance(obj, Objects.FileObject):
            continue
        for propname in [ "atime", "ctime", "crtime", "gid", "inode", "mtime", "uid" ]:
            if not getattr(obj, propname) is None:
                if propname == "mtime" and obj.name_type != "d":
                    continue
                raise ValueError("Found property that should have been ignored: %r on %r." % (propname, obj.filename))
