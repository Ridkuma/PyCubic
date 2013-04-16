#!/usr/bin/python
#-*- coding:utf-8 -*-
"""CUB to GraphML file(s) conversion tool

"""

import subprocess, tempfile, os, sys, logging


def _convert(cub_file, graphml_file):
    """Convert a CUB Python File Object and write to a GraphML Python File Object"""
    # Get number of vertices and degree
    n = int(cub_file.readline())

    graphml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"  
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
         http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
    <graph id="G" edgedefault="directed"
           parse.nodes="{}" parse.edges="{}" 
           parse.maxindegree="3" parse.maxoutdegree="3">
""".format(n, n*3)

    node_id = 0
    for line in cub_file :
        edge_id = 0
        data = line.split()
        node = data[0]
        edges = data[1:]
        graphml += '\t\t<node id="{}" parse.indegree="3" parse.outdegree="3"/>\n'.format(node_id)
        for end_node in edges:
            graphml += '\t\t<edge id="{}_{}" source="{}" target="{}"/>\n'.format(node_id, end_node, node_id, end_node)
        node_id += 1

    graphml += "\t</graph>\n</graphml>"
    graphml_file.write(graphml)


def main(file, save_path=os.getcwd()):
    """Convert a CUB file or a folder to GraphML file(s)
    Arguments:
    file (string) -- filename of the file (or folder) to convert
    save_path (string) -- where to save the G6 files, defaults to current working directory
    
    """
    
    # Test if we have a folder
    if os.path.isdir(file):
        for root, dirs, files in os.walk(file):
            for file in files:
                (name, ext) = os.path.splitext(file)
                if '.cub' in ext:
                    cub_filename = os.path.normpath(os.path.join(root, file))
                    with open(cub_filename) as cub_file:
                        graphml_filename_arc = os.path.join(root, os.path.splitext(file)[0]+'.graphml')
                        graphml_filename = os.path.normpath(os.path.join(save_path, graphml_filename_arc))
                        try:
                            with open(graphml_filename, 'wb') as graphml_file:
                                _convert(cub_file, graphml_file)
                        except Exception as e:
                            logging.exception("Error while converting {}".format(cub_filename))
                            os.remove(graphml_filename)
        
    # or a lone CUB file
    else:
        (name, ext) = os.path.splitext(file)
        if '.cub' in ext:
            with open(file) as f:
                graphml_filename = os.path.normpath(os.path.join(save_path, name+'.graphml'))
                try:
                    with open(graphml_filename, 'wb') as graphml_file:
                        _convert(f, graphml_file)
                except Exception as e:
                    logging.exception("Error while converting {}".format(cub_filename))
                    os.remove(graphml_filename)
        else:
            print '{} must have a .cub extension to be converted'.format(file)


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
        print("""Usage: cub2graphml FILE [FILE]... [DEST]
FILE can either be a CUB file or a folder containing CUB files.
DEST, if present, specifies the path where to save the converted file(s).

Beware, DEST must be present if there are multiple FILE.""")
