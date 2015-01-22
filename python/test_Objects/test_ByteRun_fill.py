
import Objects
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=logging.DEBUG)

br = Objects.ByteRun()
_logger.debug("br = %r." % br)

assert br.fill is None

br.fill = b'\x00'
_logger.debug("br.fill = %r." % br.fill)
assert br.fill == b'\x00'

#Catch current implementation decision.
multibyte_failed = None
try:
    br.fill = b'\x00\x01'
except NotImplementedError as e:
    multibyte_failed = True
assert multibyte_failed

br.fill = 0
_logger.debug("br.fill = %r." % br.fill)
assert br.fill == b'\x00'

br.fill = "0"
_logger.debug("br.fill = %r." % br.fill)
assert br.fill == b'\x00'

br.fill = 1
_logger.debug("br.fill = %r." % br.fill)
assert br.fill == b'\x01'
