#!/usr/bin/env python3
#
# dfxml_gen.py: Generate DFXML
#
import sys
import os
import time
import os
import pwd
import sys
import datetime
import subprocess
import xml.etree.ElementTree as ET
import __main__
import atexit

__version__="0.1"

###
### Code for working with Apache Spark
### 

def json_to_xml(e,val):
    """Turns JSON in val into XML in e"""
    if type(val)==list:
        # A list is just a bunch of values
        l = ET.SubElement(e,'list')
        for v in val:
            json_to_xml(l,v)
        return
    if type(val)==dict:
        # A dict is a bunch of values, each with a key
        d = ET.SubElement(e,'dict')
        for (k,v) in val.items():
            json_to_xml(ET.SubElement(d,k), v)
        return
    if type(val) in [int,str,bool]:
        e.text = str(val)
        return
    raise RuntimeError("don't know how to build '{}'".format(val))

def get_spark_xml(ee):
    ### Connect to SPARK on local host and dump information
    ### Uses requests
    import os
    if "SPARK_HOME" not in os.environ:
        return        # no spark

    try:
        import requests
        import json
    except ImportError:
        return 

    try:
        r = requests.get('http://localhost:4040/api/v1/applications/')
        if r.status_code!=200:
            return
    except requests.exceptions.ConnectionError:
        return
    
    for app in json.loads(r.text):
        app_id   = app['id']
        app_name = app['name']
        e = ET.SubElement(ee,'application',{'id':app_id,'name':app_name})

        attempt_count = 1
        for attempt in app['attempts']:
            e = ET.SubElement(ee,'attempt')
            json_to_xml(e,attempt)
        for param in ['jobs','allexecutors','storage/rdd']:
            r = requests.get('http://localhost:4040/api/v1/applications/{}/{}'.format(app_id,param))
            e = ET.SubElement(ee,param.replace("/","_"))
            json_to_xml(e,json.loads(r.text))
    return 


def git_commit():
    from subprocess import run,PIPE,SubprocessError
    try:
        s = run(['git','rev-parse','HEAD'],stdout=PIPE,encoding='utf-8')
        return s.stdout.strip()
    except SubprocessError as e:
        return ''

class DFXMLWriter:
    def __init__(self,heartbeat=None,filename=None,prettyprint=False,logger=None):
        import time
        self.t0 = time.time()
        self.tlast = time.time()
        self.dfxml = ET.Element('dfxml')
        self.add_DFXML_creator(self.dfxml)
        self.filename = filename
        self.logger = logger
        if self.filename:
            # Set up to automatically write to filename on exit...
            atexit.register(self.exiting,prettyprint=prettyprint)

    def exiting(self,prettyprint=False):
        """Cleanup handling. Run done() and write the output file..."""
        if self.filename:
            self.done()
            self.writeToFilename(self.filename,prettyprint=prettyprint)
            self.filename = None

    def add_DFXML_creator(self,e):
        import __main__
        ee = ET.SubElement(e, 'creator', {'version':'1.0'})
        ET.SubElement(ee, 'program').text    = str(__main__.__file__)
        try:
            ET.SubElement(ee, 'version').text = str(__main__.__version__)
        except AttributeError as e:
            ET.SubElement(ee, 'version').text = ''
        ET.SubElement(ee, 'executable').text = sys.executable
        ET.SubElement(ee, 'git-commit').text = git_commit()
        self.add_DFXML_execution_environment(ee)
        
    def add_DFXML_execution_environment(self,e):
        ee = ET.SubElement(e, 'execution_enviornment')
        uname = os.uname()
        uname_fields = ['os_sysname','host','os_release','os_version','arch']
        for i in range(len(uname_fields)):
            ET.SubElement(ee, uname_fields[i]).text = uname[i]

        ET.SubElement(ee, 'command_line').text = " ".join([sys.executable] + sys.argv)
        ET.SubElement(ee, 'uid').text = str(os.getuid())
        ET.SubElement(ee, 'username').text = pwd.getpwuid(os.getuid())[0]
        ET.SubElement(ee, 'start_time').text = datetime.datetime.now().isoformat()

    def timestamp(self,name):
        now = time.time()
        ET.SubElement(self.dfxml, 'timestamp', {'name':name,
                                                'delta':str(now - self.tlast),
                                                'total':str(now - self.t0)})
        if self.logger:
            self.logger("timestamp name:{}  delta:{:.4}  total:{}".format(name,now-self.tlast,now-self.t0))
        self.tlast = now
        

    def add_usage(self):
        import resource
        for who in ['RUSAGE_SELF','RUSAGE_CHILDREN']:
            ru = ET.SubElement(self.dfxml, 'rusage', {'who':who})
            rusage = resource.getrusage(getattr(resource,who))
            rusage_fields = ['utime','stime','maxrss','ixrss','idrss','isrss',
                             'minflt','majflt','nswap','inblock','oublock',
                             'msgsnd','msgrcv','nsignals','nvcsw','nivcsw']

            for i in range(len(rusage_fields)):
                ET.SubElement(ru, rusage_fields[i]).text = str(rusage[i])
                if rusage_fields[i] in ['maxrss']:
                    self.logger("{}: {}".format(rusage_fields[i],rusage[i]))
            ET.SubElement(ru, 'pagesize').text = str(resource.getpagesize())
        import psutil
        vm = psutil.virtual_memory()
        ru = ET.SubElement(self.dfxml, 'psutil')
        for key in vm.__dir__():
            if key[0]!='_' and key not in ['index','count']:
                ET.SubElement(ru, key).text = str( getattr(vm, key))
        

    def done(self):
        """Call when the program is finish"""
        self.add_usage()
        self.timestamp("done")

    def comment(self,s):
        self.dfxml.insert(len(list(self.dfxml)), ET.Comment(s))
        if self.logger:
            self.logger(s)

    def asString(self):
        return ET.tostring(self.dfxml).decode('utf-8')

    def write(self,f,prettyprint=False):
        if prettyprint:
            f.write(self.prettyprint())
        else:
            f.write(self.asString())

    def writeToFilename(self,fname,prettyprint=False):
        self.write(open(fname,"w"),prettyprint=prettyprint)
            

    def prettyprint(self):
        import xml.dom.minidom
        return xml.dom.minidom.parseString( self.asString()).toprettyxml(indent='  ')

    def add_spark(self):
        dfxml = ET.SubElement(self.dfxml, 'spark')
        get_spark_xml(dfxml)
        return


if __name__=="__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    arg_parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter,
                                description="Demo program. Run DFXML for this program and print the results. If you run it on a system with SPARK, you get the spark") 
    arg_parser.add_argument("--write",help="Specify filename to write XML output to")
    arg_parser.add_argument("--debug",help="Print the output. Default unless --write is specified",action='store_true')
    args = arg_parser.parse_args()
    dfxml = DFXMLWriter()
    dfxml.timestamp("first")
    dfxml.timestamp("second")
    dfxml.add_spark()
    dfxml.done()
    dfxml.comment("Thanks")
    if args.write:
        dfxml.writeToFilename(args.write)
    if args.debug or not args.write:
        print(dfxml.prettyprint())

    # Demonstrate the failure system
    d2 = DFXMLWriter(filename="demo.dfxml",prettyprint=True)
    exit(0)                     # whoops
