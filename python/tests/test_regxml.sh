#!/bin/sh
source paths.sh
python2.7 $DEMO_DIR/demo_registry_timeline.py ../tests/m57-charlie-2009-11-20-charlie-ntuser.dat.regxml
python3 $DEMO_DIR/demo_registry_timeline.py ../tests/m57-charlie-2009-11-20-charlie-ntuser.dat.regxml
