#!/usr/bin/env python3
#
# plot vmstats output

import os
import os.path
import sys
import xml.etree.ElementTree as ET
import psutil
import time
import json
import statistics

sys.path.append( os.path.join(os.path.dirname(__file__), "../python") )
import dfxml

def get_dfxml(fname):
    # Given a file, return dfxml objects
    with open(fname,"r") as f:
        buf = []
        for line in f:
            buf.append(line)
            if "</dfxml>" in line:
                yield ET.fromstring("".join(buf))
                buf=[]
    if buf:
        yield ET.fromstring("".join(buf))
        

def get_stats(root):
    """Return a list of the stats that we care about as a dictionary"""
    import dateutil.parser
    return {"start_time":dateutil.parser.parse(root.find(".//execution_environment/start_time").text),
            "cpu_percent":statistics.mean(json.loads(root.find(".//psutil/cpuinfo").text)),
            "mem_percent":float(root.find(".//virtual_memory/percent").text)}

def ps(root):
    for proc in root.findall(".//processlist/process"):
        print(proc.get('pid'),proc.get('name'),end='')
        mi = proc.findall("./memory_info")
        if mi:
            print( "{:6.0f}MB".format(float(mi[0].get('rss')) / (1024*1024)), end='')
        print("")

if __name__=="__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    import time
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("fname",nargs="+", help="filename")
    parser.add_argument("--ps", help="Show the processes", action='store_true')
    parser.add_argument("--plot",help="Create a plot")
    args   = parser.parse_args()

    plot_stats = []
    
    for fn in args.fname:
        for root in get_dfxml(fn):
            if args.plot:
                plot_stats.append( get_stats(root))
            if args.ps:
                ps(root)

    if args.plot:
        import datetime
        import matplotlib.pyplot as plt
        t0 = plot_stats[0]['start_time']
        when = [ (st['start_time']-t0).total_seconds() for st in stats]
        cpu  = [ st['cpu_percent']  for st in stats]
        mem  = [ st['mem_percent']  for st in stats]

        plt.plot( when, cpu, 'r--', label='cpu')
        plt.plot( when, mem, 'g--', label='memory')
        plt.legend()
        plt.gcf().autofmt_xdate()     # beautify the x-labels
        plt.show()
        plt.saveplot( args.plot )
