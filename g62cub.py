#!/usr/bin/python
#-*- coding:utf-8 -*-
"""G6 to CUB file(s) conversion tool

"""

import re, os, sys, tempfile, subprocess, zlib, zipfile

def _convert(g6_file, cub_file):
    """Convert a G6 Python File Object and writes to a CUB Python File Object"""
    
    string = g6_file.readline()

    # Run showg and store output in a tempFile file
    tempFile = tempfile.NamedTemporaryFile()
    tempFile.readline()
    subprocess.call("\"" +  os.getcwd() + "/\"" + "showg " + "\"" + 
                    g6_file.name + "\" " + tempFile.name, shell = True)

    # Look for the order of the graph in the file
    # Typically, will match "Graph X, order N." and capture N
    for line in tempFile :
	    matchObj = re.match(r'^.+,\s\D+\s(\d+).\s$', line)
	    if matchObj :
		    order = int(matchObj.group(1));
		    break
		
    # Stores the edges of the graph in an array
    graphSets = []
    for line in tempFile :
        node, edges = line.split(':')
        edges = (edges.replace(';','')).split() # Delete the final ';' and store edges
        graphSets.insert(int(node), edges)
        
    # Generate the .cub file
    cub_file.write(str(order) + "\t" + "3 \n")
    for i in range(0, order) :
        cub_file.write(str(i) + "\t")
        edges = "\t".join(graphSets[i])
        cub_file.write(edges + "\n")
        
    cub_file.flush()

    tempFile.close()
    cub_file.close()

def main(file, basepath=os.getcwd()):
    """Convert a G6 file or zipped G6 files to CUB file(s)
    Arguments:
    file -- filename of the file to convert
    basepath -- where to save the CUB files, defaults to current working directory
    
    """
    
    with open(file) as f:
        # Test if we have a zip
        if zipfile.is_zipfile(f):
            with zipfile.ZipFile(f) as myzip:
                # Convert every G6 in the zip
                zipname = os.path.splitext(file)[0]
                for filename in myzip.namelist():
                    # Treat only files and skip folders themselves
                    if not filename.endswith('/'):
                        root, name = os.path.split(filename)
                        # When subfolder is same name as archive, suppress it
                        if root == zipname:
                            root = ''
                        directory = os.path.normpath(os.path.join(basepath, zipname, root))
                        # Make subfolder if it does not exist
                        if not os.path.isdir(directory):
                            os.makedirs(directory)
                        # Create empty CUB file and fill it
                        cub_filename = os.path.join(directory, os.path.splitext(file)[0]+'.cub')
                        cub_file = open(cub_filename, 'wb')
                        with myzip.open(filename, 'rU') as g6_file:
                            _convert(g6_file, cub_file)
                            
        # or a lone G6 file
        else:
            cub_filename = os.path.normpath(os.path.join(basepath, os.path.splitext(file)[0]+'.cub'))
            cub_file = open(cub_filename, 'wb')
            _convert(f, cub_file)
    
# If script is called via command line, exec main with each argument if any,
# or print usage
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        for argv in sys.argv:
            main(sys.argv[1])
    else:
        print("""Usage: g62cub FILE [FILE]...
FILE can either be a G6 file or a ZIP containing G6 files""")