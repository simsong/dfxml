#!/bin/bash

set -e

source ../_pick_pythons.sh

"$PYTHON3" ../make_differential_dfxml.py -d ../../samples/difference_test_{0,1}.xml | xmllint --format - > differential_dfxml_test_01.xml

"$PYTHON3" ../summarize_differential_dfxml.py -d differential_dfxml_test_01.xml > differential_dfxml_test_01.txt

"$PYTHON3" ../make_differential_dfxml.py -d ../../samples/difference_test_{2,3}.xml | xmllint --format - > differential_dfxml_test_23.xml

"$PYTHON3" ../summarize_differential_dfxml.py -d differential_dfxml_test_23.xml > differential_dfxml_test_23.txt
