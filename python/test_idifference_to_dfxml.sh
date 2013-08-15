#!/bin/bash

. _pick_pythons.sh

XMLLINT=`which xmllint`

#Halt on error
set -e
#Display all executed commands
set -x

"$PYTHON3" idifference.py --xml idifference_test.dfxml ../samples/difference_test_[01].xml
if [ -x "$XMLLINT" ]; then
  xmllint --format idifference_test.dfxml >idifference_test_formatted.dfxml
else
  echo "Warning: xmllint not found.  Skipped check for if generated DFXML is valid XML." >&2
fi
