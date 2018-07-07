#!/bin/bash

set -e
set -u

pythonbin="$1"

mkdir -p test_walk_ignore/foo/bar/baz
echo 'contents c' > test_walk_ignore/foo/bar/baz/c
echo 'contents b' > test_walk_ignore/foo/bar/b
echo 'contents a' > test_walk_ignore/foo/a

$pythonbin ../walk_to_dfxml.py \
  -i atime \
  -i ctime \
  -i crtime \
  -i gid \
  -i inode \
  -i mtime@d \
  -i uid \
  | \
    xmllint --format - \
    > test_walk_ignore_genprops.dfxml

$pythonbin verify_walk_ignore_genprops.py test_walk_ignore_genprops.dfxml

$pythonbin ../walk_to_dfxml.py \
  --ignore-hashes \
  | \
    xmllint --format - \
    > test_walk_ignore_nohash.dfxml

$pythonbin verify_walk_ignore_nohash.py test_walk_ignore_nohash.dfxml
