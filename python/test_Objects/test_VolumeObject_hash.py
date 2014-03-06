#!/usr/bin/env python3

import Objects
import os
import logging

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(os.path.basename(__file__))

s0 = set()

v0 = Objects.VolumeObject()
v1 = Objects.VolumeObject()

s0.add(v0)
s0.add(v1)

_logger.debug("len(s0) = %r" % len(s0))
assert len(s0) == 2

f0 = Objects.FileObject()
f1 = Objects.FileObject()
f0.volume_object = v0
f1.volume_object = v0

s1 = set()
s1.add(f0.volume_object)
s1.add(f1.volume_object)
_logger.debug("len(s1) = %r" % len(s1))
assert len(s1) == 1
