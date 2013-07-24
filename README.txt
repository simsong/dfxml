DFXML tools

python/ - tools in Python
src/    - tools in C

================================================================
To get back on master:


Summary:
$ git checkout -b newbranch
$ git checkout master
$ git merge newbranch
$ git branch -d newbranch

or:

$ git checkout -b tmp  ; git checkout master ; git merge tmp ; git branch -d tmp ; git push git@github.com:simsong/dfxml.git master
