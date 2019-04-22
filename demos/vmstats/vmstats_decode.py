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
import shutil
import datetime

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
            rec['rss'] = "{:.0f}MB".format(float(mi[0].get('rss')) / (1024*1024))
        else:
            rec['rss'] = None
        ct = proc.findall("./cpu_times")
        if ct:
            rec['user'] = float(ct[0].get('user'))
            rec['system'] = float(ct[0].get('system'))
        else:
            rec['user'] = rec['system'] = None
        ret.append(rec)

    def keyfunc(rec):
        v1 = 1e10
        if 'user' in rec and type(rec['user'])==float and 'system' in rec and type(rec['system'])==float:
            v1 -= (rec['user'] + rec['system'])
        return (v1, rec['name'])

    ret.sort( key = keyfunc)
    return ret

def html_filename(root):
    fn = root.find(".//host").text + "_" + root.find(".//start_time").text
    fn = fn.replace(":","_").replace(" ","_").replace(".","_")
    return fn+".html"

TEMPLATE_FILE = "vmstats_decode.html"
def html_generate(root, *, prev_fname, next_fname):
    import jinja2 
    import os.path

    stats   = get_stats(root)
    ps_list = list( get_processes(root) )

    vars = {'next_fname' : next_fname,
            'prev_fname' : prev_fname,
            'host' : 'my host',
            'date' : '2018-08-01',
            'ps_list': ps_list, 
            **stats
    }

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
    parser.add_argument("--json", help="Render JSON file and JavaScript HTML files into a new directory")
    args   = parser.parse_args()

    stats = []
    
    if args.html:
        path = args.html
        if os.path.exists(path):
            raise RuntimeError("{}: exists".format(path))
        os.mkdir(path)
        shutil.copy( os.path.join( os.path.dirname(__file__), "skeleton.css"), path)

    if args.json:
        path = args.json
        if not os.path.exists(path):
            os.mkdir(path)
        shutil.copy( os.path.join( os.path.dirname(__file__), "vmstats_json.html"), path)
        shutil.copy( os.path.join( os.path.dirname(__file__), "skeleton.css"), path)

    roots = []
    for fn in args.fname:
        roots.extend( get_dfxml(fn) )

    for i in range(len(roots)):
        root = roots[i]
        if args.plot:
            stats.append( get_stats(root))
        if args.ps:
            for proc in get_processes(root):
                print(proc)
        if args.html:
            with open( os.path.join(path, html_filename(root)), "w") as f:
                prev_fname = html_filename(roots[i-1]) if i > 0 else ""
                next_fname = html_filename(roots[i+1]) if i < len(roots)-1 else ""
                f.write( html_generate( root, prev_fname=prev_fname, next_fname=next_fname ))

        if args.json:
            # Make the JSON file
            data = [{'stats':get_stats(root), 'processes':get_processes(root)} for root in roots]

            def myconverter(o):
                if isinstance(o, datetime.datetime):
                    return o.__str__()

            json_data = json.dumps( data, default = myconverter )
            json_data_len = len(json_data)
            # Now clean the data...
            for slot in data:
                slot['stats']['start_time'] = slot['stats']['start_time'].isoformat()[0:19]
                slot['processes'] = [p for p in slot['processes'] 
                                     if ( (p['user'] and p['user']>1) and 
                                          (p['system'] and p['system']>1)) ]
                for p in slot['processes']:
                    p['user']   = int( p['user'])
                    p['system'] = int( p['system'])

            json_data = json.dumps( data, default = myconverter )
            print("json shrunk by {} to {}".format(json_data_len - len(json_data), len(json_data)))

            # Throw the data into a JSON file
            with open( os.path.join(path, 'data.json'), 'w') as f:
                f.write( json_data )
            
            # Create a JavaScript file that also defines the data object. We do this because
            # we can load the JavaScript file from the local file system, but not data.json
            with open( os.path.join(path, 'data.js'), 'w') as f:
                f.write( "var data = ")
                f.write( json_data )
                f.write( "\n" );

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
