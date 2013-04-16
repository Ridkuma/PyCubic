#!/usr/bin/python
#-*- coding:utf-8 -*-

from gi.repository import Gtk 
from graph_tool.all import *


class testGTK:

    def __init__(self, g):

        self.builder = Gtk.Builder()
        self.builder.add_from_file("PyCubic.glade")

        self.window = self.builder.get_object("MainWindow")
        self.window.connect("delete-event", Gtk.main_quit)
        
        self.graphFrame = self.builder.get_object("graph_frame")
        layout = graph_tool.draw.sfdp_layout(g)
        self.graphDraw = graph_tool.draw.GraphWidget(g, layout)
        self.graphDraw.show_all()
        self.graphFrame.add(self.graphDraw)


g = Graph(directed = False)
v1 = g.add_vertex()
v2 = g.add_vertex()
v3 = g.add_vertex()
v4 = g.add_vertex()
v5 = g.add_vertex()

e1 = g.add_edge(v1, v2)
e2 = g.add_edge(v3, v4)


test = testGTK(g)
Gtk.main()
