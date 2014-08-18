
import Objects
import test_diffing_CellObject
import test_diffing_HiveObject

ro = Objects.RegXMLObject(version="0.2")
ho = Objects.HiveObject()
ho.append(test_diffing_CellObject.co)
ho.append(test_diffing_CellObject.nco)
ro.append(test_diffing_HiveObject.ho)
ro.print_regxml()
