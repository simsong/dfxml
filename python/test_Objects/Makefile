
SHELL = /bin/bash

PYTHON2 = python2.7
PYTHON3 = python3.3

all: check

check:
	for PY in "$(PYTHON3)" "$(PYTHON2)"; do \
	  echo Testing Python: $$PY >&2; \
	  $$PY Objects.py && \
	  $$PY test_diffing_CellObject.py && \
	  $$PY test_diffing_FileObject.py && \
	  $$PY test_diffing_HiveObject.py && \
	  $$PY test_diffing_ByteRuns.py && \
	  $$PY test_diffing_TimestampObject.py && \
	  $$PY test_diffing_VolumeObject.py && \
	  $$PY test_FileObject_from_stat.py && \
	  $$PY test_RegXMLObject.py && \
	  $$PY test_VolumeObject_hash.py && \
	  $$PY verify_differential_dfxml_01.py && \
	  $$PY verify_differential_dfxml_23.py ; \
	done

clean:
	rm verify_differential_dfxml_{01,23}.py-test[12].xml

