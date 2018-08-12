#!/usr/bin/python

# This software was developed at the National Institute of Standards
# and Technology in whole or in part by employees of the Federal
# Government in the course of their official duties. Pursuant to
# title 17 Section 105 of the United States Code portions of this
# software authored by NIST employees are not subject to copyright
# protection and are in the public domain. For portions not authored
# by NIST employees, NIST has been granted unlimited rights. NIST
# assumes no responsibility whatsoever for its use by other parties,
# and makes no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

# generate MD5s for a directory in Digital Forensics XML Output
# Uses dublin core.
# Find out more at http://www.dublincore.org/documents/dc-xml-guidelines/
# http://dublincore.org/documents/dc-citation-guidelines/
# http://jedmodes.sourceforge.net/doc/DC-Metadata/dcmi-terms-for-jedmodes.html
# http://www.ukoln.ac.uk/metadata/dcmi/mixing-matching-faq/

__version__ = '1.0.0'

import sys
import os.path
import hashlib
from xml.sax.saxutils import escape

xmloutputversion = '0.3'
dfxml_ns = {'xmlns':'http://afflib.org/fiwalk/',
         'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance',
         'xmlns:dc':'http://purl.org/dc/elements/1.1/'}


class xml:
    def __init__(self):
        self.stack = []

    def set_outfilename(self,fn):
        self.outfilename = fn
    
    def open(self,f):
        if type(f)==file:
            self.f = f
        if type(f)==str or type(f)==unicode:
            self.f = open(f,'w')
        self.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        
    def dublin_core(self,dc_record):
        self.push('metadata',dfxml_ns,attrib_delim='\n  ')
        for (n,v) in dc_record.iteritems():
            if v!=None:
                self.xmlout(n,v)
        self.pop('metadata')
        self.write('\n')
        
    def provenance(self):
        global args
        if args.allprovenance or \
           args.commandline or \
           args.pythonversion:
            self.push('creator')
            self.xmlout('program', os.path.basename(sys.argv[0]))
            self.xmlout('version', __version__)
            self.push('execution_environment')
            if args.allprovenance or args.commandline:
                self.xmlout('command_line', ' '.join(sys.argv))
            
            if args.allprovenance or args.pythonversion:
                self.xmlout('python_version', sys.version)

            self.pop('execution_environment')
            self.pop('creator')
            self.f.write('\n')

    def push(self,tag,attribs={},attrib_delim=' '):
        """Enter an XML block, with optional attributes on the tag"""
        self.tagout(tag,attribs=attribs,attrib_delim=attrib_delim,newline=True)
        self.stack.append(tag)

    def pop(self,v=None):
        """Leave an XML block"""
        if v: assert v==self.stack[-1]
        self.tagout("/"+self.stack.pop(),newline=True)

    def tagout(self,tag,attribs={},attrib_delim=' ',newline=None):
        """Outputs a plain XML tag and optional attributes"""
        self.f.write("<%s" % tag)
        if attribs:
            self.f.write(" ")
            count = len(attribs)
            for (n,v) in attribs.iteritems():
                self.f.write("%s='%s'" % (n,escape(v)))
                count -= 1
                if count>0: self.f.write(attrib_delim)
        self.f.write(">")
        if newline: self.f.write("\n")

    def xmlout(self,tag,value,attribs={}):
        """Output an XML tag and its value"""
        self.tagout(tag,attribs,newline=False)
        self.write(escape(str(value)))
        self.write("</%s>\n" % tag)

    def write(self,s):
        self.f.write(s)


def xmlout_times(fn,x,fistat):
    global args
    for (time_tag, time_field) in [
      ("mtime",  "st_mtime"),
      ("atime",  "st_atime"),
      ("ctime",  "st_ctime"),
      ("crtime", "st_birthtime")
    ]:
        if time_field in dir(fistat):
            attrs_dict = dict()
            time_data = getattr(fistat,time_field)
            #Format timestamp data
            if args.iso_8601:
                import dfxml
                text_out = str(dfxml.dftime(time_data))
            else:
                attrs_dict["format"] = "time_t"
                text_out = str(time_data)
            x.xmlout(time_tag, text_out, attrs_dict)

def emit_directory(fn,x,partno=None):
    x.push("fileobject")

    if not args.nofilenames:
        if args.stripprefix and fn.startswith(args.stripprefix):
            x.xmlout("filename",fn[ len(args.stripprefix) : ])
        elif args.stripleaddirs and args.stripleaddirs > 0:
            x.xmlout("filename","/".join(fn.split("/")[args.stripleaddirs:]))
        else:
            x.xmlout("filename",fn)

    if not args.nometadata:
        fistat = os.stat(fn)
        if partno:
            x.xmlout("partition",partno)
        x.xmlout("inode",fistat.st_ino)
        x.xmlout("filesize",fistat.st_size)
        xmlout_times(fn,x,fistat)
    
    x.xmlout("name_type", "d")

    if args.addfixml:
        x.write(args.addxml)

    x.pop("fileobject")
    x.write("\n")
    
def hash_file(fn,x,partno=None):
    import hashlib
    
    try:
        f = open(fn)
    except IOError as e:
        sys.stderr.write("%s: %s\n" % (fn,str(e)))
        return

    x.push("fileobject")

    if not args.nofilenames:
        if args.stripprefix and fn.startswith(args.stripprefix):
            x.xmlout("filename",fn[ len(args.stripprefix) : ])
        elif args.stripleaddirs and args.stripleaddirs > 0:
            x.xmlout("filename","/".join(fn.split("/")[args.stripleaddirs:]))
        else:
            x.xmlout("filename",fn)

    if not args.nometadata:
        fistat = os.stat(fn)
        if partno:
            x.xmlout("partition",partno)
        x.xmlout("inode",fistat.st_ino)
        x.xmlout("filesize",fistat.st_size)

        xmlout_times(fn,x,fistat)

    #Distinguish regular files from directories, if directories are requested
    if args.includedirs:
        x.xmlout("name_type", "r")

    if args.addfixml:
        x.write(args.addxml)

    if args.md5:    md5_all  = hashlib.md5()
    if args.sha1:   sha1_all = hashlib.sha1()
    if args.sha256: sha256_all = hashlib.sha256()

    chunk_size = 65536          # default chunk size
    if args.piecewise:
        chunk_size = args.piecewise

    if args.piecewise:
        x.push("byte_runs")
    offset = 0
    read_error = False
    while True:
        buf = ""
        try:
            buf = f.read(chunk_size)
        except:
            warning = "Warning: read() failed.  Cannot produce hash."
            read_error = True
            x.write("<!--")
            x.write(warning)
            x.write("-->\n")
            sys.stderr.write("%s  File: %r\n" % (warning, fn))
            buf = ""
        if buf=="": break

        if args.md5:    md5_all.update(buf)
        if args.sha1:   sha1_all.update(buf)
        if args.sha256: sha256_all.update(buf)

        if args.piecewise:
            x.write("<run file_offset='%d' len='%d'>" % (offset,len(buf)))

            if args.md5:
                md5_part = hashlib.md5()
                md5_part.update(buf)
                x.write("<hashdigest type='MD5'>%s</hashdigest>" % md5_part.hexdigest())

            if args.sha1:
                sha1_part = hashlib.sha1()
                sha1_part.update(buf)
                x.write("<hashdigest type='SHA1'>%s</hashdigest>" % sha1_part.hexdigest())

            if args.sha256:
                sha256_part = hashlib.sha256()
                sha256_part.update(buf)
                x.write("<hashdigest type='SHA256'>%s</hashdigest>" % sha256_part.hexdigest())

            x.write("</run>\n")

        offset += len(buf)

    if args.piecewise:
        x.pop("byte_runs")

    if not read_error:
        if args.md5:
            x.write("<hashdigest type='MD5'>%s</hashdigest>\n" % (md5_all.hexdigest()))
        if args.sha1:
            x.write("<hashdigest type='SHA1'>%s</hashdigest>\n" % (sha1_all.hexdigest()))
        if args.sha256:
            x.write("<hashdigest type='SHA256'>%s</hashdigest>\n" % (sha256_all.hexdigest()))
    x.pop("fileobject")
    x.write("\n")
    

def extract(fn):
    out = sys.stdout
    cdata = None
    def start_element(name,attr):
        global cdata
        if name=='hashdigest':
            try:
                kind = attr['type'].upper()
            except KeyError:
                kind = 'MD5'
                
            if ((kind=='MD5' and args.md5 ) or
                (kind=='SHA1' and args.sha1) or
                (kind=='SHA256' and args.sha256)):
                cdata = ""
        else:
            cdata = None
    def char_data(data):
        global cdata
        if cdata!=None:
            cdata += data
    def end_element(name):
        global cdata
        if cdata!=None:
            out.write(cdata)
            out.write("\n")
            cdata = None

    import xml.parsers.expat
    p = xml.parsers.expat.ParserCreate()
    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_data
    p.ParseFile(open(fn))
    

if(__name__=='__main__'):
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    global args

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.usage =\
"""
 prog [args] file1 [file2...]   --- hash files and produce DFXML
       [args] dir1 [dir2...]     --- hash dirs and produce DFXML

 You can also extract a set of hashes to stdout with:
             [--md5 | --sha1 | --sha256] --extract=filename.xml 

Note: MD5 output is assumed unless another hash algorithm is specified.
"""
    parser.add_argument('--piecewise',help='Specifies size of piecewise hashes',default=0,type=int)
    parser.add_argument('--addfixml',help='Specifies XML to add to each file object (for labeling)')
    parser.add_argument('--sha1',help='Generate sha1 hashes',action='store_true')
    parser.add_argument('--md5',help='Generate MD5 hashes',action='store_true')
    parser.add_argument('--sha256',help='Generate sha256 hashes',action='store_true')
    parser.add_argument('--output',help='Specify output filename (default stdout)')
    parser.add_argument('--extract',help='Specify a DFXML to extract a hash set from')
    parser.add_argument('--iso-8601',help='Format timestamps as ISO-8601 in metadata',action='store_true')
    parser.add_argument('--nometadata',help='Do not include file metadata (times & size) in XML',action='store_true')
    parser.add_argument('--nofilenames',help='Do not include filenames in XML',action='store_true')
    parser.add_argument('--stripprefix',help='Remove matching prefix string from filenames (e.g. "/mnt/diskname" would reduce "/mnt/diskname/foo" to "/foo", and would not affect "/run/mnt/diskname/foo")')
    parser.add_argument('--stripleaddirs',help='Remove N leading directories from filenames (e.g. 1 would reduce "/mnt/diskname/foo" to "mnt/diskname/foo", 2 would reduce the same to "diskname/foo")',default=0,type=int)
    parser.add_argument('--includedirs',help='Include directories alongside files in file system walk output',action='store_true')

    provenance_group = parser.add_argument_group('provenance', 'Options to record execution environment details in the output.')
    provenance_group.add_argument('--allprovenance',help='Include all provenance information requestable in this option group',action='store_true')
    provenance_group.add_argument('--commandline', help='Record command line in output',action='store_true')
    provenance_group.add_argument('--pythonversion', help='Record Python version in output',action='store_true')

    parser.add_argument('--title',help='HASHSET Title')
    parser.add_argument('--description',help='HASHSET Description')
    parser.add_argument('--publisher',help='HASHSET Publisher')
    parser.add_argument('--identifier',help='HASHSET Identifier')
    parser.add_argument('--creator',help='HASHSET Author or Creator')
    parser.add_argument('--accessRights',help='HASHSET Access Rights')
    parser.add_argument('--dateSubmitted',help='HASHSET Submission Date')
    parser.add_argument('--abstract',help='HASHSET Abstract')
    parser.add_argument('--classification',help='HASHSET Classification')
    parser.add_argument('--contact',help='HASHSET Contact if found')
    parser.add_argument('targets',help='What to parse',nargs='+')
    args = parser.parse_args()

    if args.extract:
        extract(args.extract)
        exit(0)

    x = xml()

    if args.output:
        x.open(open(args.output))
    else:
        x.open(sys.stdout)

    # Start the DFXML
    x.push("dfxml",{'xmloutputversion':xmloutputversion})
    x.dublin_core({'dc:type':'Hash Set',
                   'dc:title':args.title,
                   'dc:description':args.description,
                   'dc:publisher':args.publisher,
                   'dc:identifier':args.identifier,
                   'dc:creator':args.creator,
                   'dc:accessRights':args.accessRights,
                   'dc:dateSubmitted':args.dateSubmitted,
                   'dc:abstract':args.abstract,
                   'classification':args.classification,
                   'contactIfFound':args.contact
                   }
                  )
    x.provenance()

    # Generate the hashes

    for (fn_no, fn) in enumerate(args.targets):
        if os.path.isdir(fn):
            for (dirpath,dirnames,filenames) in os.walk(fn):
                if args.includedirs:
                    for dn in dirnames:
                        emit_directory(os.path.join(dirpath,dn),x, fn_no+1)
                for fn in filenames:
                    hash_file(os.path.join(dirpath,fn),x, fn_no+1)
        else:
            hash_file(fn,x)
    x.pop("dfxml")

            
