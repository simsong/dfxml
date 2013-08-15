#!/bin/bash

. _pick_pythons.sh

XMLLINT=`which xmllint`

#Halt on error
set -e
#Display all executed commands
set -x

#NOTE: Python2's ETree does not understand the "unicode" output encoding.
#"$PYTHON2" cat_fileobjects.py ../samples/simple.xml
"$PYTHON3" cat_fileobjects.py ../samples/simple.xml >cat_test_nocache.dfxml
"$PYTHON3" cat_fileobjects.py --cache ../samples/simple.xml >cat_test_cache.dfxml

#This checks that the XML structure wasn't changed by cache cleaning.  Only the tail is hashed because the head contains metadata.
test "x$(tail -n 10 cat_test_nocache.dfxml | openssl dgst -sha1 -)" == "x$(tail -n 10 cat_test_cache.dfxml | openssl dgst -sha1 -)"

if [ -x "$XMLLINT" ]; then
  "$PYTHON3" cat_fileobjects.py ../samples/simple.xml | "$XMLLINT" -
else
  echo "Warning: xmllint not found.  Skipped check for if generated DFXML is valid XML." >&2
fi
