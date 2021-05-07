#!/bin/bash

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

source paths.sh

#Halt on error
set -e
#Display all executed commands
set -x

"$PYTHON2" $DEMO_DIR/demo_mac_timeline.py ../samples/simple.xml >demo_mac_timeline_simple_p2.txt
test 12 == $(cat demo_mac_timeline_simple_p2.txt | wc -l)

"$PYTHON3" $DEMO_DIR/demo_mac_timeline.py ../samples/simple.xml >demo_mac_timeline_simple_p3.txt
test 12 == $(cat demo_mac_timeline_simple_p3.txt | wc -l)

"$PYTHON2" $DEMO_DIR/demo_mac_timeline_iter.py ../samples/simple.xml >demo_mac_timeline_iter_simple_p2.txt
test 12 == $(cat demo_mac_timeline_iter_simple_p2.txt | wc -l)

"$PYTHON3" $DEMO_DIR/demo_mac_timeline_iter.py ../samples/simple.xml >demo_mac_timeline_iter_simple_p3.txt
test 12 == $(cat demo_mac_timeline_iter_simple_p3.txt | wc -l)

"$PYTHON2" $DEMO_DIR/demo_mac_timeline_objects.py ../samples/simple.xml >demo_mac_timeline_objects_simple_p2.txt
test 12 == $(cat demo_mac_timeline_iter_simple_p2.txt | wc -l)

"$PYTHON3" $DEMO_DIR/demo_mac_timeline_objects.py ../samples/simple.xml >demo_mac_timeline_objects_simple_p3.txt
test 12 == $(cat demo_mac_timeline_iter_simple_p3.txt | wc -l)

"$PYTHON3" $DEMO_DIR/demo_mac_timeline.py ../samples/difference_test_1.xml >demo_mac_timeline_dt1.txt
test 9 == $(cat demo_mac_timeline_dt1.txt | wc -l)

"$PYTHON3" $DEMO_DIR/demo_mac_timeline_iter.py ../samples/difference_test_1.xml >demo_mac_timeline_iter_dt1.txt
test 9 == $(cat demo_mac_timeline_iter_dt1.txt | wc -l)

"$PYTHON3" $DEMO_DIR/demo_mac_timeline_objects.py ../samples/difference_test_1.xml >demo_mac_timeline_objects_dt1.txt
test 9 == $(cat demo_mac_timeline_objects_dt1.txt | wc -l)
