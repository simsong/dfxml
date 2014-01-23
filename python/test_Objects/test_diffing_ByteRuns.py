import Objects
import copy
import logging
import os

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(os.path.basename(__file__))

br = Objects.ByteRun()
br.file_offset = 4128
br.len = 133
brs = Objects.ByteRuns()
brs.append(br)

cbrs = copy.deepcopy(brs)

_logger.debug("brs  = %r." % brs)
_logger.debug("cbrs = %r." % cbrs)
assert cbrs == brs

cbrs[0].file_offset += 133
_logger.debug("cbrs = %r." % cbrs)
assert cbrs != brs
