#!/usr/bin/env python3
#
# dfxml_gen.py: Generate DFXML
#
import sys
import os
import time

import xml.etree.ElementTree as ET

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


class DFXMLWriter:
    def __init__(self):
        import time
        self.t0 = time.time()
        self.tlast = time.time()

        self.dfxml = ET.Element('dfxml')

        import os
        import pwd
        import sys
        import datetime

        ee = ET.SubElement(self.dfxml, 'execution_enviornment')
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
        self.tlast = now

    def done(self):
        import resource
        for who in ['RUSAGE_SELF','RUSAGE_CHILDREN']:
            ru = ET.SubElement(self.dfxml, 'rusage', {'who':who})
            rusage = resource.getrusage(getattr(resource,who))
            rusage_fields = ['utime','stime','maxrss','ixrss','idrss','isrss',
                             'minflt','majflt','nswap','inblock','oublock',
                             'msgsnd','msgrcv','nsignals','nvcsw','nivcsw']

            for i in range(len(rusage_fields)):
                ET.SubElement(ru, rusage_fields[i]).text = str(rusage[i])
            ET.SubElement(ru, 'pagesize').text = str(resource.getpagesize())

    def comment(self,s):
        self.dfxml.insert(len(list(self.dfxml)), ET.Comment(s))

    def asString(self):
        return ET.tostring(self.dfxml).decode('utf-8')

    def write(self,f):
        f.write(self.asString())

    def writeToFile(self,fname):
        self.write(open(fname,"w"))

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
    arg_parser.add_argument("--print",help="Print the output. Default unless --write is specified",action='store_true')
    args = arg_parser.parse_args()
    dfxml = DFXMLWriter()
    dfxml.timestamp("first")
    dfxml.timestamp("second")
    dfxml.add_spark()
    dfxml.done()
    dfxml.comment("Thanks")
    if args.write:
        dfxml.writeToFile(args.write)
    if args.print or not args.write:
        print(dfxml.prettyprint())
