PYTHON3 = python3.3

all: check

check:
	$(PYTHON3) Objects.py
	$(PYTHON3) test_FileObject_diffing.py
	$(PYTHON3) test_FileObject_from_stat.py
	$(PYTHON3) test_VolumeObject_diffing.py
	$(PYTHON3) test_VolumeObject_hash.py
	$(PYTHON3) verify_differential_dfxml.py
