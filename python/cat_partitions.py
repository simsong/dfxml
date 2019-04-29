#!/usr/bin/env python3

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

"""
Writes to stdout a DFXML document that is the concatenation of each input DFXML document.

Assumes the input DFXML has at most one volume per document.

Partition numbers, offsets, and byte run img_offset attributes are all overwritten with the correct value assuming the partition was carved at the offset passed on the command line.

That is, this command:

    $0 32256:fiout.xml 1073741824:fiout.xml

will create a single DFXML file with two volumes and their file objects contained.
"""

__version__ = "0.2.2"

import dfxml.objects as Objects
import logging
import os
import sys
import xml.etree.ElementTree as ET

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    d = Objects.DFXMLObject(version="1.2.0")

    d.program = sys.argv[0]
    d.program_version = __version__
    d.command_line = " ".join(sys.argv)
    d.dc["type"] = "File system walk concatenation"
    d.add_creator_library("Python", ".".join(map(str, sys.version_info[0:3]))) #A bit of a bend, but gets the major version information out.
    d.add_creator_library("Objects.py", Objects.__version__)
    d.add_creator_library("dfxml.py", Objects.dfxml.__version__)

    _offsets_and_pxml_paths = []
    for (lxfno, lxf) in enumerate(args.labeled_xml_file):
        lxf_parts = lxf.split(":")
        if len(lxf_parts) != 2 or not lxf_parts[0].isdigit():
            raise ValueError("Malformed argument in labeled_xml_file.  Expecting space-delimited list of '<number>:<path>'.  This entry doesn't work: %r." % lxf)
        offset = int(lxf_parts[0])
        path = lxf_parts[1]
        _offsets_and_pxml_paths.append((offset,path))
    offsets_and_pxml_paths = sorted(_offsets_and_pxml_paths)

    for (pxml_path_index, (offset, pxml_path)) in enumerate(offsets_and_pxml_paths):
        _logger.debug("Running on path %r." % pxml_path)
        pdo = Objects.parse(pxml_path)

        building_volume = None
        #Fetch or build volume we'll append
        if len(pdo.volumes) > 1:
            raise ValueError("An input DFXML document has multiple volumes; this script assumes each input document only has one.  The document here has %d: %r." % (len(pdo.volumes), pxml_path))
        elif len(pdo.volumes) == 0:
            v = Objects.VolumeObject()
            building_volume = True
        else:
            v = pdo.volumes[0]
            building_volume = False

        v.partition_offset = offset

        #Accumulate namespaces
        for (prefix, url) in pdo.iter_namespaces():
            d.add_namespace(prefix, url)

        for obj in pdo:
            #Force-update image offsets in byte runs
            for brs_prop in ["data_brs", "name_brs", "inode_brs"]:
                if hasattr(obj, brs_prop):
                    brs = getattr(obj, brs_prop)
                    if brs is None:
                        continue
                    for br in brs:
                        if not br.fs_offset is None:
                            br.img_offset = br.fs_offset + offset
            #For files, set partition identifier and attach to partition
            if isinstance(obj, Objects.FileObject):
                obj.partition = pxml_path_index + 1
                if building_volume:
                    v.append(obj)

        #Collect the constructed and/or updated volume
        d.append(v)

    d.print_dfxml()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="Enable debug printing", action="store_true")
    parser.add_argument("--image-path", help="Path to the source image file to record in the resulting DFXML.")
    parser.add_argument("labeled_xml_file", help="List of DFXML files, each colon-prefixed with the partition's offset in bytes (e.g. '32256:fiout.dfxml')", nargs="+")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    main()
