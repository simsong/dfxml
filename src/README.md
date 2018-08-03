This file is public domain.

Sometimes people make changes to this file when it is a sub-module. If
you do so, the following incantation will create a branch called
'tmp', checkout the master, merge the tmp into the master, delete the
tmp branch, and push the results back to the origin:

    git checkout -b tmp  ; git checkout master ; git merge tmp ; git branch -d tmp 

Then you can `git push` as necessary.
