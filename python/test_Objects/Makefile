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

PYTHON2 = python2.7
PYTHON3 = $(shell source ../_pick_pythons.sh ; echo $$PYTHON3)

all: \
  check

.PHONY: \
  check-diff_file_ignore-py2 \
  check-diff_file_ignore-py3 \
  check-py2 \
  check-py3 \
  check-versioned

check: \
  check-py2 \
  check-py3
	./test_cat_partitions.sh
	./test_differential_dfxml.sh

check-diff_file_ignore-py2: \
  diff_file_ignore_sample-py2.dfxml \
  test_diff_file_ignore.py
	$(PYTHON2) test_diff_file_ignore.py --debug diff_file_ignore_sample-py2.dfxml

check-diff_file_ignore-py3: \
  diff_file_ignore_sample-py3.dfxml \
  test_diff_file_ignore.py
	$(PYTHON3) test_diff_file_ignore.py --debug diff_file_ignore_sample-py3.dfxml

check-libraries-py2:
	$(PYTHON2) test_LibraryObject_write.py test_LibraryObject_py2.dfxml
	$(PYTHON2) test_LibraryObject_read.py test_LibraryObject_py2.dfxml

check-libraries-py3:
	$(PYTHON3) test_LibraryObject_write.py test_LibraryObject_py3.dfxml
	$(PYTHON3) test_LibraryObject_read.py test_LibraryObject_py3.dfxml

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

check-versioned:
	@echo Testing Python: $$PY >&2
	$$PY Objects.py
	$$PY test_diffing_CellObject.py
	$$PY test_diffing_FileObject.py
	$$PY test_diffing_HiveObject.py
	$$PY test_diffing_ByteRuns.py
	$$PY test_diffing_TimestampObject.py
	$$PY test_diffing_VolumeObject.py
	$$PY test_storage_layers.py
	$$PY test_ByteRun.py
	$$PY test_ByteRuns.py
	$$PY test_CellObject.py
	$$PY test_DFXMLObject_program.py ../../samples/difference_test_0.xml vi 8.0
	$$PY test_FileObject_allocation.py
	$$PY test_FileObject_byte_run_facets.py
	$$PY test_FileObject_externals.py
	$$PY test_FileObject_from_stat.py
	$$PY test_RegXMLObject.py
	$$PY test_VolumeObject_externals.py
	$$PY test_VolumeObject_hash.py
	$$PY verify_differential_dfxml_01.py
	$$PY verify_differential_dfxml_23.py

clean:
	rm -f differential_dfxml_test_[02]*
	rm -f verify_differential_dfxml_{01,23}.py-test[12].xml
	rm -f test_difference_counts.py-d*
	rm -f test_cat_partitions.sh.dfxml
	rm -f diff_file_ignore_sample-py[23].dfxml
	rm -f test_LibraryObject_py[23].dfxml

diff_file_ignore_sample-py2.dfxml: \
  Objects.py \
  diff_file_ignore_sample_dfxml.py
	rm -f _$@
	$(PYTHON2) diff_file_ignore_sample_dfxml.py --debug _$@
	mv _$@ $@

diff_file_ignore_sample-py3.dfxml: \
  Objects.py \
  diff_file_ignore_sample_dfxml.py
	rm -f _$@
	$(PYTHON3) diff_file_ignore_sample_dfxml.py --debug _$@
	mv _$@ $@
