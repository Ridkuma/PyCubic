#!/bin/sh
# Builds a package to be uploaded on SourceForge.

if [ $# -eq 1 ]
then
    name=PyCubic_v$1
    cd sphinx
    make html
    cd ..
    rm -rf $name
    mkdir $name
    cp -r *.py *.glade *.png COPYING README tests doc $name
    tar -cvzf $name.tar.gz $name
    rm -rf $name

else
    echo "Usage: ./release.sh VERSION_NUMBER
       Builds a package PyCubic_v\$VERSION_NUMBER.tar.gz
       to be uploaded on SourceForge."

fi
