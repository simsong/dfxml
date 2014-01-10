#!/usr/bin/env python3

__version__ = "0.2.0"

import Objects
import os
import sys
import logging
import hashlib

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(os.path.basename(__file__))

def is_alloc_and_uncompressed(obj):
    if obj.compressed:
        return False
    if not obj.alloc_inode is None and not obj.alloc_name is None:
        return obj.alloc_inode and obj.alloc_name
    return obj.alloc

def is_file(obj):
    if is_alloc_and_uncompressed(obj) != True:
        return False
    if obj.filename is None:
        return None
    return obj.name_type == "r"
    
def is_jpeg(obj):
    if is_alloc_and_uncompressed(obj) != True:
        return False
    if obj.filename is None:
        return None
    if is_file(obj) != True:
        return False
    return obj.filename.lower().endswith(("jpg","jpeg"))

def main():
    dfxml_path = sys.argv[1]
    image_path = sys.argv[2]
    outdir = "extraction"
    dry_run = False

    extraction_byte_tally = 0

    with open(dfxml_path, "r") as dfxml_fh:
        for (event, obj) in Objects.iterparse(dfxml_path):
            #Absolute prerequisites:
            if not isinstance(obj, Objects.FileObject):
                continue

            #Invoker prerequisites
            if not is_file(obj):
                continue

            #Construct path where the file will be extracted
            extraction_write_path = outdir
            if obj.partition is None:
                extraction_write_path = os.path.join(extraction_write_path, "no_partition")
            else:
                extraction_write_path = os.path.join(extraction_write_path, "partition_" + str(obj.partition))
            extraction_write_path = os.path.join(extraction_write_path, obj.filename)

            #Extract idempotently
            if os.path.exists(extraction_write_path):
                _logger.debug("Skipping already-extracted file: %r." % obj.filename)
                continue

            #Set up checksum verifier
            checker = None
            checked_byte_tally = 0
            if obj.sha1:
                checker = hashlib.sha1()

            extraction_byte_tally += obj.filesize

            if not dry_run:
                extraction_write_dir = os.path.dirname(extraction_write_path)
                if not os.path.exists(extraction_write_dir):
                    os.makedirs(extraction_write_dir)
                _logger.debug("Extracting to: %r." % extraction_write_path)
                with open(extraction_write_path, "wb") as extraction_write_fh:
                    for chunk in obj.extract_facet("content", image_path):
                        if checker:
                            checker.update(chunk)
                        checked_byte_tally += len(chunk)
                        extraction_write_fh.write(chunk)
                    
                    if checked_byte_tally != obj.filesize:
                        _logger.error("File size mismatch on %r." % obj.filename)
                        _logger.info("Recorded filesize = %r" % obj.filesize)
                        _logger.info("Extracted bytes   = %r" % checked_byte_tally)
                    if checker and (obj.sha1 != checker.hexdigest()):
                        _logger.error("Hash mismatch on %r." % obj.filename)
                        _logger.info("Recorded SHA-1 = %r" % obj.sha1)
                        _logger.info("Computed SHA-1 = %r" % checker.hexdigest())
                        _logger.debug("File object: %r." % obj)

    #Report
    _logger.info("Estimated extraction: %d bytes." % extraction_byte_tally)

if __name__ == "__main__":
    main()
