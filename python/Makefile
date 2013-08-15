check: \
  check-dfxml \
  check-cat_fileobjects \
  check-dfxml_tool \
  check-idifference-dfxml \
  check-mac_timelines
	@echo "Tests passed!"

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
	
clean:
	rm -f dfxml_tool_*xml
	rm -f cat_test_{,no}cache.dfxml
	rm -f idifference_test{,_formatted}.dfxml
