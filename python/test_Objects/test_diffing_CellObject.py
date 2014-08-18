
import Objects
import logging
import os

import test_diffing_ByteRuns

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(os.path.basename(__file__))

co = Objects.CellObject()
_logger.debug("co = %r" % co)
_logger.debug("co.to_regxml() = %r" % co.to_regxml())

co.root = 1
co.cellpath = "\\Deleted_root"
co.basename = "Deleted_root"
co.name_type = "k"
co.alloc = 1
co.mtime = "2009-01-23T01:23:45Z"
co.mtime.prec = "100ns"
co.byte_runs = test_diffing_ByteRuns.brs
_logger.debug("co = %r" % co)
_logger.debug("co.to_regxml() = %r" % co.to_regxml())

#Make an Element
coe = co.to_Element()

#Clone
nco = Objects.CellObject()
nco.populate_from_Element(coe)
_logger.debug("nco.to_regxml() = %r" % nco.to_regxml())
diffs = co.compare_to_other(nco)
_logger.debug("diffs = %r" % diffs)
assert co == nco

#Modify
nco.basename = "(Doubled)"
nco.root = False
nco.original_cellobject = co
nco.compare_to_original()
_logger.debug("nco.to_regxml() = %r" % nco.to_regxml())

_logger.debug("nco.diffs = %r" % nco.diffs)
assert nco.diffs == set(["basename", "root"])
