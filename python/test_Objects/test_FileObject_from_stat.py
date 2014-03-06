
import Objects
import logging
import os

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(os.path.basename(__file__))

f0 = Objects.FileObject()
f0.populate_from_stat(os.stat(__file__))
_logger.debug("f0.to_dfxml() = %r" % f0.to_dfxml())
