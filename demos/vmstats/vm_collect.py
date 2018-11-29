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
import subprocess
import urllib.request
import fcntl
import tempfile

# Add the DFXML python module to our path
sys.path.append( os.path.join(os.path.dirname(__file__), "../../python") )

from dfxml.writer import DFXMLWriter

def is_s3file(fname):
    return fname.startswith("s3://")

def aws_instance_id():
    instanceid = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read().decode()
    return instanceid

def getlock(fname):
    fd = os.open(fname,os.O_RDONLY)
    if fd>0:
        try:
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB) # non-blocking
        except IOError:
            raise RuntimeError("Could not acquire lock")
    return fd


def file_exists(fname, debug=False):
    """Return if fname exists. May be a s3: file"""
    if is_s3file(fname):
        cmd = ['aws','s3','ls',fname]
        if args.debug:
            print(" ".join(cmd))
        (out,err) = subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf-8').communicate()
        if err:
            print(err,file=sys.stderr)
            return False
        if not out:
            return False
        return True
    return os.path.exists(fname)
        

def write_process_dfxml_to_file(f,processlist=True,prettyprint=False):
    """Write the DFXML object to file f. If not prettyprint, add a blank line, so the object can be read as a single line"""
    dfxml = DFXMLWriter()
    if processlist:
        dfxml.add_processlist(dfxml.doc)
    dfxml.add_report(dfxml.doc,spark=False,rusage=False)
    dfxml.write(f, prettyprint=prettyprint)
    if not prettyprint:
        f.write("\n")
    f.flush()

if __name__=="__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    import time
    parser = ArgumentParser(description='Report statistics about a VM over time with dfxml, optionally writing back to Amazon S3',formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("fname",help="output filename. May be a S3 URL if ctools is present. $HOSTIP is replaced with the HostIP address.")
    parser.add_argument("--repeat",help="Number of times to repeat",type=int,default=1)
    parser.add_argument("--interval",help="Number of seconds to delay between query",type=float,default=60)
    parser.add_argument("--prettyprint",action='store_true')
    parser.add_argument("--pidfile",help="write PID to the indicated file")
    parser.add_argument("--lockfile",help="Only run if we can grab a lock on LOCKFILE (which we will create if it doesn't exist). Must reside in local file system; may not be an S3 file.")
    parser.add_argument("--runfile",help="Stop running when this file is deleted. May be an S3 file.")
    parser.add_argument("--noprocesslist",action='store_true',help="Exclude processlist")
    parser.add_argument("--s3root",help="If provided, fname is an s3root location. Run in EMR mode",action='store_true')
    parser.add_argument("--bg",help="Run in the background.",action='store_true')
    parser.add_argument("--aws_region", help="specify aws region")
    parser.add_argument("--debug", help="display debug info", action='store_true')
    args   = parser.parse_args()

    if args.debug and args.bg:
        print("--debug overrides --bg")
        args.bg = False

    if args.lockfile:
        if is_s3file(args.lockfile):
            raise ValueError("lockfile may not be an S3 file")
        if not os.path.exists(args.lockfile):
            with open(args.lockfile,"w") as f:
                f.flush()
        try:
            fd = getlock(args.lockfile)
        except RuntimeError as e:
            print("Cannot acquire lock: {}".format(args.lockfile),file=sys.stderr)
            exit(0)
        
    if args.aws_region:
        os.environ['AWS_DEFAULT_REGION'] = args.aws_region

    if args.pidfile:
        with open(args.pidfile,"w") as f:
            f.write(str(os.getpid()))

    if args.s3root:
        f = tempfile.NamedTemporaryFile(mode='a',encoding='utf8',suffix='.dfxml',delete=False)
        timestr = time.strftime("%Y-%m-%d-%H-%M")
        s3fname = f"{args.fname}/node/{aws_instance_id()}/DAS/dfxml-instance-state/dfxml.log.{timestr}.dfxml"
        print(f"recording to {s3fname}")
    else:
        f = open(args.fname,"a")

    if args.debug:
        print("f:",f)
        print("args.bg:",args.bg)

    if args.bg:
        # https://stackoverflow.com/questions/19369671/launching-a-daemon-from-python-then-detaching-the-parent-from-the-child
        # free parent, detach from process group
        pid = os.fork()
        if( pid>0 ):
            exit(0) #parent exits
        # become session leader, process group leader, detach from controlling terminal
        os.setsid()
        # prevent zombie process, make init cleanup
        pid = os.fork()
        if( pid>0 ):
            exit(0) #parent exits

        sys.stdin.close()
        sys.stderr.close()
        sys.stdout.close()

    if args.debug:
        print("Starting up...")
    for i in range(args.repeat):
        # Sleep after the first iteration, not after the last
        if args.runfile and not file_exists(args.runfile, debug=args.debug):
            if debug:
                print(f"runfile {args.runfile} is gone")
            break
        if i>0:
            if args.debug:
                print("Sleeping...")
            time.sleep(args.interval)
            if args.debug:
                print("Wakeup...")
        write_process_dfxml_to_file(f,prettyprint=args.prettyprint,processlist=not args.noprocesslist)
        if is_s3file(args.fname):
            # upload the file to s3
            cmd = ['aws','s3','cp','--quiet',f.name,s3fname]
            if args.debug:
                print(" ".join(cmd))
            subprocess.check_call(cmd)
