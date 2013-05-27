Prerequisites and installation
===================================

Our application requires some dependencies to execute. Below are listed the prerequisites and some installation examples.

Prerequisites
---------------------

* Python 2.7+: http://www.python.org/download/releases/2.7.5/ (should already be installed under Unix)
* nauty and Traces programs: http://cs.anu.edu.au/~bdm/nauty/
* graph-tool library: http://projects.skewed.de/graph-tool/

Installation examples
---------------------

Example for Debian, DISTRIBUTION being replaced by squeeze or sid:
::
   $ apt-get install nauty
   $ vim /etc/apt/sources.list
   # Add the following lines, replacing DISTRIBUTION
   deb http://downloads.skewed.de/apt/DISTRIBUTION DISTRIBUTION main
   deb-src http://downloads.skewed.de/apt/DISTRIBUTION DISTRIBUTION main
   # Save file
   $ apt-get update
   $ apt-get install python-graph-tool

Example for Ubuntu, DISTRIBUTION being replaced by raring, quantal,
precise, oneiric, natty or maverick:
::
   $ apt-get install nauty
   $ vim /etc/apt/sources.list
   # Add the following lines, replacing DISTRIBUTION
   deb http://downloads.skewed.de/apt/DISTRIBUTION DISTRIBUTION universe
   deb-src http://downloads.skewed.de/apt/DISTRIBUTION DISTRIBUTION universe
   # Save file
   $ apt-get update
   $ apt-get install python-graph-tool
