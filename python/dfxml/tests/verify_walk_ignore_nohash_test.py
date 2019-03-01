#!/usr/bin/env python

__version__="0.1.0"

import sys
import os

# "dfxml/python" directory where dfxml is the directory where repo is cloned
# should be added to sys.path for when these files are run by themselves from Makefile
dfxml_python_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if dfxml_python_dir not in sys.path:
    sys.path.append(dfxml_python_dir)
# sys.path.append( os.path.join(os.path.dirname(__file__), ".."))
import dfxml.objects as Objects

if __name__=="__main__":
    for (event, obj) in Objects.iterparse(sys.argv[1]):
        if not isinstance(obj, Objects.FileObject):
            continue
        for propname in Objects.FileObject._hash_properties:
            if not getattr(obj, propname) is None:
                raise ValueError("Found hash property: %r on %r." % (propname, obj.filename))
