#/usr/bin/env python3

__version__ = "2.0.0alpha"

import Objects
import make_differential_dfxml
import summarize_differential_dfxml

import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

def ignorable_name(fn):
    """Filter out recognized pseudo-file names, accomodating user request for including dotdirs."""
    if fn is None:
        return False
    if args.include_dotdirs and os.path.basename(fn) in [".", ".."]:
        return False
    return make_differential_dfxml.ignorable_name(fn)

if __name__=="__main__":
    import argparse

    parser = argparse.ArgumentParser(description='%prog [options] file1 file2 [file3...]  (files can be xml or image files)')
    parser.add_argument("-x","--xml",help="specify output file for XML",dest="xmlfilename")
    parser.add_argument("--html",help="specify output in HTML",action="store_true")
    parser.add_argument("-n","--notimeline",help="do not generate a timeline",action="store_true")
    parser.add_argument("-d","--debug",help="debug",action='store_true')
    parser.add_argument("-T","--tararchive",help="create tar archive file of new/changed files",dest="tarfile")
    parser.add_argument("-Z","--zipfile",help="create ZIP64 archive file of new/changed files",dest="zipfile")
    parser.add_argument("--include-dotdirs",help="include files with names ending in '/.' and '/..'",action="store_true", dest="include_dotdirs", default=False)
    parser.add_argument("--summary",help="output summary statistics of file system changes",action="store_true", default=False)
    parser.add_argument("--timestamp",help="output all times in Unix timestamp format; otherwise use ISO 8601",action="store_true")
    parser.add_argument("--imagefile",help="specifies imagefile or file2 is an XML file and you are archiving")
    parser.add_argument("--noatime",help="Do not include atime changes",action="store_true")
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

    if args.summary:
        raise NotImplementedError("Sorry, but the tabular-summary argument was not carried forward in the re-implementation.  Please feel free to request this feature be re-implemented if you need it.")

    if args.timestamp:
        raise NotImplementedError("Sorry, but the tabular-summary argument was not carried forward in the re-implementation.  Please feel free to request this feature be re-implemented if you need it.")
#TODO Interpret these old flags
#    parser.add_argument("-n","--notimeline",help="do not generate a timeline",action="store_true")
#    parser.add_argument("--imagefile",help="specifies imagefile or file2 is an XML file and you are archiving")
#    parser.add_argument("--noatime",help="Do not include atime changes",action="store_true")

    if args.xmlfilename is None:
        #TODO Expose a report() function in summarize_differential_dfxml.
        raise ValueError("This version of idifference currently requires writing an intermediary XML file to disk.  Please supply -x.")

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
            if args.xmlfilename:
                _logger.debug("Opening temp file for writing.")
                with open(args.xmlfilename, "w") as fh:
                    fh.write(diffdfxml.to_dfxml())
                #TODO Expose a report() function in summarize_differential_dfxml, that can take a DFXML file path, or the diffdfxml object.
                #TODO Because these next three lines are a hack.
                _logger.debug("Temp file written.")
                args.infile = args.xmlfilename
                summarize_differential_dfxml.args = args
                summarize_differential_dfxml.main()
                _logger.debug("Summarizer's main function called.")
