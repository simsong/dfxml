
import Objects
import copy
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=logging.DEBUG)

ho = Objects.HiveObject()

ho.mtime = "2010-01-02T03:45:00Z"

hoc = copy.deepcopy(ho)

diffs = hoc.compare_to_other(ho)
_logger.debug(repr(diffs))
assert len(diffs) == 0

hoc.mtime = "2011-01-02T03:45:00Z"

diffs = hoc.compare_to_other(ho)
_logger.debug(repr(diffs))
assert len(diffs) == 1
