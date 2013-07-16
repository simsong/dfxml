#!/bin/bash

. _pick_pythons.sh

"$PYTHON2" dfxml.py --regress
"$PYTHON3" dfxml.py --regress
