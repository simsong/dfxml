# vmstats
This demo application uses DFXML to record the status of a virtual machine over time and allow exploration. It includes a program for making high-resolution measurements of all the nodes in an Amazon Elastic Map Reduce (EMR) cluster and producing a graph after each EMR run.

# Usages

## vm_collect.py
The `vm_collect.py` script creates a DFXML file that contains information about the current status of a virtual machine. Results are written to a DFXML file. The script has a `--repeat` option which causes multiple DFXML objects to be written to the same file.

## emr_stats.py

The `emr_stats.py` program collects on an Amazon EMR node. The resulting 

    python emr_stats.py [--cluster CLUSTERID]  [--start STARTTIME] [--end ENDTIME]

Collects on an EMR node.




