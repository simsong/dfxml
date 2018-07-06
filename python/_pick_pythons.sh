
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

# This script is meant to be included in Bash scripts (especially unit
# tests) that need a Python v2 and v3.  It defines the variables PYTHON2
# and PYTHON3 according to the highest available minor version number.
#
# (An autotool configure script would also suffice.)
#
# The 'or echo' statements keep the subshell from returning an error
# exit status on missing a Python version.

# In some environments, these Python 2 calls may find different Python
# executables.  For instance, in macOS using MacPorts, 'python' by
# default finds the system Python 2.7, whereas 'python2.7' finds the
# MacPorts Python 2.7. This script opts to select for MacPorts in that
# environment because of package management.
PYTHON2=`which python2.7 2>/dev/null || echo`
if [ -z "$PYTHON2" ]; then
  PYTHON2=`which python`
fi

PYTHON3=`which python3.6 2>/dev/null || echo`
if [ -z "$PYTHON3" ]; then
  PYTHON3=`which python3.5 2>/dev/null || echo`
  if [ -z "$PYTHON3" ]; then
    PYTHON3=`which python3.4 2>/dev/null || echo`
    if [ -z "$PYTHON3" ]; then
      PYTHON3=`which python3 2>/dev/null || echo`
      if [ -z "$PYTHON3" ]; then
        echo "Error: Could not find a python3 executable." >&2
        exit 1
      fi
    fi
  fi
fi
