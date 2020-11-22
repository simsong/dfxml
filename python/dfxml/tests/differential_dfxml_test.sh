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

set -e

"$PYTHON3" $TOOLS_DIR/make_differential_dfxml.py -d $SAMPLES_DIR/difference_test_{0,1}.xml | xmllint --format - > differential_dfxml_test_01.xml

"$PYTHON3" $TOOLS_DIR/summarize_differential_dfxml.py -d differential_dfxml_test_01.xml > differential_dfxml_test_01.txt

"$PYTHON3" $TOOLS_DIR/make_differential_dfxml.py -d $SAMPLES_DIR/difference_test_{2,3}.xml | xmllint --format - > differential_dfxml_test_23.xml

"$PYTHON3" $TOOLS_DIR/summarize_differential_dfxml.py -d differential_dfxml_test_23.xml > differential_dfxml_test_23.txt
