#!/bin/bash

. _pick_pythons.sh

#Halt on error
set -e
#Display all executed commands
set -x

"$PYTHON2" dfxml.py --regress
"$PYTHON3" dfxml.py --regress
