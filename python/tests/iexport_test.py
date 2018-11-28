import sys
import os
import py.test

sys.path.append( os.path.join(os.path.dirname(__file__), ".."))
from iexport import *

def test_iexport():
    r1 = Run(0,1000)
    r2 = Run(50,60)
    assert r1.intersects_run(r2)
    assert r2.intersects_run(r1)

    disk = RunDB(0,1000)
    print(disk)
    disk.remove(Run(50,60))
    disk.remove(Run(0,10))
    disk.remove(Run(40,20))
    print(disk)

    
