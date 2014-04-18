#!/bin/bash

. _pick_pythons.sh

#Halt on error
set -e
#Display all executed commands
set -x

"$PYTHON2" demo_mac_timeline.py ../samples/simple.xml >demo_mac_timeline_simple_p2.txt
test 12 == $(cat demo_mac_timeline_simple_p2.txt | wc -l)

"$PYTHON3" demo_mac_timeline.py ../samples/simple.xml >demo_mac_timeline_simple_p3.txt
test 12 == $(cat demo_mac_timeline_simple_p3.txt | wc -l)

"$PYTHON2" demo_mac_timeline_iter.py ../samples/simple.xml >demo_mac_timeline_iter_simple_p2.txt
test 12 == $(cat demo_mac_timeline_iter_simple_p2.txt | wc -l)

"$PYTHON3" demo_mac_timeline_iter.py ../samples/simple.xml >demo_mac_timeline_iter_simple_p3.txt
test 12 == $(cat demo_mac_timeline_iter_simple_p3.txt | wc -l)

"$PYTHON2" demo_mac_timeline_objects.py ../samples/simple.xml >demo_mac_timeline_objects_simple_p2.txt
test 12 == $(cat demo_mac_timeline_iter_simple_p2.txt | wc -l)

"$PYTHON3" demo_mac_timeline_objects.py ../samples/simple.xml >demo_mac_timeline_objects_simple_p3.txt
test 12 == $(cat demo_mac_timeline_iter_simple_p3.txt | wc -l)

"$PYTHON3" demo_mac_timeline.py ../samples/difference_test_1.xml >demo_mac_timeline_dt1.txt
test 9 == $(cat demo_mac_timeline_dt1.txt | wc -l)

"$PYTHON3" demo_mac_timeline_iter.py ../samples/difference_test_1.xml >demo_mac_timeline_iter_dt1.txt
test 9 == $(cat demo_mac_timeline_iter_dt1.txt | wc -l)

"$PYTHON3" demo_mac_timeline_objects.py ../samples/difference_test_1.xml >demo_mac_timeline_objects_dt1.txt
test 9 == $(cat demo_mac_timeline_objects_dt1.txt | wc -l)
