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

. _pick_pythons.sh

XMLLINT=`which xmllint`

#Halt on error
set -e
#Display all executed commands
set -x

#NOTE: Python2's ETree does not understand the "unicode" output encoding.
#"$PYTHON2" cat_fileobjects.py ../samples/simple.xml
"$PYTHON3" cat_fileobjects.py --debug ../samples/simple.xml >cat_test_nocache.dfxml
"$PYTHON3" cat_fileobjects.py --debug --cache ../samples/simple.xml >cat_test_cache.dfxml

#This checks that the XML structure wasn't changed by cache cleaning.  Only the tail is hashed because the head contains metadata.
subj0="x$(tail -n 10 cat_test_nocache.dfxml | openssl dgst -sha1)"
subj1="x$(tail -n 10 cat_test_cache.dfxml | openssl dgst -sha1)"
test "$subj0" != "x"
test "$subj1" != "x"
test "$subj0" == "$subj1"

if [ -x "$XMLLINT" ]; then
  "$PYTHON3" cat_fileobjects.py ../samples/simple.xml | "$XMLLINT" -
else
  echo "Warning: xmllint not found.  Skipped check for if generated DFXML is valid XML." >&2
fi

test $(grep '<fileobject' ../samples/simple.xml | wc -l) == $(grep '<fileobject' cat_test_nocache.dfxml | wc -l)
test $(grep '<fileobject' ../samples/simple.xml | wc -l) == $(grep '<fileobject' cat_test_cache.dfxml | wc -l)
