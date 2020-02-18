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

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

def test_all():
    logging.basicConfig(level=logging.DEBUG)
    _logger = logging.getLogger(os.path.basename(__file__))

    f0 = Objects.FileObject()

    fo = Objects.FileObject()
    pfo = Objects.FileObject()
    pfo.inode = 234
    f0.parent_object = pfo
    f0.filename = "test file"
    f0.error = "Neither a real file, nor real error"
    f0.partition = 2
    f0.id = 235
    f0.name_type = "r"
    f0.filesize = 1234
    f0.unalloc = 0
    f0.unused = 0
    f0.orphan = 0
    f0.compressed = 1
    f0.inode = 6543
    f0.libmagic = "data"
    f0.meta_type = 8
    f0.mode = 755
    f0.nlink = 1
    f0.uid = "S-1-234-etc"
    f0.gid = "S-2-234-etc"
    f0.mtime = "1999-12-31T12:34:56Z"
    f0.ctime = "1998-12-31T12:34:56Z"
    f0.atime = "1997-12-31T12:34:56Z"
    f0.crtime = "1996-12-31T12:34:56Z"
    f0.seq = 3
    f0.dtime = "1995-12-31T12:34:56Z"
    f0.bkup_time = "1994-12-31T12:34:56Z"
    f0.link_target = "Nonexistent file"
    f0.libmagic = "Some kind of compressed"
    f0.md5 = "db72d20e83d0ae39771403bc4cdde040"
    f0.sha1 = "866e1f426b2380aaf74a091aa0f39f62ae8a2de7"
    f0.sha256 = "4bc5996997ab9196b2d998b05ef302ed1dc167d74ec881533ee35008b5168630"
    f0.sha384 = "2ec378692eeae4b855f58832664f95bb85411caac8dcebe7cd3916e915559d3f0ccda688a1fad1e3f47801fe15298ac0"
    #fo.brs = brs #TODO
    _logger.debug("f0 = %r" % f0)
    _logger.debug("f0.to_dfxml() = %r" % f0.to_dfxml())

    e0 = f0.to_Element()
    _logger.debug("e0 = %r" % e0)

    #f1 = eval(repr(f0)) #TODO The recursive evals cause namespace confusion (Objects.foo); replace the next two lines when that's settled.
    f1 = Objects.FileObject()
    f1.populate_from_Element(e0)

    f2 = Objects.FileObject()
    f2.populate_from_Element(e0)

    #The id property should not be included in the comparisons
    f1.id = 111
    f1.alloc = False

    f2.mtime = "2999-12-31T12:34:56Z"
    f2.md5 = "593c8fe4a2236f3eeba7f4577b663876"
    f2.sha1 = "0c0c20c03bdb8913da8ea120bd59ba5f596deceb"
    f2.sha256 = "4f6dcb46e0f7b0ad748d083f6e92d7df586d0298a94acc3795287ff156614540"
    f2.sha384 = "2af87ca47d01989009caf3927a84be215528a53629dd935a828921ac0a4b22202bcba20d38fdd16d719b8c4241fcdacb"

    _logger.debug("f1 = %r" % f1)
    d01 = f0.compare_to_other(f1)
    _logger.debug("d01 = %r" % d01)
    assert d01 == set(["alloc"]) or d01 == set(["alloc", "unalloc"])

    d02 = f0.compare_to_other(f2)

    _logger.debug("d02 = %r" % d02)
    assert d02 == set(["mtime", "md5", "sha1", "sha256", "sha384"])

    f2.original_fileobject = f0
    f2.compare_to_original()
    _logger.debug("f2.diffs = %r" % f2.diffs)
    assert f2.diffs == d02

    #TODO include byte_runs

    
if __name__=="__main__":
    test_all()
