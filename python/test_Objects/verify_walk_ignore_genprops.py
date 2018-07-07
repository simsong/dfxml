#!/usr/bin/env python

import sys

import Objects

for (event, obj) in Objects.iterparse(sys.argv[1]):
    if not isinstance(obj, Objects.FileObject):
        continue
    for propname in [
      "atime",
      "ctime",
      "crtime",
      "gid",
      "inode",
      "mtime",
      "uid"
    ]:
        if not getattr(obj, propname) is None:
            if propname == "mtime" and obj.name_type != "d":
                continue
            raise ValueError("Found property that should have been ignored: %r on %r." % (propname, obj.filename))
