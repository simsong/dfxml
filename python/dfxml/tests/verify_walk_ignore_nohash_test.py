#!/usr/bin/env python

import sys

sys.path.append("../..")
import dfxml.objects as Objects

if __name__=="__main__":
    for (event, obj) in Objects.iterparse(sys.argv[1]):
        if not isinstance(obj, Objects.FileObject):
            continue
        for propname in Objects.FileObject._hash_properties:
            if not getattr(obj, propname) is None:
                raise ValueError("Found hash property: %r on %r." % (propname, obj.filename))
