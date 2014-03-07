
import Objects
import logging
import os
import xml.etree.ElementTree as ET

_logger = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=logging.DEBUG)

br1 = Objects.ByteRun(img_offset=1, len=1)
br2 = Objects.ByteRun(img_offset=2, len=2)
br3 = Objects.ByteRun(img_offset=4, len=3)

dbr = Objects.ByteRuns()
ibr = Objects.ByteRuns()
nbr = Objects.ByteRuns()

dbr.append(br1)
ibr.append(br2)
nbr.append(br3)

dbr.facet = "data"
ibr.facet = "inode"
nbr.facet = "name"

f1 = Objects.FileObject()
f1.data_brs = dbr
f1.inode_brs = ibr
f1.name_brs = nbr

assert f1.data_brs[0].img_offset == 1
assert f1.inode_brs[0].img_offset == 2
assert f1.name_brs[0].img_offset == 4

e1 = f1.to_Element()
#_logger.debug(f1)
#_logger.debug(ET.tostring(e1))

f2 = Objects.FileObject()

f2.populate_from_Element(e1)
#_logger.debug(f2)

assert f2.data_brs[0].img_offset == 1
assert f2.inode_brs[0].img_offset == 2
assert f2.name_brs[0].img_offset == 4
