
"""
This file re-creates the major DFXML classes with an emphasis on type safety, serializability, and de-serializability.

Consider this file highly experimental (read: unstable).
"""

__version__ = "0.0.6"

import logging
import re
import dfxml
import xml.etree.ElementTree as ET

#For memoization
import functools

@functools.lru_cache(maxsize=None)
def _qsplit(tagname):
    """Requires string input.  Returns namespace and local tag name as a pair.  I could've sworn this was a basic implementation gimme, but ET.QName ain't it."""
    assert isinstance(tagname, str)
    if tagname[0] == "{":
        i = tagname.rfind("}")
        return ( tagname[1:i], tagname[i+1:] )
    else:
        return (None, tagname)

def _typecheck(obj, classinfo):
    if not isinstance(obj, classinfo):
        logging.info("obj = " + repr(obj))
        if isinstance(classinfo, tuple):
            raise TypeError("Expecting object to be one of the types %r." % (classinfo,))
        else:
            raise TypeError("Expecting object to be of type %r." % classinfo)

@functools.lru_cache(maxsize=None)
def _boolcast(val):
    """Takes Boolean values, and 0 or 1 in string or integer form, and casts them all to Boolean.  Preserves nulls.  Balks at everything else."""
    if val is None:
        return None
    if val in [True, False]:
        return val

    _val = val
    if val in ["0", "1"]:
        _val = int(val)
    if _val in [0, 1]:
        return _val == 1

    logging.debug(val)
    raise ValueError("Received a not-straightforwardly-Boolean value.  Expected some form of 0, 1, True, or False.")

def _intcast(val):
    """Casts input integer or string to integer.  Preserves nulls.  Balks at everything else."""
    if val is None:
        return None
    if isinstance(val, int):
        return val

    if isinstance(val, str) and val.isdigit():
        return int(val)

    logging.debug(val)
    raise ValueError("Received a non-int-castable value.  Expected an integer or an integer as a string.")

@functools.lru_cache(maxsize=128)
def _octcast(val):
    if val is None:
        return None

    #Use _intcast to deal with nulls and bad strings
    i = _intcast(val)
    if not isinstance(i, int):
        logging.debug(val)
        raise ValueError("(Unforeseen revisions since last tested.)")

    s = "0o" + str(i)
    try:
        retval = int(s, 8)
        return retval
    except ValueError:
        logging.debug(val)
        logging.warning("Failed interpreting an octal mode.")
        return None

def _strcast(val):
    if val is None:
        return None
    return str(val)

class DFXMLBaseObject(object):
    "Coming soon."

    def __init__(self, *args, **kwargs):
        pass

class DFXMLObject(object):
    def __init__(self, *args, **kwargs):
        self.command_line = kwargs.get("command_line")
        self.version = kwargs.get("version")

        self._namespaces = dict()
        self._volumes = []
        self._files = []
        input_volumes = kwargs.get("volumes") or []
        input_files = kwargs.get("files") or []
        for v in input_volumes:
            self.append(v)
        for f in input_files:
            self.append(f)

    def add_namespace(self, prefix, url):
        self._namespaces[prefix] = url
        ET.register_namespace(prefix, url)

    def append(self, value):
        if isinstance(value, VolumeObject):
            self._volumes.append(value)
        elif isinstance(value, FileObject):
            self._files.append(value)
        else:
            logging.debug("value = %r" % value)
            raise TypeError("Expecting a VolumeObject or a FileObject.  Got instead this type: %r." % type(value))

    def to_partial_Element(self):
        outel = ET.Element("dfxml")

        tmpel0 = ET.Element("metadata")
        tmpel1 = ET.Element("dc:type")
        tmpel1.text = "(Placeholder)"
        tmpel0.append(tmpel1)
        outel.append(tmpel0)

        if self.command_line:
            tmpel0 = ET.Element("creator")
            tmpel1 = ET.Element("execution_environment")
            tmpel2 = ET.Element("command_line")
            tmpel2.text = self.command_line
            tmpel1.append(tmpel2)
            tmpel0.append(tmpel1)
            outel.append(tmpel0)
        if self.version:
            outel.attrib["version"] = self.version

        #Apparently, namespace setting is only available with the write() function, which is memory-impractical for significant uses of DFXML.
        #Ref: http://docs.python.org/3.3/library/xml.etree.elementtree.html#xml.etree.ElementTree.ElementTree.write
        for prefix in self._namespaces:
            attrib_name = "xmlns"
            if prefix != "":
                attrib_name += ":" + prefix
            outel.attrib[attrib_name] = self._namespaces[prefix]

        return outel

    def to_Element(self):
        outel = self.to_partial_Element()
        for v in self._volumes:
            tmpel = v.to_Element()
            outel.append(tmpel)
        for f in self._files:
            tmpel = f.to_Element()
            outel.append(tmpel)
        return outel

    def print_dfxml(self):
        """Memory-efficient DFXML document printer.  However, it assumes the whole element tree is already constructed."""
        pe = self.to_partial_Element()
        dfxml_wrapper = ET.tostring(pe, encoding="unicode")

        #If there are no children, this (trivial) document needs only a simpler printing.
        if len(pe) == 0 and len(self._volumes) == 0 and len(self._files) == 0:
            print(dfxml_wrapper)
            return

        dfxml_foot = "</dfxml>"
        dfxml_head = dfxml_wrapper.strip()[:-len(dfxml_foot)]

        print("""<?xml version="1.0"?>""")
        print(dfxml_head)
        for v in self._volumes:
            v.print_dfxml()
        for f in self._files:
            f.print_dfxml()
        print(dfxml_foot)

    def to_dfxml(self):
        """Serializes the entire DFXML document tree into a string.  Then returns that string.  RAM-intensive."""
        return ET.tostring(self.to_Element(), encoding="unicode")

    @property
    def command_line(self):
        return self._command_line

    @command_line.setter
    def command_line(self, value):
        if not value is None:
            assert isinstance(value, str)
        self._command_line = value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = _strcast(value)

class RegXMLObject(object):
    def __init__(self, *args, **kwargs):
        self.metadata = kwargs.get("metadata")
        self.creator = kwargs.get("creator")
        self.source = kwargs.get("source")
        self.version = kwargs.get("version")
        self._hives = []
        self._cells = []
        self._namespaces = dict()
        input_hives = kwargs.get("hives") or [] # In case kwargs["hives"] = None.
        input_cells = kwargs.get("cells") or []
        for hive in input_hives:
            self.append(hive)
        for cell in input_cells:
            self.append(cells)

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
        """Serializes the entire RegXML document tree into a string.  Returns that string.  RAM-intensive.  You probably want print_regxml()."""
        return ET.tostring(self.to_Element(), encoding="unicode")

    def print_regxml(self):
        """Serializes and prints the entire object, without constructing the whole tree."""
        regxml_wrapper = ET.tostring(self.to_partial_Element(), encoding="unicode")
        regxml_foot = "</regxml>"
        regxml_head = regxml_wrapper.strip()[:-len(regxml_foot)]

        print(regxml_head)
        for hive in self._hives:
            hive.print_regxml()
        print(regxml_foot)

class VolumeObject(object):
    def __init__(self, *args, **kwargs):
        self._files = []

    def append(self, value):
        assert isinstance(value, FileObject)
        self._files.append(value)

    def populate_from_Element(self, e):
        assert isinstance(e, ET.Element) or isinstance(e, ET.ElementTree)

        #Split into namespace and tagname
        (ns, tn) = _qsplit(e.tag)
        assert tn == "volume"

        #Look through direct-child elements to populate run array
        for ce in e.findall("./*"):
            (cns, ctn) = _qsplit(ce.tag)
            if ctn == "byte_runs":
                self.byte_runs = ByteRuns()
                self.byte_runs.populate_from_Element(ce)
            elif ctn in VolumeObject._all_properties:
                setattr(self, ctn, ce.text)
            else:
                raise ValueError("Unsure what to do with this element in a VolumeObject: %r" % ce)

    _all_properties = set(["byte_runs",
      "partition_offset",
      "sector_size",
      "block_size",
      "ftype",
      "ftype_str",
      "block_count",
      "first_block",
      "last_block",
      "allocated_only"
    ])

    _comparable_properties = set(["byte_runs",
      "partition_offset",
      "sector_size",
      "block_size",
      "ftype",
      "ftype_str",
      "block_count",
      "first_block",
      "last_block",
      "allocated_only"
    ])

    def to_partial_Element(self):
        """Returns the volume element with its properties, except for the child fileobjects."""
        outel = ET.Element("volume")
        return outel

    def to_Element(self):
        outel = self.to_partial_Element()
        for f in self._files:
            tmpel = f.to_Element()
            outel.append(tmpel)
        return outel

    def print_dfxml(self):
        pe = self.to_partial_Element()
        dfxml_wrapper = ET.tostring(pe, encoding="unicode")

        if len(pe) == 0 and len(self._files) == 0:
            print(dfxml_wrapper)
            return

        dfxml_foot = "</volume>"

        #Deal with an empty element being printed as <elem/>
        if len(pe) == 0:
            replaced_dfxml_wrapper = dfxml_wrapper.replace(" />", ">")
            dfxml_head = replaced_dfxml_wrapper
        else:
            dfxml_head = dfxml_wrapper.strip()[:-len(dfxml_foot)]

        print(dfxml_head)
        for f in self._files:
            e = f.to_Element()
            print(ET.tostring(e, encoding="unicode"))
        print(dfxml_foot)

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
        for cell in self._cells:
            print(cell.to_regxml())

class ByteRun(object):
    def __init__(self, *args, **kwargs):
        self.img_offset = kwargs.get("img_offset")
        self.fs_offset = kwargs.get("fs_offset")
        self.file_offset = kwargs.get("file_offset")
        self.len = kwargs.get("len")

    def __repr__(self):
        parts = []
        if self.file_offset:
            parts.append("file_offset=%r" % self.file_offset)
        if self.len:
            parts.append("len=%r" % self.len)
        return "ByteRun(" + ", ".join(parts) + ")"

    def __eq__(self, other):
        assert isinstance(other, ByteRun)
        return \
          self.img_offset == other.img_offset and \
          self.fs_offset == other.fs_offset and \
          self.file_offset == other.file_offset and \
          self.len == other.len

    def to_Element(self):
        outel = ET.Element("byte_run")
        if self.img_offset:
            outel.attrib["img_offset"] = str(self.img_offset)
        if self.fs_offset:
            outel.attrib["fs_offset"] = str(self.fs_offset)
        if self.file_offset:
            outel.attrib["file_offset"] = str(self.file_offset)
        if self.len:
            outel.attrib["len"] = str(self.len)
        return outel

    def populate_from_Element(self, e):
        assert isinstance(e, ET.Element) or isinstance(e, ET.ElementTree)

        #Split into namespace and tagname
        (ns, tn) = _qsplit(e.tag)
        assert tn == "byte_run"

        #Populate run properties from element attributes
        self.file_offset = e.attrib.get("file_offset")
        self.len = e.attrib.get("len")

    @property
    def file_offset(self):
        return self._file_offset

    @file_offset.setter
    def file_offset(self, val):
        self._file_offset = _intcast(val)

    @property
    def fs_offset(self):
        return self._fs_offset

    @fs_offset.setter
    def fs_offset(self, val):
        self._fs_offset = _intcast(val)

    @property
    def img_offset(self):
        return self._img_offset

    @file_offset.setter
    def img_offset(self, val):
        self._img_offset = _intcast(val)

    @property
    def len(self):
        return self._len

    @len.setter
    def len(self, val):
        self._len = _intcast(val)

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

    def __eq__(self, other):
        """Compares the byte run lists."""
        assert isinstance(other, ByteRuns)
        if len(self) != len(other):
            logging.debug("len(self) = %d" % len(self))
            logging.debug("len(other) = %d" % len(other))
            return False
        for (sbr_index, sbr) in enumerate(self):
            obr = other[sbr_index]
            logging.debug("sbr_index = %d" % sbr_index)
            logging.debug("sbr = %r" % sbr)
            logging.debug("obr = %r" % obr)
            if sbr != obr:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def append(self, value):
        assert isinstance(value, ByteRun)
        self._listdata.append(value)

    def to_Element(self):
        outel = ET.Element("byte_runs")
        for run in self:
            tmpel = run.to_Element()
            outel.append(tmpel)
        return outel

    def populate_from_Element(self, e):
        assert isinstance(e, ET.Element) or isinstance(e, ET.ElementTree)

        #Split into namespace and tagname
        (ns, tn) = _qsplit(e.tag)
        assert tn == "byte_runs"
 
        #Look through direct-child elements to populate run array
        for ce in e.findall("./*"):
            (cns, ctn) = _qsplit(ce.tag)
            if ctn == "byte_run":
                nbr = ByteRun()
                nbr.populate_from_Element(ce)
                self.append(nbr)

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
        #logging.debug("args = %r" % (args,))
        if len(args) == 0:
            self.time = None
        elif len(args) == 1:
            self.time = args[0]
        else:
            raise ValueError("Unexpected arguments.  Whole args tuple: %r." % (args,))

    def __eq__(self, other):
        _typecheck(other, TimestampObject)
        if self.name != other.name:
            return False
        if self.prec != other.prec:
            return False
        if self.time != other.time:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        parts = []
        if self.time:
            parts.append("%r" % self.time)
        if self.name:
            parts.append("name=%r" % self.name)
        if self.prec:
            parts.append("prec=%r" % (self.prec,))
        return "TimestampObject(" + ", ".join(parts) + ")"

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
        elif isinstance(value, tuple) and \
          len(value) == 2 and \
          isinstance(value[0], int) and \
          isinstance(value[1], str):
            self._prec = value
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
            #logging.debug("checked_value.timestamp() = %r" % checked_value.timestamp())
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

    _all_properties = set([
        "alloc",
        "atime",
        "bkup_time",
        "byte_runs",
        "compressed",
        "crtime",
        "ctime",
        "dtime",
        "filename",
        "filesize",
        "gid",
        "id",
        "inode",
        "libmagic",
        "md5",
        "meta_type",
        "mode",
        "mtime",
        "name_type",
        "nlink",
        "orphan",
        "parent_object",
        "partition",
        "seq",
        "sha1",
        "uid",
        "unalloc",
        "used"
])

    def __init__(self, *args, **kwargs):
        #Prime all the properties
        for prop in FileObject._all_properties:
            setattr(self, prop, kwargs.get(prop))

    def __repr__(self):
        parts = []

        def _append_str(name, value):
            if value:
                parts.append("%s=%r" % (name, str(value)))

        for prop in FileObject._all_properties:
            if prop != "byte_runs":
                _append_str(prop, getattr(self, prop))
            else:
                if self.byte_runs:
                    parts.append("byte_runs=%r" % self.byte_runs)

        return "FileObject(" + ", ".join(parts) + ")"

    def populate_from_stat(self, s):
        """Populates FileObject fields from a stat() call."""
        import os
        _typecheck(s, os.stat_result)

        self.mode = s.st_mode
        self.inode = s.st_ino
        self.nlink = s.st_nlink
        self.uid = s.st_uid
        self.gid = s.st_gid
        self.filesize = s.st_size
        #s.st_dev is ignored for now.

        if "st_mtime" in dir(s):
            self.mtime = s.st_mtime

        if "st_atime" in dir(s):
            self.atime = s.st_atime

        if "st_ctime" in dir(s):
            self.ctime = s.st_ctime

        if "st_birthtime" in dir(s):
            self.crtime = s.st_birthtime

    def populate_from_Element(self, e):
        """Populates this CellObject's properties from an ElementTree Element.  The Element need not be retained."""
        _typecheck(e, (ET.Element, ET.ElementTree))

        #Split into namespace and tagname
        (ns, tn) = _qsplit(e.tag)
        assert tn in ["fileobject", "original_fileobject", "parent_object"]

        #Look through direct-child elements for other properties
        for ce in e.findall("./*"):
            (cns, ctn) = _qsplit(ce.tag)

            if ctn == "byte_runs":
                self.byte_runs = ByteRuns()
                self.byte_runs.populate_from_Element(ce)
            elif ctn == "hashdigest":
                if ce.attrib["type"] == "md5":
                    self.md5 = ce.text
                elif ce.attrib["type"] == "sha1":
                    self.sha1 = ce.text
            elif ctn == "original_fileobject":
                self.original_fileobject = FileObject()
                self.original_fileobject.populate_from_Element(ce)
            elif ctn == "parent_object":
                self.parent_object = FileObject()
                self.parent_object.populate_from_Element(ce)
            elif ctn in FileObject._all_properties:
                setattr(self, ctn, ce.text)
            else:
                raise ValueError("Uncertain what to do with this element: %r" % ce)

    def to_Element(self):
        """Creates an ElementTree Element with elements in DFXML schema order."""
        outel = ET.Element("fileobject")

        #Recall that Element text must be a string
        def _append_str(name, value):
            #TODO Need lookup support for diff annos
            if not value is None:
                tmpel = ET.Element(name)
                tmpel.text = str(value)
                outel.append(tmpel)

        def _append_time(name, value):
            if not value is None and value.time:
                tmpel = value.to_Element()
                outel.append(tmpel)

        def _append_bool(name, value):
            if not value is None:
                tmpel = ET.Element(name)
                tmpel.text = str(1 if value else 0)
                outel.append(tmpel)

        _append_str("filename", self.filename)
        _append_str("partition", self.partition)
        _append_str("id", self.id)
        _append_str("name_type", self.name_type)
        _append_str("filesize", self.filesize)
        _append_bool("unalloc", self.unalloc)
        _append_bool("alloc", self.alloc)
        _append_bool("used", self.used)
        _append_bool("orphan", self.orphan)
        _append_str("compressed", self.compressed)
        _append_str("inode", self.inode)
        _append_str("meta_type", self.meta_type)
        _append_str("mode", self.mode)
        _append_str("nlink", self.nlink)
        _append_str("uid", self.uid)
        _append_str("gid", self.gid)
        _append_time("mtime", self.mtime) #TODO Needs handling for prec (maybe not anymore)
        _append_time("ctime", self.ctime) #TODO Needs handling for prec
        _append_time("atime", self.atime) #TODO Needs handling for prec
        _append_time("crtime", self.crtime) #TODO Needs handling for prec
        _append_str("seq", self.seq)
        _append_time("dtime", self.dtime) #TODO Needs handling for prec
        _append_time("bkup_time", self.bkup_time) #TODO Needs handling for prec

        if self.byte_runs:
            tmpel = self.byte_runs.to_Element()
            outel.append(tmpel)

        if self.md5:
            tmpel = ET.Element("hashdigest")
            tmpel.attrib["type"] = "md5"
            tmpel.text = self.md5
            outel.append(tmpel)

        if self.sha1:
            tmpel = ET.Element("hashdigest")
            tmpel.attrib["type"] = "sha1"
            tmpel.text = self.sha1
            outel.append(tmpel)

        return outel

    def to_dfxml(self):
        return ET.tostring(self.to_Element(), encoding="unicode")

    _comparable_properties = set([
      "alloc",
      "atime",
      "bkup_time",
      "byte_runs",
      "compressed",
      "crtime",
      "dtime",
      "filename",
      "filesize",
      "gid",
      "inode",
      "md5",
      "meta_type",
      "mode",
      "mtime",
      "name_type",
      "nlink",
      "orphan",
      "parent_object",
      "seq",
      "sha1",
      "uid",
      "unalloc",
      "used"
    ])

    def compare_to_original(self):
        self._diffs = set()
        assert self.original_fileobject

        for propname in FileObject._comparable_properties:
            oval = getattr(self.original_fileobject, propname)
            nval = getattr(self, propname)
            if oval is None and nval is None:
                continue
            if oval != nval:
                logging.debug("propname, oval, nval: %r, %r, %r" % (propname, oval, nval))
                self._diffs.add(propname)

    @property
    def alloc(self):
        return self._alloc

    @alloc.setter
    def alloc(self, val):
        self._alloc = _boolcast(val)

    @property
    def atime(self):
        return self._atime

    @atime.setter
    def atime(self, val):
        if val is None:
            self._atime = None
        else:
            checked_val = TimestampObject(val, name="atime")
            self._atime = checked_val

    @property
    def bkup_time(self):
        return self._bkup_time

    @bkup_time.setter
    def bkup_time(self, val):
        if val is None:
            self._bkup_time = None
        else:
            checked_val = TimestampObject(val, name="bkup_time")
            self._bkup_time = checked_val

    @property
    def compressed(self):
        return self._compressed

    @compressed.setter
    def compressed(self, val):
        self._compressed = _boolcast(val)

    @property
    def ctime(self):
        return self._ctime

    @ctime.setter
    def ctime(self, val):
        if val is None:
            self._ctime = None
        else:
            checked_val = TimestampObject(val, name="ctime")
            self._ctime = checked_val

    @property
    def crtime(self):
        return self._crtime

    @crtime.setter
    def crtime(self, val):
        if val is None:
            self._crtime = None
        else:
            checked_val = TimestampObject(val, name="crtime")
            self._crtime = checked_val

    @property
    def diffs(self):
        """This property intentionally has no setter.  To populate, call compare_to_original() after assigning an original_fileobject."""
        return self._diffs

    @property
    def dtime(self):
        return self._dtime

    @dtime.setter
    def dtime(self, val):
        if val is None:
            self._dtime = None
        else:
            checked_val = TimestampObject(val, name="dtime")
            self._dtime = checked_val

    @property
    def filesize(self):
        return self._filesize

    @filesize.setter
    def filesize(self, val):
        self._filesize = _intcast(val)

    @property
    def gid(self):
        return self._gid

    @gid.setter
    def gid(self, val):
        self._gid = _strcast(val)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, val):
        self._id = _intcast(val)

    @property
    def inode(self):
        return self._inode

    @inode.setter
    def inode(self, val):
        self._inode = _intcast(val)

    @property
    def libmagic(self):
        return self._libmagic

    @libmagic.setter
    def libmagic(self, val):
        self._libmagic = _strcast(val)

    @property
    def meta_type(self):
        return self._meta_type

    @meta_type.setter
    def meta_type(self, val):
        self._meta_type = _intcast(val)

    @property
    def mode(self):
        """The security mode is represented in the FileObject as a base-10 integer.  It is serialized as an octal integer as most people expect a Posix permission definition (e.g. 0755)."""
        #TODO This decimal-octal business is worth a unit test.
        return self._mode

    @mode.setter
    def mode(self, val):
        self._mode = _octcast(val)

    @property
    def mtime(self):
        return self._mtime

    @mtime.setter
    def mtime(self, val):
        if val is None:
            self._mtime = None
        else:
            checked_val = TimestampObject(val, name="mtime")
            self._mtime = checked_val

    @property
    def name_type(self):
        return self._name_type

    @name_type.setter
    def name_type(self, val):
        self._name_type = _strcast(val)

    @property
    def nlink(self):
        return self._nlink

    @nlink.setter
    def nlink(self, val):
        self._nlink = _intcast(val)

    @property
    def orphan(self):
        return self._orphan

    @orphan.setter
    def orphan(self, val):
        self._orphan = _boolcast(val)

    @property
    def original_fileobject(self):
        return self._original_fileobject

    @original_fileobject.setter
    def original_fileobject(self, val):
        _typecheck(val, FileObject)
        self._original_fileobject = val

    @property
    def partition(self):
        return self._partition

    @partition.setter
    def partition(self, val):
        self._partition = _intcast(val)

    @property
    def parent_object(self):
        """This object is an extremely sparse FileObject, containing just identifying information.  Alternately, it can be an entire object reference to the parent Object, though uniqueness should be checked."""
        return self._parent_object

    @parent_object.setter
    def parent_object(self, val):
        if not val is None:
            assert isinstance(val, FileObject)
        self._parent_object = val

    @property
    def seq(self):
        return self._seq

    @seq.setter
    def seq(self, val):
        self._seq = _intcast(val)

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, val):
        self._uid = _strcast(val)

    @property
    def unalloc(self):
        return self._unalloc

    @unalloc.setter
    def unalloc(self, val):
        self._unalloc = _boolcast(val)

    @property
    def used(self):
        return self._used

    @used.setter
    def used(self, val):
        self._used = _intcast(val)


class CellObject(object):
    def __init__(self, *args, **kwargs):
        #These properties must be assigned first for sanity check dependencies
        self.name_type = kwargs.get("name_type")

        self.alloc = kwargs.get("alloc")
        self.byte_runs = kwargs.get("byte_runs")
        self.cellpath = kwargs.get("cellpath")
        self.mtime = kwargs.get("mtime")
        self.name = kwargs.get("name")
        self.name_type = kwargs.get("name_type")
        self.root = kwargs.get("root")
        self.original_cellobject = kwargs.get("original_cellobject")

    def __eq__(self, other):
        """Equality is a difficult question on CellObjects.  Use compare()."""
        raise NotImplementedError

    def __ne__(self, other):
        return not self.__eq__(other) #(sic)

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

    def populate_from_Element(self, e):
        """Populates this CellObject's properties from an ElementTree Element.  The Element need not be retained."""
        assert isinstance(e, ET.Element) or isinstance(e, ET.ElementTree)

        #Split into namespace and tagname
        (ns, tn) = _qsplit(e.tag)
        assert tn in ["cellobject", "original_cellobject", "parent_object"]

        if e.attrib.get("root"):
            self.root = e.attrib["root"]

        #Look through direct-child elements for other properties
        for ce in e.findall("./*"):
            (cns, ctn) = _qsplit(ce.tag)
            if ctn == "alloc":
                self.alloc = ce.text
            elif ctn == "byte_runs":
                self.byte_runs = ByteRuns()
                self.byte_runs.populate_from_Element(ce)
            elif ctn == "cellpath":
                self.cellpath = ce.text
            elif ctn == "mtime":
                self.mtime = ce.text
            elif ctn == "name":
                self.name = ce.text
            elif ctn == "name_type":
                self.name_type = ce.text
            elif ctn == "original_cellobject":
                self.original_cellobject = CellObject()
                self.original_cellobject.populate_from_Element(ce)
            elif ctn == "parent_object":
                self.parent_object = CellObject()
                self.parent_object.populate_from_Element(ce)
            else:
                raise ValueError("Uncertain what to do with this element: %r" % ce)

        self.sanity_check()

    def to_Element(self):
        self.sanity_check()

        outel = ET.Element("cellobject")

        #Recall that Element text must be a string
        def _append_str(name, value):
            #TODO Need lookup support for diff annos
            if value:
                tmpel = ET.Element(name)
                tmpel.text = str(value)
                outel.append(tmpel)

        if self.root:
            outel.attrib["root"] = str(self.root)

        _append_str("cellpath", self.cellpath)
        _append_str("name", self.name)
        _append_str("name_type", self.name_type)
        _append_str("alloc", self.alloc)

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
        return ET.tostring(self.to_Element(), encoding="unicode")

    def sanity_check(self):
        if self.name_type and self.name_type != "k":
            if self.mtime:
                logging.debug("Error occurred sanity-checking this CellObject: %r" % (self))
                raise ValueError("A Registry Key (node) is the only kind of CellObject that can have a timestamp.")
            if self.root:
                logging.debug("Error occurred sanity-checking this CellObject: %r" % (self))
                raise ValueError("A Registry Key (node) is the only kind of CellObject that can have the 'root' attribute.")

    _comparable_properties = set([
      "cellpath",
      "name",
      "name_type",
      "alloc",
      "mtime"
    ])

    def compare_to_original(self):
        assert self.original_cellobject

        self._diffs = set()

        for propname in CellObject._comparable_properties:
            oval = getattr(self.original_cellobject, propname)
            nval = getattr(self, propname)
            if oval is None and nval is None:
                continue
            if oval != nval:
                logging.debug("propname, oval, nval: %r, %r, %r" % (propname, oval, nval))
                self._diffs.add(propname)

    @property
    def alloc(self):
        return self._alloc

    @alloc.setter
    def alloc(self, val):
        self._alloc = _boolcast(val)

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
    def diffs(self):
        return self._diffs

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
    def parent_object(self):
        """This object is an extremely sparse CellObject, containing just identifying information.  Alternately, it can be an entire object reference to the parent Object, though uniqueness should be checked."""
        return self._parent_object

    @parent_object.setter
    def parent_object(self, val):
        if not val is None:
            assert isinstance(val, CellObject)
        self._parent_object = val

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
        self._root = _boolcast(val)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    
    logging.basicConfig(level=logging.DEBUG)
    #Run unit tests

    assert _qsplit("{http://www.w3.org/2001/XMLSchema}all") == ("http://www.w3.org/2001/XMLSchema","all")
    assert _qsplit("http://www.w3.org/2001/XMLSchema}all") == (None, "http://www.w3.org/2001/XMLSchema}all")

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

    coe = co.to_Element()
    nco = CellObject()
    nco.populate_from_Element(coe)

    assert co.byte_runs == nco.byte_runs

    nco.name = "(Doubled)"
    nco.root = False
    nco.byte_runs[0].file_offset += 133

    logging.debug("co.byte_runs = %r" % co.byte_runs)
    logging.debug("nco.byte_runs = %r" % nco.byte_runs)
    assert co.byte_runs != nco.byte_runs

    failed = None
    try:
        co == nco
    except NotImplementedError:
        failed = True
    assert failed

    print(nco.to_regxml())

    nco.original_cellobject = co
    nco.compare_to_original()
    print(nco.diffs)

    ro = RegXMLObject(version="2.0")
    ho = HiveObject()
    ho.append(co)
    ho.append(nco)
    ro.append(ho)
    ro.print_regxml()

    ofo = FileObject()
    parent = FileObject()
    parent.inode = 234
    ofo.parent_object = parent
    ofo.filename = "test file"
    ofo.error = "Neither a real file, nor real error"
    ofo.partition = 2
    ofo.id = 235
    ofo.name_type = "r"
    ofo.filesize = 1234
    ofo.unalloc = 0
    ofo.unused = 0
    ofo.orphan = 0
    ofo.compressed = 1
    ofo.inode = 6543
    ofo.meta_type = 8
    ofo.mode = 755
    ofo.nlink = 1
    ofo.uid = "S-1-234-etc"
    ofo.gid = "S-2-234-etc"
    ofo.mtime = "1999-12-31T12:34:56Z"
    ofo.ctime = "1998-12-31T12:34:56Z"
    ofo.atime = "1997-12-31T12:34:56Z"
    ofo.crtime = "1996-12-31T12:34:56Z"
    ofo.seq = 3
    ofo.dtime = "1995-12-31T12:34:56Z"
    ofo.bkup_time = "1994-12-31T12:34:56Z"
    ofo.link_target = "Nonexistent file"
    ofo.libmagic = "Some kind of compressed"
    ofo.sha1 = "7d97e98f8af710c7e7fe703abc8f639e0ee507c4"   
    ofo.md5 = "2b00042f7481c7b056c4b410d28f33cf"
    ofo.brs = brs
    print(ofo.to_dfxml())

    ofoe = ofo.to_Element()
    nfo = FileObject()
    nfo.populate_from_Element(ofoe)
    nfo.mtime = "2013-12-31T12:34:56Z"
    nfo.sha1 = "447d306060631570b7713ea48e74103c68eab0a3"
    nfo.md5 = "b9eb9d6228842aeb05d64f30d56b361e"
    nfo.id += 1
    nfo.original_fileobject = ofo
    #nfo.byte_runs = nco.byte_runs #TODO
    print(nfo.to_dfxml())

    nfo.compare_to_original()
    print(nfo.diffs)

    import os
    s = os.stat(__file__)
    sfo = FileObject()
    sfo.populate_from_stat(s)
    print(sfo.to_dfxml())

    print("Unit tests passed.")
