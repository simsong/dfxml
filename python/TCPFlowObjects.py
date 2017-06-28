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

__version__ = "0.0.1"

import collections

import Objects

XMLNS_TCPFLOW = Objects.dfxml.XMLNS_DFXML + "#tcpflow"

class TCPFlowFileObject(Objects.FileObject):
    def __init__(self, *args, **kwargs):
        #Not exposed through API.
        self._scanner_result_elements = collections.OrderedDict()

        #Exposed through API.
        self._scanner_results = collections.OrderedDict()

    def populate_from_Element(self, el):
        super().populate_from_Element(el)
        #Run through child elements in external namespaces.
        for ce in self.externals:
            (cns, ctn) = Objects._qsplit(ce.tag)
            if cns != XMLNS_TCPFLOW:
                continue
            if ctn != "scanner_result":
                _logger.warning("Skipping element in TCPFlow XML namespace (processing not implemented): %r." % ce)
                continue
            scanner_name = ce.attrib.get("name")
            scanner_type = ce.attrib.get("type")
            #This clause list could equally well key off the scanner_type.
            if scanner_name == "zip_generic_header_detector":
                result_object = TCPFlowScannerResult_ZipGenericHeaderDetector()
                result_object.populate_from_Element(ce)
            else:
                raise NotImplementedError("No implementation yet written for scanner result: %r." % scanner_name)
            self.scanner_results[(scanner_name, scanner_type)] = result_object

    def to_Element(self):
        el = super.to_Element()
        #TODO Some indexing acrobatics may be necessary to flush any runtime updates to the scanner_results dictionary.

    @property
    def scanner_results(self):
        """
        Ordered Dictionary of scanner results.
          Key: the pair (scanner name, scanner type).
          Value: Subclass of TCPFlowScannerResult.

        No property setter.
        """
        return self._scanner_results

class TCPFlowScannerResult(object):
    """Base class."""

    def __init__(self, *args, **kwargs):
        pass

    def populate_from_Element(self, el):
        (ns, tn) = Objects._qsplit(el.tag)
        if ns != XMLNS_TCPFLOW:
            continue
        #All other work left to subclasses.

class TCPFlowScannerResult_ZipGenericHeaderDetector(TCPFlowScannerResult):
    """Example."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.byte_runs = Objects.ByteRuns()

    def populate_from_Element(self, el):
        super().populate_from_Element(el)
        for ce in el.findall("./*"):
            (cns, ctn) = Objects._qsplit(ce.tag)
            if ctn == "byte_runs":
                self.byte_runs.populate_from_Element(ce)
            else:
                #TODO Process anything else reported in the scanner_result element.
                raise NotImplementedError("Unexpected element: %r." % ce)
