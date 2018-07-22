#!/usr/bin/env python3
#
# run 'make clean' under py.test

import subprocess
import os
import os.path

def test_make_all():
    os.chdir( os.path.dirname(__file__) )
    subprocess.run(['make','all'], check=True)

def test_make_clean():
    os.chdir( os.path.dirname(__file__) )
    subprocess.run(['make','clean'], check=True)

                       
