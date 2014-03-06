
import Objects
import logging
import os
import copy

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(os.path.basename(__file__))

t0 = Objects.TimestampObject()
t0.name = "mtime"
t0.prec = "2s"

t1 = copy.deepcopy(t0)

assert t0 == t1

t0e = t0.to_Element()
t2 = Objects.TimestampObject()
t2.populate_from_Element(t0e)

assert t0 == t2

t2.prec = "100"

assert t0 != t2
