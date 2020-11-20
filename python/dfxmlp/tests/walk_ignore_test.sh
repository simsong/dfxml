#!/bin/bash

source paths.sh

set -e
set -u

pythonbin="$1"

mkdir -p walk_ignore_test/foo/bar/baz
echo 'contents c' > walk_ignore_test/foo/bar/baz/c
echo 'contents b' > walk_ignore_test/foo/bar/b
echo 'contents a' > walk_ignore_test/foo/a

$pythonbin $TOOLS_DIR/walk_to_dfxml.py \
  -i atime \
  -i ctime \
  -i crtime \
  -i gid \
  -i inode \
  -i mtime@d \
  -i uid \
  | \
    xmllint --format - \
    > walk_ignore_genprops_test.dfxml

$pythonbin verify_walk_ignore_genprops_test.py walk_ignore_genprops_test.dfxml

$pythonbin $TOOLS_DIR/walk_to_dfxml.py \
  --ignore-hashes \
  | \
    xmllint --format - \
    > walk_ignore_nohash_test.dfxml

$pythonbin verify_walk_ignore_nohash_test.py walk_ignore_nohash_test.dfxml
