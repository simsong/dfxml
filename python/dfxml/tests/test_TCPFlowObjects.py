#!/usr/bin/env python

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

import sys
from os.path import dirname,basename,abspath

import TCPFlowObjects

if __name__=="__main__":
    for (event, obj) in TCPFlowObjects.Objects.iterparse(sys.argv[1]):
        if not isinstance(obj, TCPFlowObjects.Objects.FileObject):
            continue
        results = TCPFlowObjects.scanner_results_from_FileObject(obj)
        if len(results) > 0:
            print("Flow name: %r." % obj.filename)
            for result in results:
                result.print_report()
