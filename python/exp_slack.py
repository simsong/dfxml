#!/usr/bin/env python3.2
# 
# exp_slack.py: experiment on the slack space 
# quantify slack space
#
# (c) Martin Mulazzani, 2012
# Additions by Simson Garfinkel

import re
import os
import sys

import dfxml.fiwalk as fiwalk

def proc(fi):
    # Skip the virtual files?
    if fi.filename()[0:1] in ['$']:
        return
    if fi.has_contents() and fi.is_file():
        outstring = str(fi.partition())+"\t"+fi.filename()+"\t"+str(fi.filesize())+"\t"+str(fi.times())+"\n"
        f_out.write(outstring)



if __name__=="__main__":
    if len(sys.argv) != 2:
        print('usage: ./fast_slack.py <input.xml>')
        sys.exit(1)

    #input
    file_name = sys.argv[1]
    f = open(file_name, "rb")
  
    #output is to stdout
    outfile = sys.stdout

    #find partition information, blocksize and filesystem
    #1st partition has no. 1, to correspond to fiwalk output
    partitioncounter = 0
    f.write("********************************** PARTITIONS **********************************")
    f.write("\nNo\tBlocksize\tFilesystem\n")

    for line in f:
        if re.search("block_size", line):
            partitioncounter += 1
            f_out.write(str(partitioncounter))
            f_out.write("\t")
            f_out.write(re.split(">|<", line)[2])
        if re.search("ftype_str", line):
            f_out.write("\t\t")
            f_out.write(re.split(">|<", line)[2])
            f_out.write("\n")
    
    f_out.write("\n\n************************************* DATA *************************************\n")
    f_out.write("Partition\tFilename\tSize\tTimestamps\n")
    f.close()

    #re-open file for binary reading
    #file processing
    f = open(file_name, "rb")
    fiwalk.fiwalk_using_sax(xmlfile=f,callback=proc)

