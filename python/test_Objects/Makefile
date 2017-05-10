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
  check-py2 \
  check-py3 \
  check-versioned

check: \
  check-py2 \
  check-py3
	./test_cat_partitions.sh
	./test_differential_dfxml.sh

check-py2:
	$(MAKE) PY=$(PYTHON2) check-versioned

check-py3:
	$(MAKE) PY=$(PYTHON3) check-versioned

check-versioned:
	@echo Testing Python: $$PY >&2
	$$PY Objects.py
	$$PY test_diffing_CellObject.py
	$$PY test_diffing_FileObject.py
	$$PY test_diffing_HiveObject.py
	$$PY test_diffing_ByteRuns.py
	$$PY test_diffing_TimestampObject.py
	$$PY test_diffing_VolumeObject.py
	$$PY test_ByteRun.py
	$$PY test_ByteRuns.py
	$$PY test_CellObject.py
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
