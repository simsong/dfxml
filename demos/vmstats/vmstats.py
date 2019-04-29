#!/usr/bin/env python3
#
# A tool for collecting stats about a system using DFXML.
# Specifically captures: uptime, current load, all running processes and their memory

import os
import os.path
import sys
import xml.etree.ElementTree as ET
import psutil
import time

sys.path.append( os.path.join(os.path.dirname(__file__), "../../python") )

from dfxml.writer import DFXMLWriter

# Here are the attribs for psutil.Process:
# ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_create_time', '_exe', '_gone', '_hash', '_ident', '_init', '_last_proc_cpu_times', '_last_sys_cpu_times', '_name', '_oneshot_inctx', '_pid', '_ppid', '_proc', '_send_signal', 'as_dict', 'children', 'cmdline', 'connections', 'cpu_percent', 'cpu_times', 'create_time', 'cwd', 'environ', 'exe', 'gids', 'is_running', 'kill', 'memory_full_info', 'memory_info', 'memory_info_ex', 'memory_maps', 'memory_percent', 'name', 'nice', 'num_ctx_switches', 'num_fds', 'num_threads', 'oneshot', 'open_files', 'parent', 'pid', 'ppid', 'resume', 'send_signal', 'status', 'suspend', 'terminal', 'terminate', 'threads', 'uids', 'username', 'wait']
#
# Here is a sample process as a dict on a MacBook; it has a lot of information!
# {'num_fds': 4, 'memory_percent': 0.06830692291259766, 'uids': puids(real=501, effective=501, saved=501), 'username': 'simsong', 'open_files': None, 'num_ctx_switches': pctxsw(voluntary=140527035280822, involuntary=0), 'memory_full_info': None, 'connections': [], 'create_time': 1533609247.593753, 'nice': 0, 'cpu_percent': 0.0, 'pid': 335, 'ppid': 1, 'memory_info': pmem(rss=11735040, vms=4447862784, pfaults=119522, pageins=12365), 'num_threads': 2, 'exe': '/usr/libexec/lsd', 'status': 'running', 'gids': puids(real=20, effective=20, saved=20), 'cmdline': ['/usr/libexec/lsd'], 'terminal': None, 'cpu_times': pcputimes(user=58.45157888, system=17.160942592, children_user=0, children_system=0), 'environ': {'TMPDIR': '/var/folders/h9/hvn4fx_54_782bl27cmy6gxw0000gn/T/', 'SHELL': '/bin/bash', 'HOME': '/Users/simsong', 'LOGNAME': 'simsong', 'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'XPC_SERVICE_NAME': 'com.apple.lsd', 'USER': 'simsong', 'XPC_FLAGS': '0x9'}, 'memory_maps': None, 'threads': None, 'cwd': '/', 'name': 'lsd'}

# Mem on linux:
#['__add__', '__class__', '__contains__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__getnewargs__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__module__', '__mul__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__rmul__', '__setattr__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '_asdict', '_fields', '_make', '_replace', '_source', 'count', 'data', 'dirty', 'index', 'lib', 'rss', 'shared', 'text', 'vms']

# Define the process attributes that we care about
# Define the ones for which we have sub requirements
# 'uids', , 'memory_info', cpu_times

# <cpu_times>pcputimes(user=38.687571968, system=141.358628864, children_user=0, children_system=0)</cpu_times>


def write_process_dfxml_to_file(fname,prettyprint=False):
    dfxml = DFXMLWriter()
    processlist = ET.SubElement(dfxml.doc,'processlist')
    for p in psutil.process_iter():
        try:
            proc = ET.SubElement(processlist,'process', 
                                 {'pid':str(p.pid), 'ppid':str(p.ppid()), 'uid':str(p.uids().real), 
                                  'euid':str(p.uids().effective), 'create_time': str(p.create_time())})
            try:
                proc.set('name',p.name())
                proc.set('num_fds',str(p.num_fds()))
                proc.set('memory_percent',str(p.memory_percent()))
                proc.set('num_threads',str(p.num_threads()))
                proc.set('cwd',p.cwd())
                ET.SubElement(proc,'cmdline').text = ' '.join( p.cmdline())
                proc.set('cpu_percent', str(p.cpu_percent()))
                mem = p.memory_info_ex()
                try:
                    ET.SubElement(proc,'memory_info', {'rss': str(mem.rss), 'vms':str(mem.vms), 
                                                       'pfaults':str(mem.pfaults), 'pageins':str(mem.pageins)})
                except AttributeError:
                    ET.SubElement(proc,'memory_info', {'rss': str(mem.rss), 'vms':str(mem.vms), 
                                                       'data':str(mem.data), 'dirty':str(mem.dirty),
                                                       'lib':str(mem.lib), 'shared':str(mem.shared),
                                                       'text':str(mem.text) })
                    
                cpu = p.cpu_times()
                ET.SubElement(proc,'cpu_times', {'user': str(cpu.user), 'system':str(cpu.system)})
            except psutil.AccessDenied:
                pass

        except psutil.ZombieProcess as e:
            pass
    dfxml.add_report(dfxml.doc,spark=False,rusage=False)
    with open(fname,"a") as f:
        dfxml.write(f, prettyprint=prettyprint)
        if not prettyprint:
            f.write("\n")

if __name__=="__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    import time
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("fname",help="filename")
    parser.add_argument("--repeat",help="Number of times to repeat",type=int,default=1)
    parser.add_argument("--interval",help="Number of seconds to delay between query",type=float,default=60)
    parser.add_argument("--prettyprint",action='store_true')
    parser.add_argument("--pid",help="write PID to the indicated file")
    args   = parser.parse_args()

    if args.pid:
        with open(args.pid,"w") as f:
            f.write(str(os.getpid()))

    for i in range(args.repeat):
        if i>0:
            time.sleep(args.interval)
        write_process_dfxml_to_file(args.fname,prettyprint=args.prettyprint)
        
