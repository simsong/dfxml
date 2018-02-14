
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
