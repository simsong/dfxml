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

Objects.html: Objects.py
	python3.3 -m pydoc -w Objects

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
