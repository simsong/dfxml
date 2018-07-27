#!/usr/bin/env python
# coding=UTF-8
"""dfxinfo.py:
Generates a report about what's up with a DFXML file.
"""

import platform
import os
import os.path
import sys
import time
import xml
import xml.etree
import xml.etree.ElementTree as ET
from collections import defaultdict

import dfxml
import dfxml.fiwalk as fiwalk
import dfxml.histogram as histogram

__version__='0.2.0'

MAXSIZE = 1024*1024*16



class DiskSet:
    """DiskSet maintains a database of the file objects within a disk.
    The entire database is maintained in memory."""
    def __init__(self):
        self.ext_histogram          = histogram()
        self.ext_histogram_distinct = histogram()
        self.fi_by_md5              = dict() # a dictionary of lists

    def uniques(self):
        return len(self.fi_by_md5)

    def pass1(self,fi):
        if fi.is_virtual(): return
        if fi.is_file():
            self.fi_by_md5.setdefault(fi.md5(),[]).append(fi)

    def print_dups_report(self):
        print("Duplicates:")
        # First extract the dups, then sort them
        dups  = filter(lambda a:len(a[1])>1,self.fi_by_md5.items(),)
        dup_bytes = 0
        for (md5hash,fis) in sorted(dups,key=lambda a:a[1][0].filesize(),reverse=True):
            for fi in fis:
                print("{:>16,} {:32} {}".format(fi.filesize(),fi.md5(),fi.filename()))
            print()
            dup_bytes += fis[0].filesize() * (len(fis)-1)
        print("Total duplicate bytes: {:,}".format(dup_bytes))

def get_text(tree,tag):
    try:
        return tree.find(tag).text
    except AttributeError as e:
        return ""

def dfxml_info(fn):
    import statistics 
    try:
        tree = ET.parse(fn)
    except xml.etree.ElementTree.ParseError as e:
        print("corrupt: {}".format(fn))
        return
    command_line    = get_text(tree,".//command_line")
    elapsed_seconds = get_text(tree,".//elapsed_seconds")
    if '.' in elapsed_seconds:
        elapsed_seconds = elapsed_seconds[0:elapsed_seconds.find('.')+2]
    elapsed_seconds += 's' if elapsed_seconds else ' '

    start_time      = get_text(tree,".//start_time")
    if '.' in start_time:
        start_time = start_time[0:start_time.find('.')]
    start_time = start_time.replace("T"," ")
    memory_usage    = ''
    maxrss = tree.findall(".//rusage[@who='RUSAGE_SELF']/maxrss")
    if maxrss:
        memory_usage = '{} MiB'.format(int(maxrss[0].text)//1024)
    print("{}    {} {:>7}   {:>10}".format(command_line,start_time,elapsed_seconds,memory_usage))

    # See if there are timers
    timers = tree.findall("timer")
    times  = defaultdict(list)
    for timer in timers:
        try:
            name = timer.attrib['name']
            elapsed = float(timer.attrib['elapsed'])
            times[name].append(elapsed)
        except KeyError as e:
            continue
    if timers:
        print("Timers:")
        fmt = "   {:>6}   {:>5}  {:>9.4}  {:>9.4}  {:>9.4}"
        print(fmt.format("name","#","min","med.","max"))
        for name in times:
            data = times[name]
            print(fmt.format(name, len(data), min(data), statistics.median(data), max(data)))

            



if __name__=="__main__":
    from argparse import ArgumentParser
    from copy import deepcopy

    parser = ArgumentParser(description='Report information about a DFXML file')
    parser.add_argument('xmlfiles',help='XML files to process',nargs='+')
    parser.add_argument("--files", help="Report on file objects that the DFXML file contains", action='store_true')
    parser.add_argument("--imagefile",help="specifies imagefile to examine; automatically runs fiwalk",nargs='+')

    args = parser.parse_args()
    ds   = DiskSet()

    if args.files:
        dfxml.read_dfxml(xmlfile=open(fn,'rb'),callback=ds.pass1)
        if ds.uniques()>0:
            ds.print_dups_report()
        exit(0)

    for fn in args.xmlfiles:
        dfxml_info(fn)
