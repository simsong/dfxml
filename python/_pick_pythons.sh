
# This script is meant to be included in Bash scripts that need a Python v2 and v3.
# An autotool configure script would also suffice.
# The 'or echo' statements keep the subshell from returning an error exit status on missing a Python version.
PYTHON2=`which python`
PYTHON3=`which python3.4 || echo`
if [ -z "$PYTHON3" ]; then
  PYTHON3=`which python3.3 || echo`
  if [ -z "$PYTHON3" ]; then
    PYTHON3=`which python3.2 || echo`
    if [ -z "$PYTHON3" ]; then
      PYTHON3=`which python3 || echo`
      if [ -z "$PYTHON3" ]; then
        echo "Error: Could not find a python3 executable." >&2
        exit 1
      fi
    fi
  fi
fi
