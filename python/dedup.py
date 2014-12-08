#!/usr/bin/python
#
# dedup  - detect and optionally remove duplicates based on a DFXML file

import os,dfxml,xml

class dedup:
    def __init__(self):
        from collections import defaultdict
        self.seen = defaultdict(list)
        self.files = 0
        self.md5s = 0

    def process(self,fi):
        self.files += 1
        if fi.md5():
            self.seen[fi.md5()].append(fi.filename())
            self.md5s += 1

    def find_dups(self,cb=None):
        for (md5,names) in self.seen.items():
            if cb and len(names)>1:
                cb(names)

    def report(self,func,cb):
        for (md5,names) in self.seen.items():
            if func(names): cb(names)

def process_dups(names):
    print("dups: ",names)

if __name__=="__main__":
    from argparse import ArgumentParser
    global options

    parser = ArgumentParser()
    parser.add_argument("dfxml",type=str)
    parser.add_argument("--verbose",action="store_true")
    parser.add_argument("--prefix",type=str,help="Only output files with the given prefix")
    parser.add_argument("--distinct",action='store_true',help='Report the distinct files')
    parser.add_argument("--dups",action='store_true',help='Report the files that are dups, and give dup count')
    args = parser.parse_args()

    dobj = dedup()

    try:
        dfxml.read_dfxml(open(args.dfxml,'rb'),callback=dobj.process)
    except xml.parsers.expat.ExpatError:
        pass

    print("Total files: {:,}  total MD5s processed: {:,}  Unique MD5s: {:,}".format(dobj.files,dobj.md5s,len(dobj.seen)))

    if args.distinct:
        def report_distinct(names):
            if args.prefix and not names[0].startswith(args.prefix): return
            print("distinct: ",names[0])
        dobj.report(lambda names:len(names)==1,report_distinct)

    if args.dups:
        def report_dups(names):
            for name in names:
                if not args.prefix or name.startswith(args.prefix):
                    print("dups: {} {}".format(name,len(names)))
        dobj.report(lambda names:len(names)>1,report_dups)

