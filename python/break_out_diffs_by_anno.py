#!/usr/bin/env python3

"""
This program reads a DFXML file with differential annotations and produces a table.

Columns: FileObject annotation (is it a new file? renamed? etc.).
Rows: Counts of instances of a property being changed per FileObject annotation.  One row per FileObject direct-child element.
"""

__version__ = "0.1.0"

import Objects
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
