

import logging
import os

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(os.path.basename(__file__))

import Objects

co = Objects.CellObject()

_logger.debug("co = %r" % co)
_logger.debug("co.to_regxml() = %r" % co.to_regxml())

co.name_type = "v"

#Test value-type tolerance of data_type: should be null, strs and ints.

co.data_type = None
co.data_type = 0
co.data_type = "REG_NONE"
failed = False
try:
    co.data_type = 0.1
except:
    failed = True
assert failed
