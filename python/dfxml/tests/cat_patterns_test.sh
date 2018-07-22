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

source ../../tests/_pick_pythons.sh

"$PYTHON3" ../cat_partitions.py \
  12345678:../../../samples/difference_test_0.xml \
  87654321:../../../samples/difference_test_1.xml \
  | xmllint --format - >$0.dfxml
