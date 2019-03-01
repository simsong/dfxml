# Unit tests for objects


__version__="0.1.0"

import sys
import os

# "dfxml/python" directory where dfxml is the directory where repo is cloned
# should be added to sys.path for when these files are run by themselves from Makefile
dfxml_python_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if dfxml_python_dir not in sys.path:
    sys.path.append(dfxml_python_dir)
from dfxml.objects import *
from dfxml.objects import _intcast, _qsplit, _logger

def test_all():
    assert _intcast(-1) == -1
    assert _intcast("-1") == -1
    assert _qsplit("{http://www.w3.org/2001/XMLSchema}all") == ("http://www.w3.org/2001/XMLSchema","all")
    assert _qsplit("http://www.w3.org/2001/XMLSchema}all") == (None, "http://www.w3.org/2001/XMLSchema}all")

    fi = FileObject()

    #Check property setting
    fi.mtime = "1999-12-31T23:59:59Z"
    _logger.debug("fi = %r" % fi)

    #Check bad property setting
    failed = None
    try:
        fi.mtime = "Not a timestamp"
        failed = False
    except:
        failed = True
    _logger.debug("fi = %r" % fi)
    _logger.debug("failed = %r" % failed)
    assert failed==True

    t0 = TimestampObject(prec="100ns", name="mtime")
    _logger.debug("t0 = %r" % t0)
    assert t0.prec[0] == 100
    assert t0.prec[1] == "ns"
    t1 = TimestampObject("2009-01-23T01:23:45Z", prec="2", name="atime")
    _logger.debug("t1 = %r" % t1)
    assert t1.prec[0] == 2
    assert t1.prec[1] == "s"


