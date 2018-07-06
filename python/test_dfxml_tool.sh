#!/bin/bash

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

. _pick_pythons.sh

#Halt on error
set -e
#Display all executed commands
set -x

#Flags listed here in alphabetical order
DT_OPTIONS[0]=
DT_OPTIONS[1]=--allprovenance
DT_OPTIONS[2]=--commandline
DT_OPTIONS[3]=--includedirs
DT_OPTIONS[4]=--iso-8601
DT_OPTIONS[5]=--md5
DT_OPTIONS[6]=--nofilenames
DT_OPTIONS[7]=--nometadata
DT_OPTIONS[8]=--pythonversion
DT_OPTIONS[9]=--sha1
DT_OPTIONS[10]=--sha256
DT_OPTIONS[11]="--stripleaddirs 1"
DT_OPTIONS[12]="--stripprefix .."

iter=0
for x in "${DT_OPTIONS[@]}"; do
  echo "Iteration $iter: Testing $x" >&2
  "$PYTHON2" dfxml_tool.py $x ../src > dfxml_tool_p2_${iter}.dfxml
#  "$PYTHON3" dfxml_tool.py "--$x" .. > dfxml_tool_p3_${iter}.dfxml
  iter=$(($iter+1))
done
