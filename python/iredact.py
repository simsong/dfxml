#!/usr/bin/python

# This software was developed in whole or in part by employees of the
# Federal Government in the course of their official duties, and with
# other Federal assistance. Pursuant to title 17 Section 105 of the
# United States Code portions of this software authored by Federal
# employees are not subject to copyright protection within the United
# States. For portions not authored by Federal employees, the Federal
# Government has been granted unlimited rights, and no claim to
# copyright is made. The Federal Government assumes no responsibility
# whatsoever for its use by other parties, and makes no guarantees,
# expressed or implied, about its quality, reliability, or any other
# characteristic.
#
# We would appreciate acknowledgement if the software is used.

"""Redact an image file using a ruleset...

Image Redaction Project.

This program redacts disk image files.

inputs:
    * The disk image file
    * A set of rules that describe what to redact, and how to redact it.

Rule File format:

The readaction command file consists of commands.
Each command has an "condition" and an "action"

  [condition] [action]

Conditions:
  FILENAME <afilename> - a file with the given name
  FILEPAT  <a file pattern> - any file with a given pattern
  DIRNAME  <a directory> - any file in the directory
  MD5 <a md5> - any file with the given md5
  SHA1 <a sha1> - any file with the given sha1
  CONTAINS <a string> - any file that contains <a string>

Actions:
  SCRUB MATCH - Scrubs the pattern where it occurs
  SCRUB SECTOR - Scrubs the block where the pattern occurs
  SCRUB FILE - Scrubs the file in which the pattern occurs

Actions:
   FILL 0x44   - overwrite by filling with character 0x44 ('D')
   ENCRYPT     - encrypts the data
   FUZZ        - fuzz the binary, but not the strings

Examples:

Example file:
===============

MD5 3482347345345 SCRUB FILE
MATCH example@acm.org SCRUB FILE
MATCH foobar SCRUB BLOCK
================================================================
Other actions in file:

KEY 12342343  (an encryption key)
"""


import xml.parsers.expat
import hashlib
import os.path
import dfxml.fiwalk as fiwalk
import re

################################################################
def convert_fileglob_to_re(fileglob):
    regex = fileglob.replace(".","[.]").replace("*",".*").replace("?",".?")
    return re.compile(regex)

class redact_rule:
    """ Instances of this class are objects that can decide whether or not to redact."""
    def __init__(self,line):
        self.line = line
        self.complete = True               # by default, redacts everything
    def should_redact(self,fileobject):
        """Returns True if this fileobject should be redacted"""
        raise ValueError("redact method of redact_rule super class should not be called")
    def __str__(self):
        return "action<"+self.line+">"
    def runs_to_redact(self,fi):
        """Returns the byte_runs of the source which match the rule.
        By default this is the entire object."""
        return fi.byte_runs()


class redact_rule_md5(redact_rule):
    """ redact if the MD5 matches"""
    def __init__(self,line,val):
        redact_rule.__init__(self,line)
        self.md5val = val.lower()
    def should_redact(self,fi):
        return self.md5val == fi.tag('md5')

class redact_rule_sha1(redact_rule):
    """ redact if the SHA1 matches"""
    def __init__(self,line,val):
        redact_rule.__init__(self,line)
        self.sha1val = val.lower()
    def should_redact(self,fi):
        return self.sha1val == fi.tag('sha1')

class redact_rule_filepat(redact_rule):
    def __init__(self,line,filepat):
        import re
        redact_rule.__init__(self,line)
        # convert fileglobbing to regular expression
        self.filepat_re = convert_fileglob_to_re(filepat)
        print("adding rule to redact path "+self.filepat_re.pattern)
    def should_redact(self,fileobject):
        return self.filepat_re.search(fileobject.filename())

class redact_rule_filename(redact_rule):
    def __init__(self,line,filename):
        redact_rule.__init__(self,line)
        self.filename = filename
        print("adding rule to redact filename "+self.filename)
    def should_redact(self,fileobject):
        was = os.path.sep
        os.path.sep = '/'                       # Force Unix filename conventions
        ret = self.filename == os.path.basename(fileobject.filename())
        os.path.sep = was
        return ret

class redact_rule_dirname(redact_rule):
    def __init__(self,line,dirname):
        redact_rule.__init__(self,line)
        self.dirname = dirname
    def should_redact(self,fileobject):
        was = os.path.sep
        os.path.sep = '/'                      # Force Unix filename conventions
        ret = self.dirname == os.path.dirname(fileobject.filename())
        os.path.sep = was
        return ret

class redact_rule_contains(redact_rule):
    def __init__(self,line,text):
        redact_rule.__init__(self,line)
        self.text = text
    def should_redact(self,fileobject):
        return self.text in fileobject.contents()

class redact_rule_string(redact_rule):
    def __init__(self,line,text):
        redact_rule.__init__(self,line)
        self.text = text
        self.complete = False           # doesn't redact the entire file

    def should_redact(self,fileobject):
        return self.text in fileobject.contents()
    def runs_to_redact(self,fi):
        """Overridden to return the byte runs of just the given text"""
        ret = []
        tlen = len(self.text)
        for run in fi.byte_runs():
            (file_offset,run_len,img_offset) = run

            run_content = fi.content_for_run(run)
            offset = 0
            # Now find all the places inside "run"
            # where the text "self.text" appears
            print("looking for '{}' in '{}'".format(self.text,run))
            while offset>=0:
                offset = run.find(self.text,offset)
                if offset>=0:
                    ret.append((file_offset+offset,tlen,img_offset+offset))
                    offset += 1         #
        return ret

"""Not actually a redact rule, but rather a rule for global ignores"""
class ignore_rule():
    def __init__(self):
        self.ignore_patterns = []
    def ignore(self,ignore):
        """Ignores specified files based on a regex"""
        self.ignore_patterns.append(re.compile(convert_fileglob_to_re(ignore)))
        return self
    def should_ignore(self, fi):
        for ig in self.ignore_patterns:
            if ig.search(fi.filename()):
                return True
        return False

################################################################
class redact_action():
    """Instances of this class are objects that specify how a redaction should be done."""
    def redact(self,rule,fileobject,rc):
        """Performs the redaction"""
        raise ValueError("redact method of redact_action super class should not be called")

class redact_action_fill(redact_action):
    """ Perform redaction by filling"""
    def __init__(self,val):
        self.fillvalue = val
    def redact(self,rule,fi,rc):
        for run in rule.runs_to_redact(fi):
            print("   Current run %s " % run)
            rc.imagefile.seek(run.img_offset)
            runlen = run.len
            print("\tFile info - \n\t\tname: %s  \n\t\tclosed: %s \n\t\tposition: %d \n\t\tmode: %s" % ("\\"))
            (rc.imagefile.name, rc.imagefile.closed, rc.imagefile.tell(), rc.imagefile.mode)
            print("   Filling at offset {}, {} bytes with pattern {}".format(run.img_offset,runlen,hex(self.fillvalue)))
            if rc.commit:
                rc.imagefile.seek(run.img_offset)
                rc.imagefile.write(chr(self.fillvalue) * run.len)
                print("   >>COMMIT\n")

class redact_action_encrypt(redact_action):
    """ Perform redaction by encrypting"""
    def redact(self,rule,fileobject,rc):
        for run in rule.runs_to_redact(fileobject):
            print("   encrypting at offset {}, {} bytes with cipher".format(run.img_offset,run.bytes))
            raise ValueError("Didn't write this yet")

class redact_action_fuzz(redact_action):
    """ Perform redaction by fuzzing x86 instructions """
    def redact(self,rule,fileobject,rc):
        '''
        The net effect of this function is that bytes 127-255 are "fuzzed" over
        the range of 159-191, with each series of four bytes
        (e.g. 128-131) to one byte value (e.g. 160).
        '''
        def fuzz(ch):
            o = ord(ch)
            if(o<127):
                r = ch
            else:
                r = chr(((o>>2)+128)%256)
            return r
        print("Redacting with FUZZ: ",fileobject)
        for run in rule.runs_to_redact(fileobject):
            try:
                print("   Fuzzing at offset: %d, can fuzz up to %d bytes " % (run.img_offset,run.len))
                rc.imagefile.seek(run.img_offset)

                # Previously redacted only first 10 bytes, now redacts entire sequence
                #first_ten_bytes = rc.imagefile.read(10)
                run_bytes = rc.imagefile.read(run.len)

                print("\tFile info - \n\t\tname: %s  \n\t\tclosed: %s \n\t\tposition: %d \n\t\tmode: %s" % "\\")
                print(rc.imagefile.name, rc.imagefile.closed, rc.imagefile.tell(), rc.imagefile.mode)
                print("    Fuzzing %d bytes - should be %d" % (len(run_bytes), run.len))
                newbytes = "".join([fuzz(x) for x in run_bytes])
                #debug
                print("new: %i old: %i" % (len(newbytes), run.len))
                assert(len(newbytes)==run.len)
                if rc.commit:
                    rc.imagefile.seek(run.img_offset)
                    rc.imagefile.write(newbytes)
                    print("\n   >>COMMIT")
            except AttributeError:
                print("!AttributeError: no byte run?")


################################################################
class RedactConfig:
    """Class to read and parse a redaction config file"""
    def __init__(self,fn):
        self.cmds = []
        self.commit = False
        self.filename = None
        self.xmlfile = None
        self.ignore_rule = ignore_rule()
        for line in open(fn,"r"):
            if line[0] in '#;': continue       # comment line
            line = line.strip()
            if line=="": continue
            atoms = line.split(" ")
            while "" in atoms: atoms.remove("") # take care of extra spaces
            cmd = atoms[0].lower()
            rule = None
            action = None

            # First look for simple commands

            if cmd=='key':
                self.key = atoms[1]
                continue

            if cmd=="commit":
                self.commit = True
                continue

            if cmd=="imagefile":
                self.imagefile = open(atoms[1],"r+b")
                continue

            if cmd=="xmlfile":
                self.xmlfile = open(atoms[1],"r")
                continue

            if cmd=='ignore':
                self.ignore_rule.ignore(atoms[1])
                continue

            # Now look for commands that are rules

            if cmd=='md5':
                rule = redact_rule_md5(line,atoms[1])
            if cmd=='sha1':
                rule = redact_rule_sha1(line,atoms[1])
            if cmd=='filename':
                rule = redact_rule_filename(line,atoms[1])
            if cmd=='filepat':
                rule = redact_rule_filepat(line,atoms[1])
            if cmd=='contains':
                rule = redact_rule_contains(line,atoms[1])
            if cmd=='string':
                rule = redact_rule_string(line,atoms[1])

            if rule:
                if atoms[2].lower()=='fill':
                    action = redact_action_fill(eval(atoms[3]))
                if atoms[2].lower()=='encrypt':
                    action = redact_action_encrypt()
                if atoms[2].lower()=='fuzz':
                    action = redact_action_fuzz()


            if not rule or not action:
                print("atoms:",atoms)
                print("rule:",rule)
                print("action:",action)
                raise ValueError("Cannot parse: '%s'" % line)
            self.cmds.append((rule,action))

    def need_md5(self):
        for (rule,action) in self.cmds:
            if rule.__class__==redact_rule_md5: return True
        return False

    def need_sha1(self):
        for (rule,action) in self.cmds:
            if rule.__class__==redact_rule_sha1: return True
        return False

    def fiwalk_opts(self):
        "Returns the options that fiwalk needs given the redaction requested."
        opts = "-x"
        if self.need_sha1(): opts = opts+"1"
        if self.need_md5():  opts = opts+"m"
        return opts

    def process_file(self,fileinfo):
        for (rule,action) in self.cmds:
            if rule.should_redact(fileinfo):
                print("Processing file: %s" % fileinfo.filename())

                if self.ignore_rule.should_ignore(fileinfo):
                    print("(Ignoring %s)" % fileinfo.filename())
                    return

                print("")
                print("Redacting ",fileinfo.filename())
                print("Reason:",str(rule))
                print("Action:",action)
                action.redact(rule,fileinfo,self)
                if rule.complete:
                    return                  # only need to redact once!

    def close_files(self):
        if self.imagefile and self.imagefile.closed == False:
            print("Closing file: %s" % self.imagefile.name)
            self.imagefile.close()
        if self.xmlfile and self.xmlfile.closed == False:
            print("Closing file: %s" % self.xmlfile.name)
            self.xmlfile.close()

if __name__=="__main__":
    import sys,time
    from optparse import OptionParser
    from subprocess import Popen,PIPE
    global options

    parser = OptionParser()
    parser.usage = "%prog [options] config-file"
    parser.add_option("-d","--debug",help="prints debugging info",dest="debug")
    (options,args) = parser.parse_args()

    t0 = time.time()
    # Read the redaction configuration file
    rc = RedactConfig(args[0])

    if not rc.imagefile:
        print("Error: a filename must be specified in the redaction config file")
        sys.exit(1)

    fiwalk.fiwalk_using_sax(imagefile=rc.imagefile,xmlfile=rc.xmlfile,callback=rc.process_file)
    t1 = time.time()

    rc.close_files()

    print("Time to run: %d seconds" % (t1-t0))
