#!/usr/bin/env python3
#
# output stats about a VM using DFXML

import os
import os.path
import sys

sys.path.append( os.path.join(os.path.dirname(__file__), "../python") )

from dfxml.writer import DFXMLWriter

if __name__=="__main__":

    dfxml = DFXMLWriter()
    dfxml.add_report(dfxml.dfxml,spark=False,rusage=False)
    print( dfxml.prettyprint())
