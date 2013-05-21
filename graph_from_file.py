#-*- coding:utf-8 -*-
"""Graph from file creation

Return a graph_tool.Graph from either CUB or G6 files.
Call g62cub.py for G6 format support.

"""

import g62cub
import tempfile
from graph_tool.all import *

class GraphFromFile:
    """Static class for graph generation from file"""
    
    @classmethod
    def from_cub(cls, cub_file):
        """Convert a CUB Python File Object cub_file and return a graph_tool.Graph Object"""
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
                graph_dict[end_node].remove(start_node)
                graph.add_edge(graph.vertex(start_node), graph.vertex(end_node))
             
        return graph

    @classmethod
    def from_g6(cls, g6_file):
        """Convert a G6 Python File Object g6_file and return a graph_tool.Graph Object"""
        temp_file = tempfile.NamedTemporaryFile()
        g62cub._convert(g6_file, temp_file)
        temp_file.seek(0)
        graph = cls.from_cub(temp_file)
        temp_file.close()
        return graph
