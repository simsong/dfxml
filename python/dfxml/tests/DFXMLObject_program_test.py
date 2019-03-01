#!/usr/bin/env python

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

__version__ = "0.1.0"

import os
import sys

# "dfxml/python" directory where dfxml is the directory where repo is cloned
# should be added to sys.path for when these files are run by themselves from Makefile
dfxml_python_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if dfxml_python_dir not in sys.path:
    sys.path.append(dfxml_python_dir)
import dfxml.objects as Objects

def main():
    dobj = Objects.parse(args.in_dfxml)
    assert dobj.program == args.expected_program
    assert dobj.program_version == args.expected_program_version

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("in_dfxml")
    parser.add_argument("expected_program")
    parser.add_argument("expected_program_version")
    args = parser.parse_args()

    main()
