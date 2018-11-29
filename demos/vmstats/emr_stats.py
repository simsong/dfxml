#!/usr/bin/env python3
# -*- mode: python; -*-
"""emr_stats.py provides tools for accessing the statistics that Amazon automatically creates for EMR nodes.
It can also interface with matplotlib.
Unfortunately, much of the data that Amazon writes out is unformatted, so it must be parsed.

The class populates a data model of a Cluster class and a Node
class. Each node has a list of Snapshot classes, which are
dictionaries.

Note that Amazon's documentation uses the terms 'instance' and 'node' interchangably. 

"""

import os
import sys
import json
import getpass
import gzip
import subprocess
from collections import defaultdict
import datetime
import re
import multiprocessing
import time
import pickle
import dateutil.parser

import ctools.s3 as s3
from ctools.s3 import _Key,_Size

# Just grab cluster_info for now.
sys.path.append("/mnt/gits/das-vm-config/bin")
from cluster_info import proxy_on,proxy_off,clusterID

# from this module.
import emr_graph

# 300 threads seems like a lot! But with 60 threads, my system was 78% idle.

THREADS = 300
EMR_LOG_BUCKET_NAME=os.environ['DAS_S3ROOT'].replace("s3://","")+"-logs"

# j-1VYQWTUI84GS2/node/i-069048ddc42e48d6c/daemons/instance-state/instance-state.log-2018-10-26-15-15.gz 

## Fields that may be put in the nodes
DATETIME = 'time'
LOAD_AVERAGE = 'load_average'   # value is the 3 averages
CPU_STATS = 'cpu_stats'
MEM_STATS = 'mem_stats'
ALERTS = 'alerts'
PROCESSES = 'processes'
EMERG = 'EMERG'
ALERT = 'ALERT'
CRIT = 'CRIT' 
ERR  = 'ERR'
WARNING='WARNING'
NOTICE='NOTICE'
CORES = 'CORES'

FIRST_DATE="1980-01-01"
END_DATE="2100-01-01"



################################################################
###
### Data Model

logfilename_re = re.compile(r"log-(\d\d\d\d)-(\d\d)-(\d\d)-(\d\d)-(\d\d)[^\d]")
def date_from_log_filename(filename):
    m = logfilename_re.search(filename)
    if not m:
        raise ValueError("No date in: {}".format(filename))
    return datetime.datetime(int(m.group(1)),int(m.group(2)),int(m.group(3)),
                             int(m.group(4)),int(m.group(5)),0)
    

class Node:
    """Represents information about a specific node (VM)"""

    def __init__(self,instanceID=None,instanceInfo=None,verbose=True):
        self.instanceID   = instanceID
        self.stats        = []     # dictionary by time
        self.s3keys       = dict() # s3 keys that have data for this node, [datestr]=key
        self.instanceInfo = instanceInfo
        self.verbose      = verbose
        if verbose:
            self.vprint   = print
        else:
            self.vprint   = lambda *args, **kwargs: None

    @classmethod
    def stats_for_s3url(self,s3url):
        """Given an S3 URL in the form s3://bucket/key, get the data, decompress it, parse, 
        and return an object. This is a slow process,
        and we will use multithreading to make it run quickly."""
        gzdata = s3.s3open(s3url,'rb',cache=True).read()
        data = gzip.decompress(gzdata).decode('utf-8')
        try:
            obj = extract_instance_state(data)
            return obj
        except SnipError as e:
            print("Snip error processing {}:\n{}\n".format(s3url,e))
            return None

    def download_and_parse_s3keys(self,*,bucket,threads=1,limit=None):
        s3key_dates = self.s3keys.keys()
        self.vprint("Instance {} date range {} - {}  ({} URLs)".format(self.instanceID, min(s3key_dates), max(s3key_dates), len(s3key_dates)))
        
        # Find the keys we are going to download
        download_keys = [f's3://{bucket}/{key}' for key in self.s3keys.values()]
        if limit:
            download_keys = download_keys[0:limit]

        # Get and parse the files, filter out the bad data, and store it all in the stats attribute
        # of the node.
        with multiprocessing.Pool(threads) as p:
            unfiltered_stats = p.map(self.stats_for_s3url, download_keys)
            self.stats = [stat for stat in unfiltered_stats if stat]        

    def addS3Key(self,date,key):
        self.s3keys[date] = key


class Cluster:
    """Represents information for a group of nodes that have a specific clusterID"""
    def __init__(self,clusterID):
        self.clusterID  = clusterID
        self.nodes      = defaultdict(Node) # dictionary by instanceID

    def get_info_from_aws(self):
        """Load cluster stats from Amazon API"""
        self.describe_cluster = describe_cluster(self.clusterID)
        for instanceInfo in list_instances(self.clusterID):
            Ec2InstanceId = instanceInfo['Ec2InstanceId']
            self.nodes[Ec2InstanceId] = Node(Ec2InstanceId,instanceInfo=instanceInfo)

    def info(self):
        print(f"Cluster {self.clusterID} info:")
        for node in self.nodes:
            print(f" NODE: {node}")
    
    def instance_type(self,Ec2InstanceId):
        """Given an InstanceID, return the InstanceType"""
        return self.nodes[Ec2InstanceId].instanceInfo['InstanceType']


################################################################
### 
### Data Extraction Tools
###

def grep(lines,text):
    """Return the line numbers of the lines that contain text"""
    return [number for (number,line) in enumerate(lines) if text in line]


class SnipError(RuntimeError):
    pass

def snip(lines,start_text,end_text,start_count=0,end_count=0,start_offset=0,end_offset=0):
    """Return the lines are between start_text and end_text (do not include end_text).
    If more than one line has the text, generate an error"""
    l0 = grep(lines,start_text)
    if not l0:
        raise SnipError("start_text '{}' not found".format(start_text))

    l1 = grep(lines,end_text)
    if not l1:
        raise SnipError("end_text '{}' not found".format(end_text))

    try:
        return lines[l0[start_count]+start_offset:l1[end_count]+end_offset]
    except IndexError as i:
        raise SnipError("IndexError.  len(lines)={}  l0={}  l1={}  start_count={}  end_count={}".
                        format(len(lines),l0,l1,start_count,end_count))
    

PS_HEADER="USER        PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND"
load_average_re=re.compile("load average: ([0-9.]+), ([0-9.]+), ([0-9.]+)")
cpunum_re = re.compile("cpuhp/(\d+)")
def extract_instance_state(data):
    """Given the text file from Amazon, create a dictionary of the node's snapshot at a given time. Returns None if an error is encountered"""
    # Given an instance state file as an input, extract useful information.
    ret = {}
    lines = data.split("\n")
    if len(lines)<50:           # too short!
        return None

    ret[DATETIME] = datetime.datetime.strptime(lines[2][4:],"%b %d %H:%M:%S %Z %Y")

    uptime         = snip(lines,"uptime","# whats running",start_offset=+1,end_offset=-1)
    ret[PROCESSES] = snip(lines,PS_HEADER,"# Top CPU users",start_offset=1,end_offset=-1)

    # Find how many cores on this system
    max_cpu = 0
    for line in ret[PROCESSES]:
        m = cpunum_re.search(line)
        if m:
            cpunum = int(m.group(1)) +1
            if cpunum>max_cpu:
                max_cpu = cpunum

    ret[CORES] = max_cpu

    m = load_average_re.search(uptime[0])
    if m:
        ret[LOAD_AVERAGE] = [float(val) for val in m.group(1,2,3)]

    cpu  = snip(lines,'iostat -x 1 5','iostat -x 1 5',start_offset=4,end_offset=5)
    mem  = snip(lines,'# whats memory usage look like','# trend memory')
    disk = snip(lines,'# amount of disk free','# amount of disk free',start_offset=0,end_offset=10)

    # Extract cpu loads
    cpu_stats      = dict(zip(['user','nice','system','iowait','steal','idle'],
                              [float(val) for val in cpu[0].split()]))
    ret[CPU_STATS] = cpu_stats

    # Extract memory
    ret[MEM_STATS] = dict(zip(mem[2].strip().split(),
                              [float(val) for val in mem[3].strip().split()[1:]]))

    # Get the alerts
    ret[ALERTS] = {}
    for level in [EMERG,ALERT,CRIT,ERR,WARNING,NOTICE]:
        ret[ALERTS][level] = [lines[m] for m in grep(lines,level)]
    return ret

def bucket_prefix_for_cluster(cluster):
    return s3.get_bucket_key('s3://' + EMR_LOG_BUCKET_NAME + '/' + cluster + '/node')



################################################################
###
### Census Proxy Information
###
################################################################

HTTP_PROXY='HTTP_PROXY'
HTTPS_PROXY='HTTPS_PROXY'
BCC_PROXY='BCC_PROXY'
def proxy_on():
    if BCC_PROXY in os.environ:
        os.environ[HTTP_PROXY] = os.environ[BCC_PROXY]
        os.environ[HTTPS_PROXY] = os.environ[BCC_PROXY]

def proxy_off():
    del os.environ[HTTP_PROXY]
    del os.environ[HTTPS_PROXY]


################################################################
###
### aws emr commands
###
################################################################

def describe_cluster(clusterID):
    """Get the cluster info"""
    proxy_on()
    ret = json.loads(subprocess.check_output(['aws','emr','describe-cluster','--output','json','--cluster-id',clusterID]))['Cluster']
    proxy_off()
    return ret


def list_instances(clusterID):
    """Get the list of instances"""
    proxy_on()
    ret = json.loads(subprocess.check_output(['aws','emr','list-instances','--output','json','--cluster-id',clusterID]))['Instances']
    proxy_off()
    return ret

################################################################

INSTANCE_STATE_RE = re.compile('(?P<cluster>[^/]+)/node/(?P<node>[^/]+)/daemons/instance-state/'+
                               'instance-state.log-(?P<date>.*).gz')

def get_cluster_stats(clusterID,limit=None,threads=THREADS,start=dateutil.parser.parse(FIRST_DATE),end=dateutil.parser.parse(END_DATE)):
    print(f"Generating report for clusterID {clusterID}")
    ci = Cluster(clusterID=clusterID)
    ci.get_info_from_aws()
    ci.info()

    (bucket,prefix) = bucket_prefix_for_cluster(clusterID)
    for node in ci.nodes.values():

        p2 = f'{prefix}/{node.instanceID}/daemons/instance-state/'
        for obj in s3.list_objects(bucket,p2,limit=limit):
            key = obj[_Key]
            date = date_from_log_filename(key)
            if start <= date <= end:
                m = INSTANCE_STATE_RE.search(key)
                if m:
                    instanceID2 = m['node']
                    datestr     = m['date']
                    assert node.instanceID == instanceID2
                    node.addS3Key(datestr,key)

    # Now get all of the S3 keys:
    # We do this separatel because we parallelize this within each node
    for node in ci.nodes.values():
        node.download_and_parse_s3keys(bucket=bucket,threads=threads,limit=limit)
    return ci

def time_range_for_node(cluster,node):
    prefix = cluster + '/node/' + node + '/daemons/instance-state/'
    times = [obj['Key'].replace(prefix,'') for obj in s3.list_objects(EMR_LOG_BUCKET_NAME, prefix, delimiter='/')]
    if not times:
        return (None, None)
    t0 = times[0].replace('instance-state.log-','').replace('.gz','')
    t1 = times[-1].replace('instance-state.log-','').replace('.gz','')
    t0 = t0[0:10] + " " + t0[11:13] + ":" + t0[14:16]
    t1 = t1[0:10] + " " + t1[11:13] + ":" + t1[14:16]
    return (t0,t1)

def nodes_for_cluster(cluster):
    prefix = cluster + '/node/'
    return [obj['Prefix'].replace(prefix,'').replace('/','') for obj in s3.list_objects(EMR_LOG_BUCKET_NAME, prefix, delimiter='/')]

def list_available_clusters():
    print("Available clusters:")
    for obj in s3.list_objects(EMR_LOG_BUCKET_NAME,'',delimiter='/'):
        cluster = obj['Prefix'].replace('/','')
        print(f'Cluster: {cluster:16}  ',end='', flush=True)
        nodes = nodes_for_cluster(cluster)
        print(f'nodes: {len(nodes):2}  ',end='', flush=True)
        (t0,t1) = time_range_for_node(cluster,nodes[0])
        print(f'from {t0} to {t1}')
    



if __name__=="__main__":
    from argparse import ArgumentParser,ArgumentDefaultsHelpFormatter
    parser = ArgumentParser( formatter_class = ArgumentDefaultsHelpFormatter,
                             description="Generate stats on the current cluster" )
    parser.add_argument("--list",    help="List available clusters", action='store_true')
    parser.add_argument("--cluster", help="specify nodes in this cluster",default=clusterID())
    parser.add_argument("--start",   help="Specify start time for stats in ISO8601 format (e.g. 2018-10-10T10:10)")
    parser.add_argument("--end",     help="specify end time for stats in ISO8601 format")
    parser.add_argument("--parse",   help="Just parse the specified node stats file (for testing)")
    parser.add_argument('-j',"--threads", type=int, default=THREADS, help="Use this many threads by default")
    parser.add_argument('--limit', type=int, help="Limit to this many samples (for debugging)")
    parser.add_argument("--save" , help="Save cluster stats in a file")
    parser.add_argument("--load" , help="Load cluster stats from file, rather than from S3")
    parser.add_argument("--outfile", help="Specify output file", default='cluster_stats.pdf')

    args   = parser.parse_args()
    if args.parse:
        data = extract_instance_state(open(args.parse,"r").read())
        print("data:",data)
        exit(0)
    
    if args.list:
        list_available_clusters()
        exit(0)

    if args.load:
        ci = pickle.loads(open(args.load,"rb").read())
        print("Cluster loaded from file:")
        ci.info()

    else:
        a2 = {}
        if args.start:
            a2['start'] = dateutil.parser.parse(args.start)
        if args.end:
            a2['end'] = dateutil.parser.parse(args.end)
        ci = get_cluster_stats(args.cluster,limit=args.limit,threads=args.threads,**a2)

    if args.save:
        with open(args.save,"wb") as f:
            f.write(pickle.dumps(ci))


    emr_graph = emr_graph.EMR_Graph(ci)
    emr_graph.graph(args.outfile)


