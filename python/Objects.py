
"""
This file re-creates the major DFXML classes with an emphasis on type safety, serializability, and de-serializability.

Consider this file highly experimental (read: unstable).
"""

__version__ = "0.0.34"

#Remaining roadmap to 0.1.0:
# * Make sure object annos are read in from DFXML files
# * Ensure ctrl-c works in the extraction loops (did it before, in dfxml.py's .contents()?)

import logging
import re
import copy
import xml.etree.ElementTree as ET
import subprocess
import dfxml
import os
import sys

_logger = logging.getLogger(os.path.basename(__file__))

#Contains: (namespace, local name) qualified XML element name pairs
_warned_elements = set([])

#Issue some log statements only once per program invocation.
_nagged_alloc = False
_warned_byterun_badtypecomp = False

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

    _logger.debug("val = " + repr(val))
    raise ValueError("Received a not-straightforwardly-Boolean value.  Expected some form of 0, 1, True, or False.")

def _bytecast(val):
    """Casts a value as a byte string.  If a character string, assumes a UTF-8 encoding."""
    if val is None:
        return None
    if isinstance(val, bytes):
        return val
    return _strcast(val).encode("utf-8")

def _intcast(val):
    """Casts input integer or string to integer.  Preserves nulls.  Balks at everything else."""
    if val is None:
        return None
    if isinstance(val, int):
        return val

    if isinstance(val, str):
        if val[0] == "-":
            if val[1:].isdigit():
                return int(val)
        else:
            if val.isdigit():
                return int(val)

    _logger.debug("val = " + repr(val))
    raise ValueError("Received a non-int-castable value.  Expected an integer or an integer as a string.")

def _read_differential_annotations(annodict, element, annoset):
    """
    Uses the shorthand-to-attribute mappings of annodict to translate attributes of element into annoset.
    """
    #Start with inverting the dictionary
    _d = { annodict[k].replace("delta:",""):k for k in annodict }
    #_logger.debug("Inverted dictionary: _d = %r" % _d)
    for attr in element.attrib:
        #_logger.debug("Looking for differential annotations: %r" % e.attrib)
        (ns, an) = _qsplit(attr)
        if an in _d and ns == dfxml.XMLNS_DELTA:
            #_logger.debug("Found; adding _d[an]=%r." % _d[an])
            annoset.add(_d[an])

def _qsplit(tagname):
    """Requires string input.  Returns namespace and local tag name as a pair.  I could've sworn this was a basic implementation gimme, but ET.QName ain't it."""
    _typecheck(tagname, str)
    if tagname[0] == "{":
        i = tagname.rfind("}")
        return ( tagname[1:i], tagname[i+1:] )
    else:
        return (None, tagname)

def _strcast(val):
    if val is None:
        return None
    return str(val)

def _typecheck(obj, classinfo):
    if not isinstance(obj, classinfo):
        _logger.info("obj = " + repr(obj))
        if isinstance(classinfo, tuple):
            raise TypeError("Expecting object to be one of the types %r." % (classinfo,))
        else:
            raise TypeError("Expecting object to be of type %r." % classinfo)

class DFXMLBaseObject(object):
    "Coming soon."

    def __init__(self, *args, **kwargs):
        pass

class DFXMLObject(object):
    def __init__(self, *args, **kwargs):
        self.command_line = kwargs.get("command_line")
        self.version = kwargs.get("version")
        self.sources = kwargs.get("sources", [])

        self._namespaces = dict()
        self._volumes = []
        self._files = []

        input_volumes = kwargs.get("volumes") or []
        input_files = kwargs.get("files") or []
        for v in input_volumes:
            self.append(v)
        for f in input_files:
            self.append(f)

        #Add default namespaces
        self.add_namespace("", dfxml.XMLNS_DFXML)
        self.add_namespace("dc", dfxml.XMLNS_DC)

    def __iter__(self):
        """Yields all VolumeObjects, recursively their FileObjects, and the FileObjects directly attached to this DFXMLObject, in that order."""
        for v in self._volumes:
            yield v
            for f in v:
                yield f
        for f in self._files:
            yield f

    def add_namespace(self, prefix, url):
        self._namespaces[prefix] = url
        ET.register_namespace(prefix, url)

    def append(self, value):
        if isinstance(value, VolumeObject):
            self._volumes.append(value)
        elif isinstance(value, FileObject):
            self._files.append(value)
        else:
            _logger.debug("value = %r" % value)
            raise TypeError("Expecting a VolumeObject or a FileObject.  Got instead this type: %r." % type(value))

    def iter_namespaces(self):
        """Yields (prefix, url) pairs of each namespace registered in this DFXMLObject."""
        for prefix in self._namespaces:
            yield (prefix, self._namespaces[prefix])

    def populate_from_Element(self, e):
        if "version" in e.attrib:
            self.version = e.attrib["version"]

        for elem in e.findall(".//*"):
            (ns, ln) = _qsplit(elem.tag)
            if ln == "command_line":
                self.command_line = elem.text
            elif ln == "image_filename":
                self.sources.append(elem.text)

    def print_dfxml(self, output_fh=sys.stdout):
        """Memory-efficient DFXML document printer.  However, it assumes the whole element tree is already constructed."""
        pe = self.to_partial_Element()
        dfxml_wrapper = ET.tostring(pe, encoding="unicode")

        #If there are no children, this (trivial) document needs only a simpler printing.
        if len(pe) == 0 and len(self._volumes) == 0 and len(self._files) == 0:
            _logger.debug("This DFXML document has no children.  An empty tree is being printed with a code shortcut.")
            output_fh.write(dfxml_wrapper)
            return

        dfxml_foot = "</dfxml>"
        dfxml_head = dfxml_wrapper.strip()[:-len(dfxml_foot)]

        output_fh.write("""<?xml version="1.0"?>\n""")
        output_fh.write(dfxml_head)
        output_fh.write("\n")
        _logger.debug("Writing %d volume objects." % len(self._volumes))
        for v in self._volumes:
            v.print_dfxml(output_fh)
            output_fh.write("\n")
        _logger.debug("Writing %d file objects." % len(self._files))
        for f in self._files:
            e = f.to_Element()
            output_fh.write(ET.tostring(e, encoding="unicode"))
            output_fh.write("\n")
        output_fh.write(dfxml_foot)
        output_fh.write("\n")

    def to_Element(self):
        outel = self.to_partial_Element()
        for v in self._volumes:
            tmpel = v.to_Element()
            outel.append(tmpel)
        for f in self._files:
            tmpel = f.to_Element()
            outel.append(tmpel)
        return outel

    def to_dfxml(self):
        """Serializes the entire DFXML document tree into a string.  Then returns that string.  RAM-intensive."""
        return ET.tostring(self.to_Element(), encoding="unicode")

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

        if len(self.sources) > 0:
            tmpel0 = ET.Element("source")
            for source in self.sources:
                tmpel1 = ET.Element("image_filename")
                tmpel1.text = source
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

    @property
    def command_line(self):
        return self._command_line

    @command_line.setter
    def command_line(self, value):
        self._command_line = _strcast(value)

    @property
    def namespaces(self):
        raise AttributeError("The namespaces dictionary should not be directly accessed; instead, use .iter_namespaces().")

    @property
    def sources(self):
        return self._sources

    @sources.setter
    def sources(self, value):
        if not value is None:
            _typecheck(value, list)
        self._sources = value

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
            _logger.debug("value = %r" % value)
            raise TypeError("Expecting a HiveObject or a CellObject.  Got instead this type: %r." % type(value))

    def print_regxml(self):
        """Serializes and prints the entire object, without constructing the whole tree."""
        regxml_wrapper = ET.tostring(self.to_partial_Element(), encoding="unicode")
        regxml_foot = "</regxml>"
        regxml_head = regxml_wrapper.strip()[:-len(regxml_foot)]

        print(regxml_head)
        for hive in self._hives:
            hive.print_regxml()
        print(regxml_foot)

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


class VolumeObject(object):
    _all_properties = set([
      "annos",
      "byte_runs",
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

    _diff_attr_names = {
      "new":"delta:new_volume",
      "deleted":"delta:deleted_volume",
      "modified":"delta:modified_volume",
      "matched":"delta:matched"
    }

    #TODO There may be need in the future to compare the annotations as well.  It complicates make_differential_dfxml too much for now.
    _incomparable_properties = set([
      "annos"
    ])

    def __init__(self, *args, **kwargs):
        self._files = []
        self._original_volume = None
        self._annos = set()
        self._diffs = set()

        for prop in VolumeObject._all_properties:
            if prop in ["annos", "files"]:
                continue
            setattr(self, prop, kwargs.get(prop))

    def __iter__(self):
        """Yields all FileObjects directly attached to this VolumeObject."""
        for f in self._files:
            yield f

    def __repr__(self):
        parts = []
        for prop in VolumeObject._all_properties:
            #Skip outputting the files list.
            if prop == "files":
                continue
            val = getattr(self, prop)
            if not val is None:
                parts.append("%s=%r" % (prop, val))
        return "VolumeObject(" + ", ".join(parts) + ")"

    def append(self, value):
        _typecheck(value, FileObject)
        self._files.append(value)

    def compare_to_original(self):
        self._diffs = self.compare_to_other(self.original_volume)

    def compare_to_other(self, other):
        """Returns a set of all the properties found to differ."""
        _typecheck(other, VolumeObject)
        diffs = set()
        for prop in VolumeObject._all_properties:
            if prop in VolumeObject._incomparable_properties:
                continue
            #_logger.debug("getattr(self, %r) = %r" % (prop, getattr(self, prop)))
            #_logger.debug("getattr(other, %r) = %r" % (prop, getattr(other, prop)))
            if getattr(self, prop) != getattr(other, prop):
                diffs.add(prop)
        return diffs

    def populate_from_Element(self, e):
        global _warned_elements
        _typecheck(e, (ET.Element, ET.ElementTree))
        #_logger.debug("e = %r" % e)

        #Read differential annotations
        _read_differential_annotations(VolumeObject._diff_attr_names, e, self.annos)

        #Split into namespace and tagname
        (ns, tn) = _qsplit(e.tag)
        assert tn in ["volume", "original_volume"]

        #Look through direct-child elements to populate run array
        for ce in e.findall("./*"):
            #_logger.debug("ce = %r" % ce)
            (cns, ctn) = _qsplit(ce.tag)
            #_logger.debug("cns = %r" % cns)
            #_logger.debug("ctn = %r" % ctn)
            if ctn == "byte_runs":
                self.byte_runs = ByteRuns()
                self.byte_runs.populate_from_Element(ce)
            elif ctn == "original_volume":
                self.original_volume = VolumeObject()
                self.original_volume.populate_from_Element(ce)
            elif ctn in VolumeObject._all_properties:
                #_logger.debug("ce.text = %r" % ce.text)
                setattr(self, ctn, ce.text)
                #_logger.debug("getattr(self, %r) = %r" % (ctn, getattr(self, ctn)))
            else:
                if (cns, ctn) not in _warned_elements:
                    _warned_elements.add((cns, ctn))
                    _logger.warning("Unsure what to do with this element in a VolumeObject: %r" % ce)

    def print_dfxml(self, output_fh=sys.stdout):
        pe = self.to_partial_Element()
        dfxml_wrapper = ET.tostring(pe, encoding="unicode")

        if len(pe) == 0 and len(self._files) == 0:
            output_fh.write(dfxml_wrapper)
            return

        dfxml_foot = "</volume>"

        #Deal with an empty element being printed as <elem/>
        if len(pe) == 0:
            replaced_dfxml_wrapper = dfxml_wrapper.replace(" />", ">")
            dfxml_head = replaced_dfxml_wrapper
        else:
            dfxml_head = dfxml_wrapper.strip()[:-len(dfxml_foot)]

        output_fh.write(dfxml_head)
        output_fh.write("\n")
        _logger.debug("Writing %d file objects for this volume." % len(self._files))
        for f in self._files:
            e = f.to_Element()
            output_fh.write(ET.tostring(e, encoding="unicode"))
            output_fh.write("\n")
        output_fh.write(dfxml_foot)
        output_fh.write("\n")

    def to_Element(self):
        outel = self.to_partial_Element()
        for f in self._files:
            tmpel = f.to_Element()
            outel.append(tmpel)
        return outel

    def to_partial_Element(self):
        """Returns the volume element with its properties, except for the child fileobjects.  Properties are appended in DFXML schema order."""
        outel = ET.Element("volume")

        if len(self.diffs) > 0:
            #TODO The diffs appear to be attaching to the wrong object.  It seems to be time to use .annos as well.
            _logger.debug("self.diffs = %s." % repr(self.diffs))
            outel.attrib["delta:modified_volume"] = "1"

        if self.byte_runs:
            outel.append(self.byte_runs.to_Element())

        def _append_el(prop, value):
            tmpel = ET.Element(prop)
            _keep = False
            if not value is None:
                tmpel.text = str(value)
                _keep = True
            if prop in self.diffs:
                tmpel.attrib["delta:changed_property"] = "1"
                _keep = True
            if _keep:
                outel.append(tmpel)

        def _append_str(prop):
            value = getattr(self, prop)
            _append_el(prop, value)

        def _append_bool(prop):
            value = getattr(self, prop)
            if not value is None:
                value = "1" if value else "0"
            _append_el(prop, value)

        for prop in [
          "partition_offset",
          "sector_size",
          "block_size",
          "ftype",
          "ftype_str",
          "block_count",
          "first_block",
          "last_block"
        ]:
            _append_str(prop)

        #Output the one Boolean property
        _append_bool("allocated_only")

        #Output the original volume's properties
        if not self.original_volume is None:
            #Skip FileObject list, if any
            tmpel = self.original_volume.to_partial_Element()
            tmpel.tag = "delta:original_volume"
            outel.append(tmpel)

        return outel

    @property
    def allocated_only(self):
        return self._allocated_only

    @allocated_only.setter
    def allocated_only(self, val):
        self._allocated_only = _boolcast(val)

    @property
    def annos(self):
        """Set of differential annotations.  Expected members are the keys of this class's _diff_attr_names dictionary."""
        return self._annos

    @annos.setter
    def annos(self, val):
        _typecheck(val, set)
        self._annos = val

    @property
    def block_count(self):
        return self._block_count

    @block_count.setter
    def block_count(self, val):
        self._block_count = _intcast(val)

    @property
    def block_size(self):
        return self._block_size

    @block_size.setter
    def block_size(self, val):
        self._block_size = _intcast(val)

    @property
    def diffs(self):
        return self._diffs

    @property
    def first_block(self):
        return self._first_block

    @first_block.setter
    def first_block(self, val):
        self._first_block = _intcast(val)

    @property
    def ftype(self):
        return self._ftype

    @ftype.setter
    def ftype(self, val):
        self._ftype = _intcast(val)

    @property
    def ftype_str(self):
        return self._ftype_str

    @ftype_str.setter
    def ftype_str(self, val):
        self._ftype_str = _strcast(val)

    @property
    def last_block(self):
        return self._last_block

    @last_block.setter
    def last_block(self, val):
        self._last_block = _intcast(val)

    @property
    def original_volume(self):
        return self._original_volume

    @original_volume.setter
    def original_volume(self, val):
        if not val is None:
            _typecheck(val, VolumeObject)
        self._original_volume= val

    @property
    def partition_offset(self):
        return self._partition_offset

    @partition_offset.setter
    def partition_offset(self, val):
        self._partition_offset = _intcast(val)

    @property
    def sector_size(self):
        return self._sector_size

    @sector_size.setter
    def sector_size(self, val):
        self._sector_size = _intcast(val)

class HiveObject(object):
    def __init__(self, *args, **kwargs):
        self._cells = []

    def append(self, value):
        _typecheck(value, CellObject)
        self._cells.append(value)

    def print_regxml(self):
        for cell in self._cells:
            print(cell.to_regxml())

    def to_Element(self):
        outel = ET.Element("hive")
        for cell in self._cells:
            tmpel = cell.to_Element()
            outel.append(tmpel)
        return outel

class ByteRun(object):

    _all_properties = set([
      "img_offset",
      "fs_offset",
      "file_offset",
      "fill",
      "len"
    ])

    def __init__(self, *args, **kwargs):
        for prop in ByteRun._all_properties:
            setattr(self, prop, kwargs.get(prop))

    def __eq__(self, other):
        #Check type
        if other is None:
            return False
        if not isinstance(other, ByteRun):
            if not _warned_byterun_badtypecomp:
                _logger.warning("A ByteRun comparison was called against a non-ByteRun object: " + repr(other) + ".")
                _warned_byterun_badtypecomp = True
            return False

        #Check values
        return \
          self.img_offset == other.img_offset and \
          self.fs_offset == other.fs_offset and \
          self.file_offset == other.file_offset and \
          self.fill == other.fill and \
          self.len == other.len

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        parts = []
        for prop in ByteRun._all_properties:
            val = getattr(self, prop)
            if not val is None:
                parts.append("%s=%r" % (prop, val))
        return "ByteRun(" + ", ".join(parts) + ")"

    def populate_from_Element(self, e):
        _typecheck(e, (ET.Element, ET.ElementTree))

        #Split into namespace and tagname
        (ns, tn) = _qsplit(e.tag)
        assert tn == "byte_run"

        #Populate run properties from element attributes
        for prop in ByteRun._all_properties:
            val = e.attrib.get(prop)
            if not val is None:
                setattr(self, prop, val)

    def to_Element(self):
        outel = ET.Element("byte_run")
        for prop in ByteRun._all_properties:
            val = getattr(self, prop)
            if not val is None:
                outel.attrib[prop] = str(val)
        return outel

    @property
    def file_offset(self):
        return self._file_offset

    @file_offset.setter
    def file_offset(self, val):
        self._file_offset = _intcast(val)

    @property
    def fill(self):
        """There is an implicit assumption that the fill character is encoded as UTF-8."""
        return self._fill

    @fill.setter
    def fill(self, val):
        self._fill = _bytecast(val)

    @property
    def fs_offset(self):
        return self._fs_offset

    @fs_offset.setter
    def fs_offset(self, val):
        self._fs_offset = _intcast(val)

    @property
    def img_offset(self):
        return self._img_offset

    @img_offset.setter
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

    def __delitem__(self, key):
        del self._listdata[key]

    def __eq__(self, other):
        """Compares the byte run lists."""
        #Check type
        if other is None:
            return False
        _typecheck(other, ByteRuns)

        if len(self) != len(other):
            #_logger.debug("len(self) = %d" % len(self))
            #_logger.debug("len(other) = %d" % len(other))
            return False
        for (sbr_index, sbr) in enumerate(self):
            obr = other[sbr_index]
            #_logger.debug("sbr_index = %d" % sbr_index)
            #_logger.debug("sbr = %r" % sbr)
            #_logger.debug("obr = %r" % obr)
            if sbr != obr:
                return False
        return True

    def __getitem__(self, key):
        return self._listdata.__getitem__(key)

    def __iter__(self):
        return iter(self._listdata)

    def __len__(self):
        return self._listdata.__len__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        parts = []
        for run in self:
            parts.append(repr(run))
        return "ByteRuns(run_list=[" + ", ".join(parts) + "])"

    def __setitem__(self, key, value):
        _typecheck(value, ByteRun)
        self._listdata[key] = value

    def append(self, value):
        _typecheck(value, ByteRun)
        self._listdata.append(value)

    def iter_contents(self, raw_image, buffer_size=1048576, sector_size=512, errlog=None, statlog=None):
        """
        Generator.  Yields contents, as byte strings one block at a time, given a backing raw image path.  Relies on The SleuthKit's img_cat, so contents can be extracted from any disk image type that TSK supports.
        @param buffer_size The maximum size of the byte strings yielded.
        @param sector_size The size of a disk sector in the raw image.  Required by img_cat.
        """
        if not isinstance(raw_image, str):
            raise TypeError("iter_contents needs the string path to the image file.  Received: %r." % raw_image)

        stderr_fh = None
        if not errlog is None:
            stderr_fh = open(errlog, "wb")

        status_fh = None
        if not statlog is None:
            status_fh = open(errlog, "wb")

        #The exit status of the last img_cat.
        last_status = None

        try:
            for run in self:
                if run.len is None:
                    raise AttributeError("Byte runs can't be extracted if a run length is undefined.")

                len_to_read = run.len

                #If we have a fill character, just pump out that character
                if not run.fill is None and len(run.fill) > 0:
                    while len_to_read > 0:
                        #This multiplication and slice should handle multi-byte fill characters, in case that ever comes up.
                        yield (run.fill * buffer_size)[:len_to_read]
                        len_to_read -= buffer_size
                    #Next byte run
                    continue

                if run.img_offset is None:
                    raise AttributeError("Byte runs can't be extracted if missing a fill character and image offset.")

                cmd = ["img_cat"]
                cmd.append("-b")
                cmd.append(str(sector_size))
                cmd.append("-s")
                cmd.append(str(run.img_offset//sector_size))
                cmd.append("-e")
                cmd.append(str( (run.img_offset + run.len)//sector_size))
                cmd.append(raw_image)
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=stderr_fh)

                #Do the buffered read
                while len_to_read > 0:
                    buffer_data = p.stdout.read(buffer_size)
                    yield_data = buffer_data[ : min(len_to_read, buffer_size)]
                    if len(yield_data) > 0:
                        yield yield_data
                    else:
                        #Let the subprocess terminate so we can see the exit status
                        p.wait()
                        last_status = p.returncode
                        if last_status != 0:
                            e = subprocess.CalledProcessError("img_cat failed.")
                            e.returncode = last_status
                            e.cmd = cmd
                            raise e
                    len_to_read -= buffer_size
        except Exception as e:
            #Cleanup in an exception
            if not stderr_fh is None:
                stderr_fh.close()

            if not status_fh is None:
                if isinstance(e, subprocess.CalledProcessError):
                    status_fh.write(e.returncode)
                else:
                    status_fh.write("1")
                status_fh.close()
            raise e

        #Cleanup when all's gone well.
        if not status_fh is None:
            if not last_status is None:
                status_fh.write(last_status)
            status_fh.close()
        if not stderr_fh is None:
            stderr_fh.close()

    def populate_from_Element(self, e):
        _typecheck(e, (ET.Element, ET.ElementTree))

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

    def to_Element(self):
        outel = ET.Element("byte_runs")
        for run in self:
            tmpel = run.to_Element()
            outel.append(tmpel)
        return outel

re_precision = re.compile(r"(?P<num>\d+)(?P<unit>(|m|n)s|d)?")
class TimestampObject(object):
    """
    Encodes the "dftime" type.  Wraps around dfxml.dftime, closely enough that this might just get folded into that class.

    TimestampObjects implement a vs-null comparison workaround as in the SAS family of products:  Null, for ordering purposes, is considered to be a value less than negative infinity.
    """

    timestamp_name_list = ["mtime", "atime", "ctime", "crtime", "dtime", "bkup_time"]

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name")
        self.prec = kwargs.get("prec")
        #_logger.debug("type(args) = %r" % type(args))
        #_logger.debug("args = %r" % (args,))
        if len(args) == 0:
            self.time = None
        elif len(args) == 1:
            self.time = args[0]
        else:
            raise ValueError("Unexpected arguments.  Whole args tuple: %r." % (args,))

    def __eq__(self, other):
        #Check type
        if other is None:
            return False
        _typecheck(other, TimestampObject)

        if self.name != other.name:
            return False
        if self.prec != other.prec:
            return False
        if self.time != other.time:
            return False
        return True

    def __ge__(self, other):
        """Note: The semantics here and in other ordering functions are that "Null" is a value less than negative infinity."""
        if other is None:
            return False
        else:
            self._comparison_sanity_check(other)
        return self.time.__ge__(other.time)

    def __gt__(self, other):
        """Note: The semantics here and in other ordering functions are that "Null" is a value less than negative infinity."""
        if other is None:
            return False
        else:
            self._comparison_sanity_check(other)
        return self.time.__gt__(other.time)

    def __le__(self, other):
        """Note: The semantics here and in other ordering functions are that "Null" is a value less than negative infinity."""
        if other is None:
            return True
        else:
            self._comparison_sanity_check(other)
        return self.time.__le__(other.time)

    def __lt__(self, other):
        """Note: The semantics here and in other ordering functions are that "Null" is a value less than negative infinity."""
        if other is None:
            return True
        else:
            self._comparison_sanity_check(other)
        return self.time.__lt__(other.time)

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

    def __str__(self):
        if self.time:
            return str(self.time)
        else:
            return self.__repr__()

    def _comparison_sanity_check(self, other):
        if None in (self.time, other.time):
            raise ValueError("Can't compare TimestampObjects: %r, %r." % self, other)

    def to_Element(self):
        _typecheck(self.name, str)
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
        #_logger.debug("tup = %r" % (tup,))
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
            #_logger.debug("checked_value.timestamp() = %r" % checked_value.timestamp())
            self._time = checked_value


class FileObject(object):
    """
    This class provides property accesses, an XML serializer (ElementTree-based), and a deserializer.
    The properties interface is NOT function calls, but simple accesses.  That is, the old _fileobject_ style:

        assert isinstance(fi, dfxml.fileobject)
        fi.mtime()

    is now replaced with:

        assert isinstance(fi, Objects.FileObject)
        fi.mtime
    """

    _all_properties = set([
      "alloc",
      "alloc_inode",
      "alloc_name",
      "annos",
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
      "link_target",
      "libmagic",
      "md5",
      "meta_type",
      "mode",
      "mtime",
      "name_type",
      "nlink",
      "original_fileobject",
      "orphan",
      "parent_object",
      "partition",
      "seq",
      "sha1",
      "uid",
      "unalloc",
      "unused",
      "used"
    ])

    #TODO There may be need in the future to compare the annotations as well.  It complicates make_differential_dfxml too much for now.
    _incomparable_properties = set([
      "annos",
      "id"
    ])

    _diff_attr_names = {
      "new":"delta:new_file",
      "deleted":"delta:deleted_file",
      "renamed":"delta:renamed_file",
      "changed":"delta:changed_file",
      "modified":"delta:modified_file",
      "matched":"delta:matched"
    }

    def __init__(self, *args, **kwargs):
        #Prime all the properties
        for prop in FileObject._all_properties:
            if prop == "annos":
                continue
            setattr(self, prop, kwargs.get(prop))
        self._annos = set()
        self._diffs = set()

    def __eq__(self, other):
        if other is None:
            return False
        _typecheck(other, FileObject)
        for prop in FileObject._all_properties:
            if prop in FileObject._incomparable_properties:
                continue
            if getattr(self, prop) != getattr(other, prop):
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        parts = []

        for prop in sorted(FileObject._all_properties):
            #Save byte runs for the end
            if prop != "byte_runs":
                value = getattr(self, prop)
                if not value is None:
                    parts.append("%s=%r" % (prop, value))

        if self.byte_runs:
            parts.append("byte_runs=%r" % self.byte_runs)

        return "FileObject(" + ", ".join(parts) + ")"

    def compare_to_original(self):
        self._diffs = self.compare_to_other(self.original_fileobject, True)

    def compare_to_other(self, other, ignore_original=False):
        _typecheck(other, FileObject)

        diffs = set()

        for propname in FileObject._all_properties:
            if propname in FileObject._incomparable_properties:
                continue
            if ignore_original and propname == "original_fileobject":
                continue
            oval = getattr(other, propname)
            nval = getattr(self, propname)
            if oval is None and nval is None:
                continue
            if oval != nval:
                #_logger.debug("propname, oval, nval: %r, %r, %r" % (propname, oval, nval))
                diffs.add(propname)

        return diffs

    def extract_facet(self, facet, image_path=None, buffer_size=1048576, partition_offset=None, sector_size=512, errlog=None, statlog=None, icat_threshold = 268435456):
        """
        Generator.  Extracts the facet with a SleuthKit tool, yielding chunks of the data.

        @param buffer_size The facet data is yielded in chunks of at most this parameter's size. Default 1MiB.
        @param partition_offset The offset of the file's containing partition, in bytes.  Needed for icat.  If not given, the FileObject's VolumeObject will be used.  If that's also absent, icat can't be used, and img_cat will instead be tried as a fallback (which means byte runs must be in the DFXML).
        @param icat_threshold icat incurs extensive, non-sequential IO overhead to walk the filesystem to reach the facet's byte runs.  img_cat can be called on each byte run reported in the DFXML file, but on fragmented files this incurs overhead in process spawning.  Facets larger than this threshold are extracted with icat.  Default 256MiB.  Force icat by setting this to -1; force img_cat with infinity (float("inf")).
        """

        _image_path = image_path
        if _image_path is None:
            raise ValueError("The backing image path must be supplied.")

        _partition_offset = partition_offset
        if _partition_offset is None:
            if self.volume_object:
                _partition_offset = self.volume_object.partition_offset

        #Try using icat; needs inode number and volume offset.  We're additionally requiring the filesize be known.
        #TODO The icat needs a little more experimentation.
        if False and facet == "content" and \
          not self.filesize is None and \
          self.filesize >= icat_threshold and \
          not self.inode is None and \
          not _partition_offset is None:
            _logger.debug("Extracting with icat: %r." % self)

            #Set up logging if desired
            stderr_fh = sys.stderr
            if not errlog is None:
                stderr_fh = open(errlog, "wb")

            status_fh = None
            if not statlog is None:
                status_fh = open(errlog, "w")

            #Set up icat process
            cmd = ["icat"]
            cmd.append("-b")
            cmd.append(str(sector_size))
            cmd.append("-o")
            cmd.append(str(self.volume_object.partition_offset//sector_size))
            if not self.volume_object.ftype_str is None:
                cmd.append("-f")
                cmd.append(self.volume_object.ftype_str)
            cmd.append(image_path)
            cmd.append(str(self.inode))
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=stderr_fh)

            #Do a buffered read
            len_to_read = self.filesize
            while len_to_read > 0:
                buffer_data = p.stdout.read(buffer_size)
                yield_data = buffer_data[ : min(len_to_read, buffer_size)]
                if len(yield_data) > 0:
                    yield yield_data
                else:
                    #Let the subprocess terminate so we can see the exit status
                    p.wait()
                    last_status = p.returncode

                    #Log the status if requested
                    if not status_fh is None:
                        status_fh.write(last_status)

                    #Act on a bad status
                    if last_status != 0:
                        e = subprocess.CalledProcessError("icat failed.")
                        e.returncode = last_status
                        e.cmd = cmd
                        raise e
                len_to_read -= buffer_size

            #Clean up file handles
            if status_fh: status_fh.close()
            if stderr_fh: stderr_fh.close()
            
        elif not self.byte_runs is None:
            for chunk in self.byte_runs.iter_contents(_image_path, buffer_size, sector_size, errlog, statlog):
                yield chunk

    def populate_from_Element(self, e):
        """Populates this FileObject's properties from an ElementTree Element.  The Element need not be retained."""
        global _warned_elements
        _typecheck(e, (ET.Element, ET.ElementTree))

        #_logger.debug("FileObject.populate_from_Element(%r)" % e)

        #Split into namespace and tagname
        (ns, tn) = _qsplit(e.tag)
        assert tn in ["fileobject", "original_fileobject", "parent_object"]

        #Map "delta:" attributes of <fileobject>s into the self.annos set
        _read_differential_annotations(FileObject._diff_attr_names, e, self.annos)

        #Look through direct-child elements for other properties
        for ce in e.findall("./*"):
            (cns, ctn) = _qsplit(ce.tag)

            #Inherit any marked changes
            for attr in e.attrib:
                (ns, an) = _qsplit(attr)
                if an == "changed_property" and ns == dfxml.XMLNS_DELTA:
                    self.diffs.add(ctn)

            if ctn == "byte_runs":
                self.byte_runs = ByteRuns()
                self.byte_runs.populate_from_Element(ce)
            elif ctn == "hashdigest":
                if ce.attrib["type"].lower() == "md5":
                    self.md5 = ce.text
                elif ce.attrib["type"].lower() == "sha1":
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
                if (cns, ctn) not in _warned_elements:
                    _warned_elements.add((cns, ctn))
                    _logger.warning("Uncertain what to do with this element: %r" % ce)

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

    def to_Element(self):
        """Creates an ElementTree Element with elements in DFXML schema order."""
        outel = ET.Element("fileobject")

        annos_whittle_set = copy.deepcopy(self.annos)
        diffs_whittle_set = copy.deepcopy(self.diffs)

        for annodiff in FileObject._diff_attr_names:
            if annodiff in annos_whittle_set:
                outel.attrib[FileObject._diff_attr_names[annodiff]] = "1"
                annos_whittle_set.remove(annodiff)

        def _anno_change(el):
            if el.tag in self.diffs:
                el.attrib["delta:changed_property"] = "1"
                diffs_whittle_set.remove(el.tag)

        def _anno_hash(el):
            if el.attrib["type"] in self.diffs:
                el.attrib["delta:changed_property"] = "1"
                diffs_whittle_set.remove(el.attrib["type"])

        #Recall that Element text must be a string
        def _append_str(name, value):
            #TODO Need lookup support for diff annos
            if not value is None or name in diffs_whittle_set:
                tmpel = ET.Element(name)
                if not value is None:
                    tmpel.text = str(value)
                _anno_change(tmpel)
                outel.append(tmpel)

        def _append_time(name, value):
            if not value is None and value.time:
                tmpel = value.to_Element()
                _anno_change(tmpel)
                outel.append(tmpel)

        def _append_bool(name, value):
            if not value is None:
                tmpel = ET.Element(name)
                tmpel.text = str(1 if value else 0)
                _anno_change(tmpel)
                outel.append(tmpel)

        if self.parent_object:
            tmpel = self.parent_object.to_Element()
            tmpel.tag = "parent_object"
            outel.append(tmpel)

        _append_str("filename", self.filename)
        _append_str("partition", self.partition)
        _append_str("id", self.id)
        _append_str("name_type", self.name_type)
        _append_str("filesize", self.filesize)
        if self.alloc_name is None and self.alloc_inode is None:
            _append_bool("alloc", self.alloc)
        else:
            _append_bool("alloc_inode", self.alloc_inode)
            _append_bool("alloc_name", self.alloc_name)
        _append_bool("used", self.used)
        _append_bool("orphan", self.orphan)
        _append_bool("compressed", self.compressed)
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
        _append_str("link_target", self.link_target)
        _append_str("libmagic", self.libmagic)

        if self.byte_runs:
            tmpel = self.byte_runs.to_Element()
            _anno_change(tmpel)
            outel.append(tmpel)

        if self.md5:
            tmpel = ET.Element("hashdigest")
            tmpel.attrib["type"] = "md5"
            tmpel.text = self.md5
            _anno_hash(tmpel)
            outel.append(tmpel)

        if self.sha1:
            tmpel = ET.Element("hashdigest")
            tmpel.attrib["type"] = "sha1"
            tmpel.text = self.sha1
            _anno_hash(tmpel)
            outel.append(tmpel)

        if self.original_fileobject:
            tmpel = self.original_fileobject.to_Element()
            tmpel.tag = "delta:original_fileobject"
            outel.append(tmpel)

        return outel

    def to_dfxml(self):
        return ET.tostring(self.to_Element(), encoding="unicode")

    @property
    def alloc(self):
        """Note that setting .alloc will affect the value of .unalloc, and vice versa.  The last one to set wins."""
        global _nagged_alloc
        if not _nagged_alloc:
            _logger.warning("The FileObject.alloc property is deprecated.  Use .alloc_inode and/or .alloc_name instead.  .alloc is proxied as True if alloc_inode and alloc_name are both True.")
            _nagged_alloc = True
        if self.alloc_inode and self.alloc_name:
            return True
        else:
            return self._alloc

    @alloc.setter
    def alloc(self, val):
        self._alloc = _boolcast(val)
        if not self._alloc is None:
            self._unalloc = not self._alloc

    @property
    def alloc_inode(self):
        return self._alloc_inode

    @alloc_inode.setter
    def alloc_inode(self, val):
        self._alloc_inode = _boolcast(val)

    @property
    def alloc_name(self):
        return self._alloc_name

    @alloc_name.setter
    def alloc_name(self, val):
        self._alloc_name = _boolcast(val)

    @property
    def annos(self):
        """Set of differential annotations.  Expected members are the keys of this class's _diff_attr_names dictionary."""
        return self._annos

    @annos.setter
    def annos(self, val):
        _typecheck(val, set)
        self._annos = val

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
        """The security mode is represented in the FileObject as a base-10 integer.  It is also serialized as a decimal integer."""
        #TODO This decimal-octal business is worth a unit test.
        return self._mode

    @mode.setter
    def mode(self, val):
        self._mode = _intcast(val)

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
        if val is None:
            self._name_type = val
        else:
            cast_val = _strcast(val)
            if cast_val not in ["-", "p", "c", "d", "b", "r", "l", "s", "h", "w", "v"]:
                raise ValueError("Unexpected name_type received: %r (casted to %r)." % (val, cast_val))
            self._name_type = cast_val

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
        if not val is None:
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
            _typecheck(val, FileObject)
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
        """Note that setting .unalloc will affect the value of .alloc, and vice versa.  The last one to set wins."""
        return self._unalloc

    @unalloc.setter
    def unalloc(self, val):
        self._unalloc = _boolcast(val)
        if not self._unalloc is None:
            self._alloc = not self._unalloc

    @property
    def unused(self):
        return self._used

    @unused.setter
    def unused(self, val):
        self._unused = _intcast(val)
        if not self._unused is None:
            self._used = not self._unused

    @property
    def used(self):
        return self._used

    @used.setter
    def used(self, val):
        self._used = _intcast(val)
        if not self._used is None:
            self._unused = not self._used

    @property
    def volume_object(self):
        """Reference to the containing volume object.  Not meant to be propagated with __repr__ or to_Element()."""
        return self._volume_object

    @volume_object.setter
    def volume_object(self, val):
        if not val is None:
            _typecheck(val, VolumeObject)
        self._volume_object = val


class CellObject(object):
    _comparable_properties = set([
      "cellpath",
      "name",
      "name_type",
      "alloc",
      "mtime"
    ])

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

    def compare_to_original(self):
        _typecheck(self.original_cellobject, CellObject)

        self._diffs = set()

        for propname in CellObject._comparable_properties:
            oval = getattr(self.original_cellobject, propname)
            nval = getattr(self, propname)
            if oval is None and nval is None:
                continue
            if oval != nval:
                #_logger.debug("propname, oval, nval: %r, %r, %r" % (propname, oval, nval))
                self._diffs.add(propname)

    def populate_from_Element(self, e):
        """Populates this CellObject's properties from an ElementTree Element.  The Element need not be retained."""
        global _warned_elements
        _typecheck(e, (ET.Element, ET.ElementTree))

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
                if (cns, ctn) not in _warned_elements:
                    _warned_elements.add((cns, ctn))
                    _logger.warning("Uncertain what to do with this element: %r" % ce)

        self.sanity_check()

    def sanity_check(self):
        if self.name_type and self.name_type != "k":
            if self.mtime:
                _logger.debug("Error occurred sanity-checking this CellObject: %r" % (self))
                raise ValueError("A Registry Key (node) is the only kind of CellObject that can have a timestamp.")
            if self.root:
                _logger.debug("Error occurred sanity-checking this CellObject: %r" % (self))
                raise ValueError("A Registry Key (node) is the only kind of CellObject that can have the 'root' attribute.")

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
            _typecheck(val, ByteRuns)
        self._byte_runs = val

    @property
    def cellpath(self):
        return self._cellpath

    @cellpath.setter
    def cellpath(self, val):
        if not val is None:
            _typecheck(val, str)
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
            _typecheck(val, str)
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
            _typecheck(val, CellObject)
        self._parent_object = val

    @property
    def original_cellobject(self):
        return self._original_cellobject

    @original_cellobject.setter
    def original_cellobject(self, val):
        if not val is None:
            _typecheck(val, CellObject)
        self._original_cellobject = val

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, val):
        self._root = _boolcast(val)


def iterparse(filename, events=("start","end"), dfxmlobject=None):
    """
    Generator.  Yields a stream of populated DFXMLObjects, VolumeObjects and FileObjects, paired with an event type ("start" or "end").  The DFXMLObject and VolumeObjects do NOT have their child lists populated with this method - that is left to the calling program.

    The event type interface is meant to match the interface of ElementTree's iterparse; this is simply for familiarity's sake.  DFXMLObjects and VolumeObjects are yielded with "start" when the stream of VolumeObject or FileObjects begins - that is, they are yielded after being fully constructed up to the potentially-lengthy child object stream.  FileObjects are yielded only with "end".

    @param filename: A string
    @param events: Events.  Optional.  A tuple of strings, containing "start" and/or "end".
    @param dfxmlobject: A DFXMLObject document.  Optional.  A DFXMLObject is created and yielded in the object stream if this argument is not supplied.
    """

    #The DFXML stream file handle.
    fh = None
    subp = None
    subp_command = ["fiwalk", "-x", filename]
    if filename.endswith("xml"):
        fh = open(filename, "rb")
    else:
        subp = subprocess.Popen(subp_command, stdout=subprocess.PIPE)
        fh = subp.stdout

    _events = set()
    for e in events:
        if not e in ("start","end"):
            raise ValueError("Unexpected event type: %r.  Expecting 'start', 'end'." % e)
        _events.add(e)

    dobj = dfxmlobject or DFXMLObject()

    #The only way to efficiently populated VolumeObjects is to populate the object when the stream has hit its first FileObject.
    vobj = None

    #It doesn't seem ElementTree allows fetching parents of Elements that are incomplete (just hit the "start" event).  So, build a volume Element when we've hit "<volume ... >", glomming all elements until the first fileobject is hit.
    #Likewise with the Element for the DFXMLObject.
    dfxml_proxy = None
    volume_proxy = None

    #State machine, used to track when the first fileobject of a volume is encountered.
    READING_START = 0
    READING_PRESTREAM = 1 #DFXML metadata, pre-Object stream
    READING_VOLUMES = 2
    READING_FILES = 3
    READING_POSTSTREAM = 4 #DFXML metadata, post-Object stream (typically the <rusage> element)
    _state = READING_START

    for (ETevent, elem) in ET.iterparse(fh, events=("start-ns", "start", "end")):
        #View the object event stream in debug mode
        #_logger.debug("(event, elem) = (%r, %r)" % (ETevent, elem))
        #if ETevent in ("start", "end"):
        #    _logger.debug("ET.tostring(elem) = %r" % ET.tostring(elem))

        #Track namespaces
        if ETevent == "start-ns":
            dobj.add_namespace(*elem)
            continue

        #Split tag name into namespace and local name
        (ns, ln) = _qsplit(elem.tag)

        if ETevent == "start":
            if ln == "dfxml":
                if _state != READING_START:
                    raise ValueError("Encountered a <dfxml> element, but the parser isn't in its start state.  Recursive <dfxml> declarations aren't supported at this time.")
                dfxml_proxy = ET.Element(elem.tag)
                for k in elem.attrib:
                    #TODO Check if xmlns declarations cause problems here
                    dfxml_proxy.attrib[k] = elem.attrib[k] 
                _state = READING_PRESTREAM
            elif ln == "volume":
                if _state == READING_PRESTREAM:
                    #Cut; yield DFXMLObject now.
                    dobj.populate_from_Element(dfxml_proxy)
                    if "start" in _events:
                        yield ("start", dobj)
                #Start populating a new Volume proxy.
                volume_proxy = ET.Element(elem.tag)
                for k in elem.attrib:
                    volume_proxy.attrib[k] = elem.attrib[k] 
                _state = READING_VOLUMES
            elif ln == "fileobject":
                if _state == READING_PRESTREAM:
                    #Cut; yield DFXMLObject now.
                    dobj.populate_from_Element(dfxml_proxy)
                    if "start" in _events:
                        yield ("start", dobj)
                elif _state == READING_VOLUMES:
                    _logger.debug("Encountered a fileobject while reading volume properties.  Yielding volume now.")
                    #Cut; yield VolumeObject now.
                    if volume_proxy is not None:
                        vobj = VolumeObject()
                        vobj.populate_from_Element(volume_proxy)
                        if "start" in _events:
                            yield ("start", vobj)
                        #Reset
                        volume_proxy.clear()
                        volume_proxy = None
                _state = READING_FILES
        elif ETevent == "end":
            if ln == "fileobject":
                if _state in (READING_PRESTREAM, READING_POSTSTREAM):
                    #This particular branch can be reached if there are trailing fileobject elements after the volume element.  This would happen if a tool needed to represent files (likely reassembled fragments) found outside all the partitions.
                    #More frequently, we hit this point when there are no volume groupings.
                    vobj = None
                fi = FileObject()
                fi.populate_from_Element(elem)
                fi.volume_object = vobj
                #_logger.debug("fi = %r" % fi)
                if "end" in _events:
                    yield ("end", fi)
                #Reset
                elem.clear()
            elif elem.tag == "dfxml":
                if "end" in _events:
                    yield ("end", dobj)
            elif elem.tag == "volume":
                if "end" in _events:
                    yield ("end", vobj)
                _state = READING_POSTSTREAM
            elif _state == READING_VOLUMES:
                #This is a volume property; glom onto the proxy.
                if volume_proxy is not None:
                    volume_proxy.append(elem)
            elif _state == READING_PRESTREAM:
                if ln in ["metadata", "creator", "source"]:
                    #This is a direct child of the DFXML document property; glom onto the proxy.
                    if dfxml_proxy is not None:
                        dfxml_proxy.append(elem)

    #If we called Fiwalk, double-check that it exited successfully.
    if not subp is None:
        _logger.debug("Calling wait() to let the Fiwalk subprocess terminate...") #Just reading from subp.stdout doesn't let the process terminate; it only finishes working.
        subp.wait()
        if subp.returncode != 0:
            e = subprocess.CalledProcessError("There was an error running Fiwalk.")
            e.returncode = subp.returncode
            e.cmd = subp_command
            raise e

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    
    logging.basicConfig(level=logging.DEBUG)
    #Run unit tests

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
    assert failed

    t0 = TimestampObject(prec="100ns", name="mtime")
    _logger.debug("t0 = %r" % t0)
    assert t0.prec[0] == 100
    assert t0.prec[1] == "ns"
    t1 = TimestampObject("2009-01-23T01:23:45Z", prec="2", name="atime")
    _logger.debug("t1 = %r" % t1)
    assert t1.prec[0] == 2
    assert t1.prec[1] == "s"

    co = CellObject()
    _logger.debug("co = %r" % co)
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
    _logger.debug("br = %r" % br)
    _logger.debug("brs = %r" % brs)
    _logger.debug("co = %r" % co)
    print(co.to_regxml())

    coe = co.to_Element()
    nco = CellObject()
    nco.populate_from_Element(coe)

    assert co.byte_runs == nco.byte_runs

    nco.name = "(Doubled)"
    nco.root = False
    nco.byte_runs[0].file_offset += 133

    _logger.debug("co.byte_runs = %r" % co.byte_runs)
    _logger.debug("nco.byte_runs = %r" % nco.byte_runs)
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

    print("Unit tests passed.")
