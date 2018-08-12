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

def get_processes(root):
    ret = []
    for proc in root.findall(".//processlist/process"):
        rec = {'pid': proc.get('pid'),
               'name':proc.get('name')}
        mi = proc.findall("./memory_info")
        if mi:
            rec['rss'] = "{:6.0f}MB".format(float(mi[0].get('rss')) / (1024*1024))
        else:
            rec['rss'] = None
        ct = proc.findall("./cpu_times")
        if ct:
            rec['user'] = float(ct[0].get('user'))
            rec['system'] = float(ct[0].get('system'))
            rec['key'] = (1e10 - (rec['user'] + rec['system']), rec['name'])
        else:
            rec['user'] = rec['system'] = None
            rec['key']  = (1e10, rec['name'])
        ret.append(rec)
    ret.sort( key = lambda rec: rec['key'])
    return ret

def html_filename(root):
    fn = root.find(".//host").text + "_" + root.find(".//start_time").text
    fn = fn.replace(":","_").replace(" ","_").replace(".","_")
    return fn+".html"

TEMPLATE_FILE = "vmstats_decode.html"
def html_generate(root):
    import jinja2 
    import os.path

    ps_list = list( get_processes(root) )

    vars = {'next':'next',
            'prev':'prev',
            'host':'my host',
            'date':'2018-08-01',
            'ps_list': ps_list}

    templateLoader = jinja2.FileSystemLoader(searchpath = os.path.dirname(__file__) )
    templateEnv = jinja2.Environment(loader=templateLoader, undefined=jinja2.StrictUndefined)
    template = templateEnv.get_template(TEMPLATE_FILE)
    return template.render( **vars )


if __name__=="__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    import time
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("fname",nargs="+", help="filename")
    parser.add_argument("--ps", help="Show the processes", action='store_true')
    parser.add_argument("--plot",help="Create a plot")
    parser.add_argument("--html", help="Render HTML files into a new directory")
    args   = parser.parse_args()

    stats = []
    
    if args.html:
        path = args.html
        if os.path.exists(path):
            raise RuntimeError("{}: exists".format(path))
        os.mkdir(path)

    roots = []
    for fn in args.fname:
        roots.extend( get_dfxml(fn) )

    for root in roots:
        if args.plot:
            stats.append( get_stats(root))
        if args.ps:
            for proc in get_processes(root):
                print(proc)
        if args.html:
            fn = os.path.join(path, html_filename(root))
            with open(fn,"w") as f:
                f.write( html_generate( root ))

    if args.plot:
        import datetime
        import matplotlib.pyplot as plt
        t0 = stats[0]['start_time']
        when = [ (st['start_time']-t0).total_seconds() for st in stats]
        cpu  = [ st['cpu_percent']  for st in stats]
        mem  = [ st['mem_percent']  for st in stats]

        plt.plot( when, mem, 'g--', label='memory')
        plt.plot( when, cpu, 'r--', label='cpu')
        plt.legend()
        plt.gcf().autofmt_xdate()     # beautify the x-labels
        plt.xlabel("seconds from start of run")
        plt.ylabel("% of resources utilized\n(lower is better)")
        plt.ylim((0,100.0))
        #plt.show()
        plt.savefig( args.plot )
