#!/opt/local/bin/python3.3

"""This program reads a disk image and verifies the SHA1's of every regular file, using only the byte runs."""

__version__ = "0.1.3"

import os
import logging
import hashlib
import argparse
import Objects

parser = argparse.ArgumentParser()
parser.add_argument("image_file")
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(os.path.basename(__file__))

for (event, f) in Objects.iterparse(args.image_file):
    if not isinstance(f, Objects.FileObject):
        continue

    if f.name_type != "r":
        continue

    if f.compressed:
        raise NotImplementedError("The Python bindings don't support working with compressed files at this time.")

    if not f.byte_runs is None:
        s = hashlib.sha1()

        bytes_tally = 0

        try:
            for block in f.byte_runs.iter_contents(args.image_file):
                bytes_tally += len(block)
                s.update(block)
            if f.sha1 != s.hexdigest():
                _logger.debug("Hash mismatch on %r." % f.filename)
                _logger.debug("f.filesize = %r" % f.filesize)
                _logger.debug("bytes_tally = %r" % bytes_tally)
                _logger.debug("f.sha1 = %r" % f.sha1)
                _logger.debug("mysha1 = %r" % s.hexdigest())
                _logger.debug("f.byte_runs = %r" % f.byte_runs)
        except:
            _logger.info("Error reading contents of %r." % f.filename)
            _logger.debug("f.byte_runs = %r" % f.byte_runs)
            raise
