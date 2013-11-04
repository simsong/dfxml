
"""
This file re-creates the major DFXML classes with an emphasis on type safety, serializability, and de-serializability.

Consider this file highly experimental (read: unstable).
"""

__version__ = "0.0.1"

import logging
import re
import dfxml
import xml.etree.ElementTree as ET

class RegXMLObject(object):
    def __init__(self, *args, **kwargs):
        self.version = kwargs.get("version")
        self.creator = kwargs.get("creator")
        self._hives = []
        self._cells = []

    def append(self, value):
        if isinstance(value, HiveObject):
            self._hives.append(value)
        elif isinstance(value, CellObject):
            self._cells.append(value)
        else:
            logging.debug("value = %r" % value)
            raise TypeError("Expecting a HiveObject or a CellObject.  Got instead this type: %r." % type(value))

    def to_Element(self):
        outel = self.to_partial_Element()

        for hive in self._hives:
            tmpel = hive.to_Element()
            outel.append(tmpel)

        for cell in self._cells:
            tmpel = cell.to_Element()
            outel.append(tmpel)

        return outel

    def to_partial_Element(self):
        """
        Creates the wrapping RegXML text.  No hives, no cells.  Saves on creating an entire element tree in memory.
        """
        outel = ET.Element("regxml")

        if self.version:
            outel.attrib["version"] = self.version

        return outel

    def to_regxml(self):
        """(RAM-intensive.)"""
        print(ET.tostring(self.to_Element()))

    def print_regxml(self):
        """Serializes and prints the entire object, without constructing the whole tree."""
        regxml_wrapper = ET.tostring(self.to_partial_Element())
        regxml_head = regxml_wrapper.strip()[:-len("</regxml>")]
        regxml_foot = "</regxml>"

        print(regxml_head)
        for hive in _hives:
            hive.print_regxml()
        print(regxml_foot)

class HiveObject(object):
    def __init__(self, *args, **kwargs):
        self._cells = []

    def append(self, value):
        assert isinstance(value, CellObject)
        self._cells.append(value)

    def to_Element(self):
        outel = ET.Element("hive")
        for cell in self._cells:
            tmpel = cell.to_Element()
            outel.append(tmpel)
        return outel

    def print_regxml(self):
        for cell in _cells:
            print(cell.to_regxml)

class ByteRun(object):
    def __init__(self, *args, **kwargs):
        self.file_offset = kwargs.get("file_offset")
        self.len = kwargs.get("len")

    def __repr__(self):
        parts = []
        if self.file_offset:
            parts.append("file_offset=%r" % self.file_offset)
        if self.len:
            parts.append("len=%r" % self.len)
        return "ByteRun(" + ", ".join(parts) + ")"

    def to_Element(self):
        outel = ET.Element("byte_run")
        if self.file_offset:
            outel.attrib["file_offset"] = str(self.file_offset)
        if self.len:
            outel.attrib["len"] = str(self.len)
        return outel

    @property
    def file_offset(self):
        return self._file_offset

    @file_offset.setter
    def file_offset(self, val):
        if not val is None:
            assert isinstance(val, int)
        self._file_offset = val

    @property
    def len(self):
        return self._len

    @len.setter
    def len(self, val):
        if not val is None:
            assert isinstance(val, int)
        self._len = val

class ByteRuns(list):
    """
    An extension to Python lists.

    Refs:
    http://www.rafekettler.com/magicmethods.html
    http://stackoverflow.com/a/8841520
    """
    #Must define these methods to adhere to the list protocol:
    #__len__
    #__getitem__
    #__setitem__
    #__delitem__
    #__iter__
    #append

    def __init__(self, run_list=None):
        self._listdata = []
        if isinstance(run_list, list):
            for run in run_list:
                self.append(run)

    def __repr__(self):
        parts = []
        for run in self:
            parts.append(repr(run))
        return "ByteRuns(run_list=[" + ", ".join(parts) + "])"

    def __len__(self):
        return self._listdata.__len__()

    def __getitem__(self, key):
        return self._listdata.__getitem__(key)

    def __setitem__(self, key, value):
        assert isinstance(value, ByteRun)
        self._listdata[key] = value

    def __delitem__(self, key):
        del self._listdata[key]

    def __iter__(self):
        return iter(self._listdata)

    def append(self, value):
        assert isinstance(value, ByteRun)
        self._listdata.append(value)

    def to_Element(self):
        outel = ET.Element("byte_runs")
        for run in self:
            tmpel = run.to_Element()
            outel.append(tmpel)
        return outel

    def contents(self, raw_image):
        """Generator.  Yields contents, given a backing raw image path."""
        assert not raw_image is None
        raise Exception("Not implemented yet.")

re_precision = re.compile(r"(?P<num>\d+)(?P<unit>(|m|n)s|d)?")
class TimestampObject(object):
    """
    Encodes the "dftime" type.  Wraps around dfxml.dftime, closely enough that this might just get folded into that class.
    """

    timestamp_name_list = ["mtime", "atime", "ctime", "crtime", "dtime", "bkup_time"]

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name")
        self.prec = kwargs.get("prec")
        #logging.debug("type(args) = %r" % type(args))
        logging.debug("args = %r" % (args,))
        if len(args) == 0:
            pass
        elif len(args) == 1:
            self.time = args[0]
        else:
            raise ValueError("Unexpected arguments.  Whole args tuple: %r." % (args,))

    def to_Element(self):
        assert self.name
        outel = ET.Element(self.name)
        if self.prec:
            outel.attrib["prec"] = "%d%s" % self.prec
        if self.time:
            outel.text = str(self.time)
        return outel

    @property
    def name(self):
        """The type of timestamp - modified (mtime), accessed (atime), etc."""
        return self._name

    @name.setter
    def name(self, value):
        if not value is None:
            assert value in TimestampObject.timestamp_name_list 
        self._name = value

    @property
    def prec(self):
        """
        A pair, (resolution, unit); unit is a second (s), millisecond, nanosecond, or day (d).  The default unit is "s".
        """
        return self._prec

    @prec.setter
    def prec(self, value):
        if value is None:
            self._prec = None
            return self._prec
        m = re_precision.match(value)
        md = m.groupdict()
        tup = (int(md["num"]), md.get("unit") or "s")
        logging.debug("tup = %r" % (tup,))
        self._prec = tup

    @property
    def time(self):
        """
        The actual timestamp.  A DFXML.dftime object.  This class might be superfluous and end up collapsing into that...
        """
        return self._time

    @time.setter
    def time(self, value):
        if value is None:
            self._time = None
        else:
            checked_value = dfxml.dftime(value)
            logging.debug("checked_value.timestamp() = %r" % checked_value.timestamp())
            self._time = checked_value

class FileObject(object):
    """
    This class provides property accesses, an XML serializer (ElementTree-based), and a deserializer.
    The properties interface is NOT function calls, but simple accesses.  That is, the old _fileobject_ style:

        assert isinstance(fi, dfxml.fileobject)
        fi.mtime()

    is now replaced with:

        assert isinstance(fi, dfxml.FileObject)
        fi.mtime
    """

    def __init__(self, *args, **kwargs):
        self.mtime = kwargs.get("mtime")

    def __repr__(self):
        parts = []

        if self.mtime:
            parts.append("mtime=%r" % str(self.mtime))

        return "FileObject(" + ", ".join(parts) + ")"

    @property
    def mtime(self):
        return self._mtime

    @mtime.setter
    def mtime(self, val):
        if val is None:
            self._mtime = None
        else:
            checked_val = dfxml.dftime(val)
            logging.debug("checked_val.timestamp() = %r" % checked_val.timestamp())
            self._mtime = checked_val

class CellObject(object):
    def __init__(self, *args, **kwargs):
        #These properties must be assigned first for sanity check dependencies
        self.name_type = kwargs.get("name_type")

        self.alloc = kwargs.get("alloc")
        self.byte_runs = kwargs.get("byte_runs")
        self.cellpath = kwargs.get("cellpath")
        self.mtime = kwargs.get("mtime")
        self.name = kwargs.get("name")
        self.root = kwargs.get("root")
        self.original_cellobject = kwargs.get("original_cellobject")

    def __repr__(self):
        parts = []

        if self.alloc:
            parts.append("alloc=%r" % self.alloc)
        if self.byte_runs:
            parts.append("byte_runs=%r" % self.byte_runs)
        if self.cellpath:
            parts.append("cellpath=%r" % self.cellpath)
        if self.mtime:
            parts.append("mtime=%r" % str(self.mtime))
        if self.name:
            parts.append("name=%r" % self.name)
        if self.name_type:
            parts.append("name_type=%r" % self.name_type)
        if self.original_cellobject:
            parts.append("original_cellobject=%r" % self.original_cellobject)
        if self.root:
            parts.append("root=%r" % self.root)

        return "CellObject(" + ", ".join(parts) + ")"

    def to_Element(self):
        self.sanity_check()

        outel = ET.Element("cellobject")

        if self.root:
            outel.attrib["root"] = str(self.root)

        if self.cellpath:
            tmpel = ET.Element("cellpath")
            tmpel.text = self.cellpath
            outel.append(tmpel)

        if self.name:
            tmpel = ET.Element("name")
            tmpel.text = self.name
            outel.append(tmpel)

        if self.name_type:
            tmpel = ET.Element("name_type")
            tmpel.text = self.name_type
            outel.append(tmpel)

        if self.alloc:
            tmpel = ET.Element("alloc")
            tmpel.text = str(self.alloc)
            outel.append(tmpel)

        if self.mtime:
            tmpel = self.mtime.to_Element()
            outel.append(tmpel)

        if self.byte_runs:
            tmpel = self.byte_runs.to_Element()
            outel.append(tmpel)

        if self.original_cellobject:
            tmpel = self.original_cellobject.to_Element()
            outel.append(tmpel)

        return outel

    def to_regxml(self):
        return ET.tostring(self.to_Element())

    def sanity_check(self):
        if self.name_type and self.name_type != "k":
            if self.mtime:
                logging.debug("Error occurred sanity-checking this CellObject: %r" % (self))
                raise ValueError("A Registry Key (node) is the only kind of CellObject that can have a timestamp.")
            if self.root:
                logging.debug("Error occurred sanity-checking this CellObject: %r" % (self))
                raise ValueError("A Registry Key (node) is the only kind of CellObject that can have the 'root' attribute.")

    @property
    def alloc(self):
        return self._alloc

    @alloc.setter
    def alloc(self, val):
        if not val is None:
            assert val in [0,1]
        self._alloc = val

    @property
    def byte_runs(self):
        return self._byte_runs

    @byte_runs.setter
    def byte_runs(self, val):
        if not val is None:
            assert isinstance(val, ByteRuns)
        self._byte_runs = val

    @property
    def cellpath(self):
        return self._cellpath

    @cellpath.setter
    def cellpath(self, val):
        if not val is None:
            assert isinstance(val, str)
        self._cellpath = val

    @property
    def mtime(self):
        return self._mtime

    @mtime.setter
    def mtime(self, val):
        self._mtime = TimestampObject(val, name="mtime")
        self.sanity_check()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        if not val is None:
            assert isinstance(val, str)
        self._name = val

    @property
    def name_type(self):
        return self._name_type

    @name_type.setter
    def name_type(self, val):
        if not val is None:
            assert val in ["k", "v"]
        self._name_type = val

    @property
    def original_cellobject(self):
        return self._original_cellobject

    @original_cellobject.setter
    def original_cellobject(self, val):
        if not val is None:
            assert isinstance(val, CellObject)
        self._original_cellobject = val

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, val):
        if not val is None:
            assert val == 1
        self._root = val

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    
    logging.basicConfig(level=logging.DEBUG)
    #Run unit tests
    fi = FileObject()

    #Check property setting
    fi.mtime = "1999-12-31T23:59:59Z"
    logging.debug("fi = %r" % fi)

    #Check bad property setting
    failed = None
    try:
        fi.mtime = "Not a timestamp"
        failed = False
    except:
        failed = True
    logging.debug("fi = %r" % fi)
    logging.debug("failed = %r" % failed)
    assert failed

    t0 = TimestampObject(prec="100ns", name="mtime")
    logging.debug("t0 = %r" % t0)
    assert t0.prec[0] == 100
    assert t0.prec[1] == "ns"
    t1 = TimestampObject("2009-01-23T01:23:45Z", prec="2", name="atime")
    logging.debug("t1 = %r" % t1)
    assert t1.prec[0] == 2
    assert t1.prec[1] == "s"

    co = CellObject()
    logging.debug("co = %r" % co)
    print(co.to_regxml())

    co.root = 1
    co.cellpath = "\\Deleted_root"
    co.name = "Deleted_root"
    co.name_type = "k"
    co.alloc = 1
    co.mtime = "2009-01-23T01:23:45Z"
    co.mtime.prec = "100ns"
    br = ByteRun()
    br.file_offset = 4128
    br.len = 133
    brs = ByteRuns()
    brs.append(br)
    co.byte_runs = brs
    logging.debug("br = %r" % br)
    logging.debug("brs = %r" % brs)
    logging.debug("co = %r" % co)
    print(co.to_regxml())

    ro = RegXMLObject(version="2.0")
    ho = HiveObject()
    ho.append(co)
    ro.append(ho)
    print(ro.to_regxml())
