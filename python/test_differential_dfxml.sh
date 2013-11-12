#!/bin/bash

source _pick_pythons.sh

"$PYTHON3" make_differential_dfxml.py ../samples/difference_test_[01].xml > differential_dfxml_test.xml

"$PYTHON3" summarize_differential_dfxml.py -d differential_dfxml_test.xml > differential_dfxml_test.txt
