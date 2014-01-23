PYTHON2 = python2.7
PYTHON3 = python3.3

all: check

check:
	@echo Testing Python 3: $(PYTHON2)
	$(PYTHON3) Objects.py
	$(PYTHON3) test_diffing_FileObject.py
	$(PYTHON3) test_diffing_ByteRuns.py
	$(PYTHON3) test_diffing_VolumeObject.py
	$(PYTHON3) test_FileObject_from_stat.py
	$(PYTHON3) test_VolumeObject_hash.py
	$(PYTHON3) verify_differential_dfxml.py
#	@echo Testing Python 2: $(PYTHON2)
#	$(PYTHON2) Objects.py
#	$(PYTHON2) test_diffing_FileObject.py
#	$(PYTHON2) test_diffing_ByteRuns.py

clean:
	rm verify_differential_dfxml.py-test[12].xml
