#!/bin/sh

# Originally from https://gist.github.com/GraemeConradie/49d2f5962fa72952bc6c64ac093db2d5
# Install gnu autotools for running under github actions

##
# Install autoconf, automake and libtool smoothly on Mac OS X.
# Newer versions of these libraries are available and may work better on OS X
##

echo '###################################'
echo 'install_autotools.sh'

export build=~/devtools # or wherever you'd like to build
mkdir -p $build

##
# Autoconf
# https://ftpmirror.gnu.org/autoconf

echo ========
echo autoconf
cd $build
curl -OL https://ftpmirror.gnu.org/autoconf/autoconf-2.71.tar.gz &&\
tar xzf autoconf-2.71.tar.gz && cd autoconf-2.71 && ./configure --prefix=/usr/local && make && sudo make install
export PATH=$PATH:/usr/local/bin

##
# Automake
# https://ftpmirror.gnu.org/automake

echo =======
echo automake
cd $build
curl -OL https://ftpmirror.gnu.org/automake/automake-1.16.tar.gz &&\
tar xzf automake-1.16.tar.gz && cd automake-1.16 && ./configure --prefix=/usr/local && make && sudo make install

##
# Libtool
# https://ftpmirror.gnu.org/libtool

echo =======
echo libtool
cd $build
curl -OL https://ftpmirror.gnu.org/libtool/libtool-2.4.6.tar.gz &&\
tar xzf libtool-2.4.6.tar.gz && cd libtool-2.4.6 &&  ./configure --prefix=/usr/local && make && sudo make install

echo =======================
echo "Installation complete."
echo PATH=$PATH
echo which autoconf: `which autoconf`
echo which automake: `which automake`
echo which libtool: `which libtool`
