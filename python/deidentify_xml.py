#!/usr/bin/python
#
# deidentify_xml.py:
# Given XML for a disk, remove information that might be personally identifying from filenames.
# remember the mapping so that directory names don't get changed.
#
# 2012-10-27 slg - updated to Python3

private_dirs = ["home/","usr/home","Users"]
ok_top_paths_win = ["program files/","System","Windows"]
ok_top_paths_mac = ["bin/","usr","etc","private","applications","developer",'bin','sbin','lib','dev']
ok_top_paths = ok_top_paths_win + ok_top_paths_mac + ['$orphanfiles']
acceptable_extensions = ["exe","dll","sys","com","hlp"]

import os.path, os, sys

partdir = {}
def sanitize_part(part):
    """Sanitize a part of a pathname in a consistent manner"""
    if part not in partdir:
        partdir[part] = "P%07d" % (len(partdir)+1)
    return partdir[part]

def sanitize_filename(fname):
    """Given a filename, sanitize each part and return it."""
    ofn = fname
    jfn = fname
    if jfn[0]=='/': jfn=jfn[1:]
    pathok = False
    for p in ok_top_paths:
        if jfn.lower().startswith(p):
            pathok = True

    if not pathok:
        # if the path is not okay, replace all of the parts
        # and the name up to the .ext
        parts = fname.split("/")
        parts[:-1] = [sanitize_part(s) for s in parts[:-1]]
        (root,ext) = os.path.splitext(parts[-1])
        if ext not in acceptable_extensions:
            parts[-1] = sanitize_part(root) + ext
        fname = "/".join(parts)
    if ofn[0]=='/' and fname[0]!='/':
        fname = "/" + fname
    return fname
    
class xml_sanitizer:
    """Read and write the XML, but sanitize the filename elements."""
    def __init__(self,out):
        self.out = out
        self.cdata = ""
        
    def _start_element(self, name, attrs):
        """ Handles the start of an element for the XPAT scanner"""
        s = ['<',name]
        if attrs:
            for (a,v) in attrs.items():
                if '"' not in v:
                    s += [' ',a,'="',v,'"']
                else:
                    s += [" ",a,"='",v,"'"]
        s += ['>']
        self.out.write("".join(s))
        self.cdata = ""                 # new element

    def _end_element(self, name):
        """Handles the end of an element for the XPAT scanner"""
        if name=="filename":
            self.cdata = sanitize_filename(self.cdata)
        if self.cdata=="\n": self.cdata=""
        self.out.write("".join([self.cdata,'</',name,'>']))
        self.cdata = ""

    def _char_data(self, data):
        """Handles XML data"""
        self.cdata += data

    def process_xml_stream(self,xml_stream):
        "Run the reader on a given XML input stream"
        import xml.parsers.expat
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler  = self._start_element
        p.EndElementHandler    = self._end_element
        p.CharacterDataHandler = self._char_data
        p.ParseFile(xml_stream)

if __name__=="__main__":
    from optparse import OptionParser
    global options
    parser = OptionParser()
    parser.add_option("-t","--test",help='Test a specific pathanme to sanitize')
    (options,args) = parser.parse_args()

    if options.test:
        if os.path.isdir(options.test):
            for (dirpath,dirnames,filenames) in os.walk(options.test):
                for filename in filenames:
                    fn = dirpath+"/"+filename
                    print("%s\n   %s" % (fn,sanitize_filename(fn)))

    x = xml_sanitizer(sys.stdout)
    x.process_xml_stream(open(args[0],'rb'))
    
            
            
