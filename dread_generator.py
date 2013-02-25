#!/usr/bin/python
""" .cub cubic graph file parser
and dreadnaut commands generator
By Gwenegan Hudin
11/02/2013/home/gwaihir/Dropbox/Etude Pratique/dread_parser.py
gwenegan.hudin@insa-rennes.fr

"""

import subprocess
import tempfile
import shutil
import os
import sys
import fileinput

""" Script variables """

# Open the input file
f = fileinput.input()

# Get number of vertices and degree
n, deg = [int(x) for x in f.readline().split()]

""" dreadnaut commands generation """

# Header, only consists in declaring the number of vertices
header = "n=" + str(n) + '\n'

# Parse the .cub file and generates commands for each line
s = ""
for line in f :
    set = line.split()
    for v in set[1:deg+1] :
        s += " "+ v
    s+= "; "

# Create the final dreadnaut command string
command = header + s[1:len(s)-2] + '.'

fileinput.close()

""" dreadnaut temp file creation """

temp = tempfile.NamedTemporaryFile()
temp.write(command)
temp.flush()

""" dreadnaut to G6 conversion """
# ZONE DE TRAVAUX, FERMER LES YEUX
os.system("sudo \"" +  os.getcwd() + "/\"" + "dretog " + temp.name + 
        " \"" +  os.getcwd() + "/\"" + "dread_sample")

temp.close()

