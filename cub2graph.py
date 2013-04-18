#!/usr/bin/python
#-*- coding:utf-8 -*-
"""CUB file to graph-tool's Graph object conversion tool

"""

import subprocess, tempfile, os, sys, logging
from graph_tool.all import *

def _convert(cub_file):
    """Convert a CUB Python File Object and return a graph-tool Graph Object"""
    # Get number of vertices
    n = int(cub_file.readline())
    
    # Initialize graph
    graph = Graph(directed=False)
    
    # Get all graph data
    graph_dict = {}
    for line in cub_file :
        data = line.split()
        node = data[0]
        edges = data[1:]
        graph_dict[node] = edges
        graph.add_vertex() # Adding vertex now saves some computation
    
    for start_node, edges in graph_dict.iteritems():
        for end_node in edges:
            graph.add_edge(graph.vertex(start_node), graph.vertex(end_node))
         
    return graph
    
def main(file):
    """Convert a CUB file (resp. a folder) to a graph-tool Graph Object
       (resp. an array of graph-tool Graph Objects)
    Arguments:
    file (string) -- filename of the file (or folder) to convert
    
    """
    
    # Test if we have a folder
    if os.path.isdir(file):
        graphs = []
        for root, dirs, files in os.walk(file):
            for file in files:
                (name, ext) = os.path.splitext(file)
                if '.cub' in ext:
                    cub_filename = os.path.normpath(os.path.join(root, file))
                    with open(cub_filename) as cub_file:
                        graphs.append(_convert(cub_file))
        return graphs
        
    # or a lone CUB file
    else:
        (name, ext) = os.path.splitext(file)
        if '.cub' in ext:
            with open(file) as f:
                return _convert(f)
        else:
            print '{} must have a .cub extension to be converted'.format(file)


# If script is called via command line, exec main with each argument if any,
# or print usage
if __name__ == "__main__":
    args = len(sys.argv)
    if args >= 2:
        for argv in sys.argv[1:]:
            main(argv)
    else:
        print("""Usage: cub2graph FILE [FILE]...
FILE can either be a CUB file or a folder containing CUB files.""")
