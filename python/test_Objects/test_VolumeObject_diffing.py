
import Objects
import logging

logging.basicConfig(level=logging.DEBUG)

v0 = Objects.VolumeObject()

v0.sector_size = 512
v0.block_size = 4096
v0.partition_offset = 32256
v0.ftype = -1
assert v0.ftype == -1
v0.ftype_str = 1
v0.block_count = 100000
v0.allocated_only = False
v0.first_block = 0
v0.last_block = v0.block_count

logging.debug(repr(v0))
v1 = eval("Objects." + repr(v0))

e0 = v0.to_Element()
logging.debug("e0 = %r" % e0)

v2 = Objects.VolumeObject()
v2.populate_from_Element(e0)

v1.block_size = 512
v2.partition_offset = v0.partition_offset + v0.block_count*v0.block_size

d01 = v0.compare_to_other(v1)
d02 = v0.compare_to_other(v2)

logging.debug("d01 = %r" % d01)
assert d01 == set(["block_size"])

logging.debug("d02 = %r" % d02)
assert d02 == set(["partition_offset"])
