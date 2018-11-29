#!/usr/bin/env python3
#
# Using Yarn, launch vm_collect.py on each of the nodes
# Assumes that the DFXML project is checked out on every node

import os
from subprocess import check_call,check_output
import sys

VM_COLLECT = os.path.join( os.path.dirname(__file__),"vm_collect.py")
INSTANCE_FACTOR = 3             # creates this times more vm_collect processes (logfile will prevent others from launching)


if __name__=="__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    import time
    parser = ArgumentParser(description='Launch vm_collect on each of the nodes in an EMR cluster',formatter_class=ArgumentDefaultsHelpFormatter)
    if "CLUSTERID" in os.environ:
        parser.add_argument("--clusterId",help="Specifies cluster ID",default=os.environ['CLUSTERID'])
    else:
        parser.add_argument("--clusterId",help="Specifies cluster ID",required=True)
    if "DAS_S3ROOT" in os.environ:
        parser.add_argument("--s3logbucket",help="When running in EMR mode, this bucket specifies where the logfiles are stored.",
                            default=os.environ['DAS_S3ROOT']+"-logs")
    else:
        parser.add_argument("--s3logbucket",help="When running in EMR mode, this bucket specifies where the logfiles are stored.",
                            required=True)
    parser.add_argument("--vm_collect", help="vm_collect.py executable on each node",default=VM_COLLECT)
    parser.add_argument("--max_seconds", help="Maximum number of seconds to collect for",default=60*60*24*7)
    args = parser.parse_args()

    s3root  = f"{args.s3logbucket}/{args.clusterId}"
    if not s3root.startswith("s3://"):
        s3root = "s3://" + s3root

    # Determine how many instances there are
    output = check_output(['aws','s3','ls',s3root+"/node/"],encoding='utf-8')
    instances = output.count("\n")
    print(f"There are {instances} instances in cluster {args.clusterId}")
    runfile = f"{s3root}/vm_collect_running"

    # Create the runfile
    check_call(['aws','s3','cp','-',runfile],stdin=open('/dev/null'))

    shell_command = f"{sys.executable} {args.vm_collect} --repeat {args.max_seconds} --lockfile /tmp/vm_collect.lock --runfile {runfile} --s3root {s3root} --bg"

    # Run on the head end
    check_call(shell_command,shell=True)

    # Run on CORE nodes
    DSJAR='/usr/lib/hadoop-yarn/hadoop-yarn-applications-distributedshell-2.8.3-amzn-0.jar'
    CLIENT='org.apache.hadoop.yarn.applications.distributedshell.Client'
    check_call(['yarn','jar',DSJAR,'-jar',DSJAR, CLIENT,
                '-num_containers', str(instances * INSTANCE_FACTOR),'-master_memory','1000','-container_memory','1000',
                '-shell_command',shell_command])
    
    print(f"Terminate with: aws s3 rm {runfile}")
