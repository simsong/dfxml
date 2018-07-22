
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

__version__="0.1.0"

import sys
import logging
import os
import xml.etree.ElementTree as ET

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

def test_all():


    _logger = logging.getLogger(os.path.basename(__file__))
    logging.basicConfig(level=logging.DEBUG)

    XMLNS_TEST_CLAMSCAN = "file:///opt/local/bin/clamscan"
    XMLNS_TEST_UNREGGED = "file:///dev/random"

    ET.register_namespace("clam", XMLNS_TEST_CLAMSCAN)

    fi = Objects.FileObject()
    fi.filename = "clamscanned"

    #Try and fail to add a non-Element to the list.
    failed = None
    _logger.debug("Before:  " + repr(fi.externals))
    try:
        fi.externals.append(1)
        failed = False
    except TypeError:
        failed = True
    except:
        failed = True
        raise
    _logger.debug("After:  " + repr(fi.externals))
    assert failed
    failed = None

    #Dummy up a non-DFXML namespace element.  This should be appendable.
    e = ET.Element("{%s}scan_results" % XMLNS_TEST_CLAMSCAN)
    e.text = "Clean"
    fi.externals.append(e)

    #Dummy up a DFXML namespace element.  This should not be appendable (the schema specifies other namespaces).
    e = ET.Element("{%s}filename" % Objects.dfxml.XMLNS_DFXML)
    e.text = "Superfluous name"
    _logger.debug("Before:  " + repr(fi.externals))
    try:
        fi.externals.append(e)
        failed = False
    except ValueError:
        failed = True
    except:
        failed = True
        raise
    _logger.debug("After:  " + repr(fi.externals))
    assert failed
    failed = None

    #Add an element with the colon prefix style
    e = ET.Element("clam:version")
    e.text = "20140101"
    fi.externals.append(e)

    #Add an element that doesn't have an ET-registered namespace prefix.
    e = ET.Element("{%s}test2" % XMLNS_TEST_UNREGGED)
    e.text = "yes"
    fi.externals.append(e)

    #Test serialization
    s = Objects._ET_tostring(fi.to_Element()) #TODO Maybe this should be more than an internal function.
    _logger.debug(s)
    if s.find("scan_results") == -1:
        raise ValueError("Serialization did not output other-namespace element 'scan_results'.")
    if s.find("clam:version") == -1:
        raise ValueError("Serialization did not output prefixed element 'clam:version'.")
    if s.find("test2") == -1:
        raise ValueError("Serialization did not output unregistered-prefix element 'test2'.")

    #Test de-serialization
    fir = Objects.FileObject()
    x = ET.XML(s)
    fir.populate_from_Element(x)
    _logger.debug("De-serialized: %r." % fir.externals)
    assert len(fir.externals) == 3

if __name__=="__main__":
    test_all()    
