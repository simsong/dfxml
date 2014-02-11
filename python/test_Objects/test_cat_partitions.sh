#!/bin/bash

. ../_pick_pythons.sh

"$PYTHON3" ../cat_partitions.py \
  12345678:../../samples/difference_test_0.xml \
  87654321:../../samples/difference_test_1.xml \
  | xmllint --format - >$0.dfxml
