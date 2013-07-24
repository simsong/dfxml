
# This script is meant to be included in Bash scripts that need a Python v2 and v3.
# An autotool configure script would also suffice.
PYTHON2=`which python`
PYTHON3=`which python3.3`
if [ -z "$PYTHON3" ]; then
  PYTHON3=`which python3.2`
  if [ -z "$PYTHON3" ]; then
    PYTHON3=`which python3`
    if [ -z "$PYTHON3" ]; then
      echo "Error: Could not find a python3 executable." >&2
      exit 1
    fi
  fi
fi
