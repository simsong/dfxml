#!/usr/bin/make -f

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

SHELL = /bin/bash
PICK_PYTHONS = ../../tests/_pick_pythons.sh
SAMPLES_DIR=../../../samples

PYTHON2 = python2.7
PYTHON3 = $(shell source $(PICK_PYTHONS) ; echo $$PYTHON3)

OBJECTS=../objects.py

all: \
  check

.PHONY: \
  check-diff_file_ignore-py2 \
  check-diff_file_ignore-py3 \
  check-py2 \
  check-py3 \
  check-tcpflow \
  check-versioned

check: \
  check-py3 \
  check-tcpflow \
	./cat_partitions_test.sh \
	./differential_dfxml_test.sh

check-diff_file_ignore-py2: \
  diff_file_ignore_sample-py2.dfxml \
  diff_file_ignore_test.py
	$(PYTHON2) diff_file_ignore_test.py --debug diff_file_ignore_sample-py2.dfxml

check-diff_file_ignore-py3: \
  diff_file_ignore_sample-py3.dfxml \
  diff_file_ignore_test.py
	$(PYTHON3) diff_file_ignore_test.py --debug diff_file_ignore_sample-py3.dfxml

check-libraries-py2:
	$(PYTHON2) LibraryObject_write_test.py LibraryObject_py2_test.dfxml
	$(PYTHON2) LibraryObject_read_test.py LibraryObject_py2_test.dfxml

check-libraries-py3:
	$(PYTHON3) LibraryObject_write_test.py LibraryObject_py3_test.dfxml
	$(PYTHON3) LibraryObject_read_test.py LibraryObject_py3_test.dfxml

check-py2:
	$(MAKE) \
	  PY=$(PYTHON2) \
	  check-diff_file_ignore-py2 \
	  check-libraries-py2 \
	  check-versioned

check-py3:
	$(MAKE) \
	  PY=$(PYTHON3) \
	  check-diff_file_ignore-py3 \
	  check-libraries-py3 \
	  check-versioned

check-tcpflow: \
  ../../samples/tcpflow_zip_generic_header.xml \
  ../TCPFlowObjects.py \
  test_TCPFlowObjects.py
	$(PYTHON2) test_TCPFlowObjects.py ../../samples/tcpflow_zip_generic_header.xml
	$(PYTHON3) test_TCPFlowObjects.py ../../samples/tcpflow_zip_generic_header.xml

check-versioned:
	@echo Testing Python: $$PY >&2
	$$PY $(OBJECTS)
	$$PY DFXMLObject_program_test.py $(SAMPLES_DIR)/difference_test_0.xml vi 8.0
	$$PY verify_differential_dfxml_01_test.py
	$$PY verify_differential_dfxml_23_test.py
	./walk_ignore_test.sh $$PY

clean:
	rm -f differential_dfxml_test_??.{xml,txt}
	rm -f verify_differential_dfxml_{01,23}_test.py-test[12].xml
	rm -f difference_counts_test.py-d*
	rm -f cat_partitions_test.sh.dfxml
	rm -f diff_file_ignore_sample-py[23].dfxml
	rm -f LibraryObject_py[23]_test.dfxml
	rm -rf walk_ignore_test/ walk_ignore_*_test.dfxml
	rm -f *~


diff_file_ignore_sample-py2.dfxml: \
  $(OBJECTS) \
  diff_file_ignore_sample_dfxml_test.py
	rm -f _$@
	$(PYTHON2) diff_file_ignore_sample_dfxml_test.py --debug _$@
	mv _$@ $@

diff_file_ignore_sample-py3.dfxml: \
  $(OBJECTS) \
  diff_file_ignore_sample_dfxml_test.py
	rm -f _$@
	$(PYTHON3) diff_file_ignore_sample_dfxml_test.py --debug _$@
	mv _$@ $@
