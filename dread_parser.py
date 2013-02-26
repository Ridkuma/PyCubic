#!/usr/bin/python
""" .cub cubic graph file parser
and dreadnaut commands generator
By Gwenegan Hudin
11/02/2013
gwenegan.hudin@insa-rennes.fr

"""

import re
import fileinput

f = fileinput.input()

# Looks for the order of the graph in the file
# Typically, will match "Graph X, order N." and capture N
for line in f :
	matchObj = re.match(r'^.+,\s\D+\s(\d+).\s$', line)
	if matchObj :
		order = matchObj.group(1);
		break
		
# Stores the edges of the graph in an array
for line in f :
    node, edges = line.split(':')
    node = int(node)
    edges = edges[:-1].split() # Suppress the final ';' and stores edges
    graphSets[int(node)] = [int(edge) for edge in edges]
