#!/usr/bin/python
#-*- coding:utf-8 -*-
"""G6 to CUB file(s) conversion tool

Usage: g62cub FILE [FILE]... [DEST]

FILE can either be a G6 file or a ZIP containing G6 files.
DEST, if present, specifies the path where to save the converted file(s).

Beware, DEST must be present if there are multiple FILE.

"""

import re, os, sys, tempfile, subprocess, zlib, zipfile, logging

def _convert(g6_file, cub_file):
    """Convert a G6 Python File Object and write to a CUB Python File Object"""
    
    g6_file.readline()

    # Run showg and store output in a tempFile file
    tempFile = tempfile.NamedTemporaryFile()
    tempFile.readline()
    subprocess.call("showg " + "\"" + 
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
    cub_file.write(str(order) + "\n")
    for i in range(0, order) :
        cub_file.write(str(i) + "\t")
        edges = "\t".join(graphSets[i])
        cub_file.write(edges + "\n")
        
    cub_file.flush()

    tempFile.close()


def main(file, save_path=os.getcwd()):
    """main(file, save_path=os.getcwd())
    
    Convert a G6 file or zipped G6 files to CUB file(s)
    
    Arguments:
    file (string) -- filename of the file to convert
    
    Keyword arguments:
    save_path (string) -- where to save the CUB files (default: current working directory)
    
    """
    
    with open(file) as f:
        # Test if we have a zip
        if zipfile.is_zipfile(f):
            with zipfile.ZipFile(f) as myzip:
                # Convert every G6 in the zip
                zipname = os.path.basename(os.path.splitext(file)[0])
                for filename in myzip.namelist():
                    # Treat only files with .g6 extensions
                    (name, ext) = os.path.splitext(filename)
                    if '.g6' in ext:
                        root, basename = os.path.split(filename)
                        # When subfolder is same name as archive, suppress it
                        if root == zipname:
                            root = ''
                        directory = os.path.normpath(os.path.join(save_path, root))
                        # Make subfolder if it does not exist
                        if not os.path.isdir(directory):
                            os.makedirs(directory)
                        # Create empty CUB file and fill it
                        cub_filename = os.path.join(directory, name+'.cub')
                        try:
                            with open(cub_filename, 'wb') as cub_file:
                                myzip.extract(filename)
                                with open(filename, 'rU') as g6_file:
                                    _convert(g6_file, cub_file)
                                os.remove(filename)
                        except Exception as e:
                            logging.exception("Error while converting {}".format(cub_filename))
                            os.remove(cub_filename)
        # or a lone G6 file
        else:
            (name, ext) = os.path.splitext(file)
            if '.g6' in ext:
                cub_filename = os.path.normpath(os.path.join(save_path, name+'.cub'))
                try:
                    with open(cub_filename, 'wb') as cub_file:
                        _convert(f, cub_file)
                except Exception as e:
                    logging.exception("Error while converting {}".format(cub_filename))
                    os.remove(cub_filename)
            else:
                print '{} must have a .g6 extension to be converted'.format(file)


# If script is called via command line, exec main with each argument if any,
# or print usage
if __name__ == "__main__":
    args = len(sys.argv)
    if args > 2:
        dest = sys.argv[-1]
        for argv in sys.argv[1:-1]:
            main(argv, dest)
    elif args == 2:
        main(sys.argv[1])
    else:
        print """Usage: g62cub FILE [FILE]... [DEST]
FILE can either be a G6 file or a ZIP containing G6 files.
DEST, if present, specifies the path where to save the converted file(s).

Beware, DEST must be present if there are multiple FILE."""
