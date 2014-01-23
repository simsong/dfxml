
import Objects
import logging
import os

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
f0.sha1 = "7d97e98f8af710c7e7fe703abc8f639e0ee507c4"
f0.md5 = "2b00042f7481c7b056c4b410d28f33cf"
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
f2.sha1 = "447d306060631570b7713ea48e74103c68eab0a3"
f2.md5 = "b9eb9d6228842aeb05d64f30d56b361e"

_logger.debug("f1 = %r" % f1)
d01 = f0.compare_to_other(f1)
_logger.debug("d01 = %r" % d01)
assert d01 == set(["alloc"]) or d01 == set(["alloc", "unalloc"])

d02 = f0.compare_to_other(f2)

_logger.debug("d02 = %r" % d02)
assert d02 == set(["mtime", "md5", "sha1"])

f2.original_fileobject = f0
f2.compare_to_original()
_logger.debug("f2.diffs = %r" % f2.diffs)
assert f2.diffs == d02

#TODO include byte_runs
