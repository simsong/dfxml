#!/usr/bin/env python3
"""
mem_info.py: report the memory used by a program that wrote results to a dfxml file
"""


import xml.etree.ElementTree as ET
import sys

def fmt(n):
    if args.h:
        for (p,let) in reversed((3,"K"),
                                  (6,"M"),
                                  (9,"G"),
                                  (12,"T"),
                                  (15,"P")):
            if n>10**p:
                return f"{n/10**p}{let}"
    return n
                

def process_dfxml(dfxml):
    root = ET.parse(dfxml)
    start_time = root.find(".//start_time").text[0:19].replace("T"," ")
    command_line = " ".join(root.find(".//command_line").text.split()[1:])
    maxrss = 0
    for e in root.findall(".//rusage/maxrss"):
        maxrss += int(e.text)
    print(start_time,fmt(maxrss),command_line)
        


if __name__=="__main__":
    from argparse import ArgumentParser,ArgumentDefaultsHelpFormatter
    parser = ArgumentParser( formatter_class = ArgumentDefaultsHelpFormatter,
                             description="report memory utilization from DFXML file" ) 
    parser.add_argument("--h", help="human format", action='store_true')
    parser.add_argument("dfxml", nargs='*')
    args   = parser.parse_args()
    bad_files = []
    for fname in args.dfxml:
        try:
            process_dfxml(fname)
        except ET.ParseError as e:
            bad_files.append(fname)
    if bad_files:
        print("Could not read:",file=sys.stderr)
        print("\n".join(bad_files),file=sys.stderr)

