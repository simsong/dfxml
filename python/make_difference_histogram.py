#!/usr/bin/env python3

"""
This program (-to-be) reads a DFXML file with differential annotations and produces a table.

Columns: FileObject annotation.
Rows: Counts of instances of a property being changed per FileObject annotation.  One row per FileObject direct-child element.
"""

__version__ = "0.0.1"

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
        for anno in obj.diffs:
            if anno[0] != "_":
                continue
            #Loop through diffs
            for diff in obj.diffs:
                hist[(anno, diff)] += 1

    annos = ["_new", "_deleted", "_renamed", "_changed", "_modified"]
    print("""
<table>
  <thead>
    <tr>
""")
    for anno in annos:
        print("      <th>%s</th>" % anno[1:])
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
        for anno in annos:
            print("      <td>%d</td>" % hist[(anno,diff)])
        print("    </tr>")
    print("""
  </tbody>
</table>
""")
            
if __name__ == "__main__":
    main()

raise NotImplementedError("TODO: Implement difference and annotation reading in Objects.py.")
