
SHELL = /bin/bash

PYTHON2 = python2.7
PYTHON3 = python3

all: check

check:
	set -e; \
	for PY in "$(PYTHON3)" "$(PYTHON2)"; do \
	  echo Testing Python: $$PY >&2; \
	  $$PY Objects.py && \
	  $$PY test_diffing_CellObject.py && \
	  $$PY test_diffing_FileObject.py && \
	  $$PY test_diffing_HiveObject.py && \
	  $$PY test_diffing_ByteRuns.py && \
	  $$PY test_diffing_TimestampObject.py && \
	  $$PY test_diffing_VolumeObject.py && \
	  $$PY test_ByteRun.py && \
	  $$PY test_ByteRuns.py && \
	  $$PY test_CellObject.py && \
	  $$PY test_FileObject_byte_run_facets.py && \
	  $$PY test_FileObject_from_stat.py && \
	  $$PY test_RegXMLObject.py && \
	  $$PY test_VolumeObject_hash.py && \
	  $$PY verify_differential_dfxml_01.py && \
	  $$PY verify_differential_dfxml_23.py ; \
	done
	./test_cat_partitions.sh
	./test_differential_dfxml.sh

clean:
	rm -f differential_dfxml_test_[02]*
	rm -f verify_differential_dfxml_{01,23}.py-test[12].xml
	rm -f test_difference_counts.py-d*
	rm -f test_cat_partitions.sh.dfxml
