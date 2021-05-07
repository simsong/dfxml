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

SHELL ?= /bin/bash

SCHEMA_REPOSITORY_URL ?= https://github.com/dfxml-working-group/dfxml_schema.git

all:

.PHONY: schema-init

schema-init: schema/dfxml.xsd

schema/dfxml.xsd: dfxml_schema_commit.txt
	if [ -z "$(SCHEMA_REPOSITORY_URL)" ]; then echo 'ERROR:Makefile:Please provide a URL for the Makefile parameter SCHEMA_REPOSITORY_URL.' >&2 ; exit 1 ; fi
	if [ ! -d schema ]; then git clone $(SCHEMA_REPOSITORY_URL) schema ; cd schema ; git checkout $$(head -n1 ../dfxml_schema_commit.txt) ; fi
	test -r $@ && touch $@

clean:
	find . -name '*~' -exec rm {} \;

check:
	(cd src;make check)
	@echo performing checks currently in Travis
