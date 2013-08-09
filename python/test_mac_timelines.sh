#!/bin/bash

. _pick_pythons.sh

#Halt on error
set -e
#Display all executed commands
set -x

"$PYTHON2" demo_mac_timeline.py ../samples/simple.xml
"$PYTHON3" demo_mac_timeline.py ../samples/simple.xml
