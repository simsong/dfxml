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

all: \
  check

.PHONY: \
  check-dfxml \
  check-cat_fileobjects \
  check-dfxml_tool \
  check-idifference-dfxml \
  check-mac_timelines \
  check-Objects \
  clean-Objects

check: \
  check-dfxml \
  check-cat_fileobjects \
  check-dfxml_tool \
  check-idifference-dfxml \
  check-mac_timelines \
  check-Objects
	@echo ""
	@echo "Tests passed!"
	@echo "Clean up the test results with 'make clean'."

doc: \
  Objects.html

Objects.html: \
  Objects.py
	python3 -m pydoc -w Objects

check-dfxml:
	./test_dfxml.sh

check-cat_fileobjects:
	./test_cat_fileobjects.sh

check-dfxml_tool:
	./test_dfxml_tool.sh

check-idifference-dfxml:
	./test_idifference_to_dfxml.sh

check-mac_timelines:
	./test_mac_timelines.sh

check-Objects:
	$(MAKE) -C test_Objects

clean: clean-Objects
	rm -f dfxml_tool_*xml
	rm -f cat_test_*.dfxml
	rm -f idifference_test.txt
	rm -f idifference_test*.dfxml
	rm -f demo_mac_timeline*.txt

clean-Objects:
	$(MAKE) -C test_Objects clean
