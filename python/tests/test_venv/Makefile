#!/usr/bin/make -f

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

SHELL = /bin/bash

# The PYTHON variable is written to be provided primarily by a Travis virtual environment.  Local tests should provide their own python binary by calling 'make PYTHON=python3.7 [...]'
PYTHON ?= $(shell which python 2>/dev/null || which python3 2>/dev/null || which python3.7 2>/dev/null || which python3.6 2>/dev/null)
ifeq ($(PYTHON),)
$(error PYTHON not defined)
endif

VIRTUALENV ?= $(shell which virtualenv 2>/dev/null || which virtualenv-3.7 2>/dev/null || which virtualenv-3.6 2>/dev/null)
ifeq ($(VIRTUALENV),)
$(error VIRTUALENV not defined)
endif

all: \
  .venv.done.log

.venv.done.log: \
  ../../setup.py
	rm -rf venv
	$(VIRTUALENV) \
	  --python=$(PYTHON) \
	  venv
	source venv/bin/activate \
	  ; pip install ../..
	touch $@

check: \
  .venv.done.log \
  simple_read_dfxml.py
	source venv/bin/activate \
	  ; python simple_read_dfxml.py ../../../samples/difference_test_0.xml

clean:
	@rm -rf .venv.done.log venv
