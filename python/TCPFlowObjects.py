#!/usr/bin/env python

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

"""
This file is for design/implementation discussion.

Design assumption: TCPFlow scanner results are stored as direct child elements of DFXML <fileobject>, namespaced under DFXML namespace, + #tcpflow.  Structure:

    <tcpflow:scanner_result name="foo" type="bar">baz</tcpflow:scanner_result>

E.g.:

    <tcpflow:scanner_result name="zip_generic_header_detector" type="Python">
      <byte_runs>
        <byte_run img_offset="1234" len="30" />
      </byte_runs>
    </tcpflow:scanner_result>
"""

__version__ = "0.0.3"

import collections

import dfxml.objects as Objects

XMLNS_TCPFLOW = Objects.dfxml.XMLNS_DFXML + "#tcpflow"

class TCPFlowScannerResult(object):
    """Base class."""

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name")
        self.type = kwargs.get("type")
        self.flow_name = kwargs.get("flow_name")

    def populate_from_Element(self, el):
        (ns, tn) = Objects._qsplit(el.tag)
        if ns != XMLNS_TCPFLOW or tn != "scanner_result":
            raise ValueError("TCPFlowScannerResult needs to be instantiated from a {%s}scanner_result element." % XMLNS_TCPFLOW)
        #All other work left to subclasses.

    def print_report(self):
        raise NotImplementedError("Should be implemented in subclass.")

class TCPFlowScannerResult_ZipGenericHeaderDetector(TCPFlowScannerResult):
    """Example."""

    def __init__(self, *args, **kwargs):
        super(TCPFlowScannerResult_ZipGenericHeaderDetector, self).__init__(*args, **kwargs)
        self.byte_runs = Objects.ByteRuns()

    def populate_from_Element(self, el):
        super(TCPFlowScannerResult_ZipGenericHeaderDetector, self).populate_from_Element(el)
        for ce in el.findall("./*"):
            (cns, ctn) = Objects._qsplit(ce.tag)
            if ctn == "byte_runs":
                self.byte_runs.populate_from_Element(ce)
            else:
                #TODO Process anything else reported in the scanner_result element.
                raise NotImplementedError("Unexpected element: %r." % ce)

    def print_report(self):
        #print("Flow name: %r." % self.flow_name)
        print("Zip headers detected.  Locations:")
        for br in self.byte_runs:
            print("  * %d, %d" % (br.img_offset, br.len))

def scanner_results_from_FileObject(fobj):
    """
    Returns a list of scanner results, each an object, a subclass of TCPFlowScannerResult.
    """
    scanner_results = []

    #Run through child elements in external namespaces.
    for ce in fobj.externals:
        (cns, ctn) = Objects._qsplit(ce.tag)
        if cns != XMLNS_TCPFLOW:
            continue
        if ctn != "scanner_result":
            _logger.warning("Skipping element in TCPFlow XML namespace (processing not implemented): %r." % ce)
            continue

        result_kwargs = dict()
        result_kwargs["name"] = ce.attrib.get("name")
        result_kwargs["type"] = ce.attrib.get("type")
        result_kwargs["flow_name"] = fobj.filename

        #This clause list could equally well key off the scanner_type.
        if result_kwargs["name"] == "zip_generic_header_detector":
            result_object = TCPFlowScannerResult_ZipGenericHeaderDetector(**result_kwargs)
            result_object.populate_from_Element(ce)
        else:
            raise NotImplementedError("No implementation yet written for scanner result: %r." % result_kwargs["name"])
        scanner_results.append(result_object)

    return scanner_results
