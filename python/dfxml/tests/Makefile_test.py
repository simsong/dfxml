#!/usr/bin/env python3
#
# run 'make clean' under py.test

import subprocess
import os
import os.path
import sys

def test_make_all():
    if sys.platform=='win32':
        return                  # don't run on win32
    os.chdir( os.path.dirname(__file__) )
    subprocess.run(['make','all'], check=True)

def test_make_clean():
    if sys.platform=='win32':
        return                  # don't run on win32
    os.chdir( os.path.dirname(__file__) )
    subprocess.run(['make','clean'], check=True)

                       
