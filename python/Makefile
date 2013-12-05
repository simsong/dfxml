check: \
  check-dfxml \
  check-cat_fileobjects \
  check-dfxml_tool \
  check-differential_dfxml \
  check-idifference-dfxml \
  check-mac_timelines \
  check-Objects
	@echo "Tests passed!"

check-dfxml:
	./test_dfxml.sh

check-cat_fileobjects:
	./test_cat_fileobjects.sh

check-differential_dfxml:
	./test_differential_dfxml.sh

check-dfxml_tool:
	./test_dfxml_tool.sh

check-idifference-dfxml:
	./test_idifference_to_dfxml.sh

check-mac_timelines:
	./test_mac_timelines.sh
	
check-Objects:
	$(MAKE) -C test_Objects

clean:
	rm -f dfxml_tool_*xml
	rm -f cat_test_*.dfxml
	rm -f idifference_test.txt
	rm -f idifference_test*.dfxml
	rm -f demo_mac_timeline*.txt
	rm -f differential_dfxml_test_[02].*
