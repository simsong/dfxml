import Objects
import logging
logging.basicConfig(level=logging.DEBUG)

import os
f0 = Objects.FileObject()
f0.populate_from_stat(os.stat(__file__))
logging.debug("f0.to_dfxml() = %r" % f0.to_dfxml())
