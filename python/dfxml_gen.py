#!/usr/bin/env python3
#
# dfxml_gen.py: Generate DFXML
#
import sys
import os
import time

import xml.etree.ElementTree as ET
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

    def prettyprint(self):
        import xml.dom.minidom
        return xml.dom.minidom.parseString( self.asString()).toprettyxml(indent='  ')

if __name__=="__main__":
    dfxml = DFXMLWriter()
    dfxml.timestamp("first")
    dfxml.timestamp("second")
    dfxml.done()
    dfxml.comment("Thanks")
    print(dfxml.prettyprint())
