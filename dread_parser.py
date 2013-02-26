#!/usr/bin/python
""" .cub cubic graph file parser
and dreadnaut commands generator
By Gwenegan Hudin
11/02/2013
gwenegan.hudin@insa-rennes.fr

"""

import re
import sys
import fileinput

f = fileinput.input()

# Looks for the order of the graph in the file
# Typically, will match "Graph X, order N." and capture N
for line in f :
	if re.match(r'^.+,\s\D+\s(\d+).\s$', line) :
		order = \1
		break
		
# Stores the edges of the graph in an array
for line in f :
	re.match(r'^\s*(\d+)\s*:\s*(\d)\s*(\d);\s*$', line)
	#TODO make it work with an array
	edge1 = \1
	edge2 = \2