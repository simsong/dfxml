#!/usr/bin/env python3

# This software was developed at the National Institute of Standards
# and Technology in whole or in part by employees of the Federal
# Government in the course of their official duties. Pursuant to
# title 17 Section 105 of the United States Code portions of this
# software authored by NIST employees are not subject to copyright
# protection and are in the public domain. For portions not authored
# by NIST employees, NIST has been granted unlimited rights. NIST
# assumes no responsibility whatsoever for its use by other parties,
# and makes no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

"""
This program reads a DFXML file with differential annotations and produces a table.

Columns: FileObject annotation (is it a new file? renamed? etc.).
Rows: Counts of instances of a property being changed per FileObject annotation.  One row per FileObject direct-child element.
"""

__version__ = "0.1.0"

import dfxml.objects as Objects
import sys
import collections

def main():
    #Key: (annotation, histogram)
    hist = collections.defaultdict(int)
    for (event, obj) in Objects.iterparse(sys.argv[1]):
        if event != "end" or not isinstance(obj, Objects.FileObject):
            continue
        #Loop through annotations
        for anno in obj.annos:
            #Loop through diffs
            for diff in obj.diffs:
                hist[(anno, diff)] += 1

    annos = Objects.FileObject._diff_attr_names.keys()
    print("""
<table>
  <thead>
    <tr>
      <th>Property</th>
""")
    for anno in annos:
        print("      <th>%s</th>" % anno)
    print("""
    </tr>
  </thead>
  <tfoot></tfoot>
  <tbody>
""")
    for diff in sorted(Objects.FileObject._all_properties):
        print("    <tr>")
        if diff in Objects.FileObject._incomparable_properties:
            continue
        print("      <th style='text-align:left;'>%s</th>" % diff)
        for anno in annos:
            print("      <td>%d</td>" % hist[(anno,diff)])
        print("    </tr>")
    print("""
  </tbody>
</table>
""")
            
if __name__ == "__main__":
    main()
