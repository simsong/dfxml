#/usr/bin/env python3

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
DEVELOPMENT NOTE: This implementation will soon be replaced by what is currently idifference2.py, after a period of testing by users.  If idifference2.py does not meet your needs, but idifference.py does, please let one of the maintainers know (email addresses in the Git history or the python/ChangeLog file).
"""

__version__ = "2.0.0alpha2"

import sys
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import dfxml.objects as Objects
import make_differential_dfxml
import summarize_differential_dfxml

def ignorable_name(fn):
    """Filter out recognized pseudo-file names, accommodating user request for including dotdirs."""
    if fn is None:
        return False
    if args.include_dotdirs and os.path.basename(fn) in [".", ".."]:
        return False
    return make_differential_dfxml.ignorable_name(fn)

if __name__=="__main__":
    import argparse

    parser = argparse.ArgumentParser(description='%prog [options] file1 file2  (files can be xml or image files)')
    returningsoon = parser.add_argument_group("Returning soon", "Some of the options in idifference were not carried forward in the reimplementation.  Please feel free to request these features be re-implemented if you need them.")
    parser.add_argument("-d","--debug",help="Enable debug printing",action='store_true')
    parser.add_argument("-x","--xml",help="Specify output file for DFXML manifest of differences",dest="xmlfilename")
    parser.add_argument("--include-dotdirs",help="Include files with names ending in '/.' and '/..'",action="store_true", default=False)
    parser.add_argument("--sort-by", help="Sorts reported file lists.  Pass one of these arguments: \"times\" or \"paths\".")
    parser.add_argument("--summary",help="output summary statistics of file system changes",action="store_true", default=False)
    parser.add_argument("--timestamp",help="output all times in Unix timestamp format; otherwise use ISO 8601",action="store_true")

    returningsoon.add_argument("-n","--notimeline",help="do not generate a timeline",action="store_true")
    returningsoon.add_argument("-T","--tararchive",help="create tar archive file of new/changed files",dest="tarfile")
    returningsoon.add_argument("-Z","--zipfile",help="create ZIP64 archive file of new/changed files",dest="zipfile")
    returningsoon.add_argument("--html",help="specify output in HTML",action="store_true")
    returningsoon.add_argument("--noatime",help="Do not include atime changes",action="store_true")
    returningsoon.add_argument("--imagefile",help="specifies imagefile or file2 is an XML file and you are archiving")

    parser.add_argument("infiles", nargs="+")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if len(args.infiles) != 2:
        raise NotImplementedError("Sorry, but this version of idifference can only run on two disk images, not a longer sequence.  Please feel free to request longer sequences be re-implemented if you need it.")

    if args.tarfile:
        raise NotImplementedError("Sorry, but the tarring argument was not carried forward in the re-implementation.  Please feel free to request this feature be re-implemented if you need it.")

    if args.zipfile:
        raise NotImplementedError("Sorry, but the zipping argument was not carried forward in the re-implementation.  Please feel free to request this feature be re-implemented if you need it.")
        #TODO The Extractor program should get a Zip-handling function to handle this flag.

    if args.html:
        raise NotImplementedError("Sorry, but the HTML output argument was not carried forward in the re-implementation.  Please feel free to request this feature be re-implemented if you need it.")

    if args.noatime:
        raise NotImplementedError("Sorry, but the ignore-atime argument was not carried forward in the re-implementation.  Please feel free to request this feature be re-implemented if you need it.")

    if args.notimeline:
        raise NotImplementedError("Sorry, but the notimeline argument was not carried forward in the re-implementation.  Please feel free to request this feature be re-implemented if you need it.")

    if args.imagefile:
        raise NotImplementedError("Sorry, but the imagefile argument was not carried forward in the re-implementation.  Please feel free to request this feature be re-implemented if you need it.")

    pre = None
    post = None
    for infile in args.infiles:
        pre = post
        post = infile

        _logger.info(">>> Reading %s." % infile)

        if not pre is None:
            diffdfxml = make_differential_dfxml.make_differential_dfxml(
              pre,
              post,
              diff_mode="idifference",
              ignore_filename_function=ignorable_name
            )
            diffdfxml.program = sys.argv[0]
            diffdfxml.program_version = __version__
            if args.xmlfilename:
                _logger.debug("Opening temp file for writing.")
                with open(args.xmlfilename, "w") as fh:
                    diffdfxml.print_dfxml(output_fh=fh)
            summarize_differential_dfxml.report(
              diffdfxml,
              sort_by=args.sort_by,
              summary=args.summary,
              timestamp=args.timestamp
            )
