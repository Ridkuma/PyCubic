#!/usr/bin/python
#-*- coding:utf-8 -*-

from gi.repository import Gtk 
from graph_tool.all import *


class PyCubic:

    def __init__(self):

        self.builder = Gtk.Builder()
        self.builder.add_from_file("PyCubic.glade")
        self.graphFrame = self.builder.get_object("graph_frame")
        self.builder.connect_signals(Handler())
        
    # Add the GraphWidget to display graph g
    def displayGraph(self, g):
        layout = graph_tool.draw.sfdp_layout(g)
        self.graphDraw = graph_tool.draw.GraphWidget(g, layout)
        self.graphDraw.show_all()
        self.graphFrame.add(self.graphDraw)


class HelpWindow(Gtk.MessageDialog):
    
    def __init__(self):
        self.dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE, "Graph manipulation shortcuts")
        self.dialog.format_secondary_text(""" 
        Select vertice : Left Click
        
        Unselect : Right Click
        
        Select multiple vertices : Maj + Left click dragging
        
        Move vertice : Left Click dragging
        
        Pan graph : Middle Click dragging / Ctrl + Left Click dragging
        
        Zoom (no vertice scaling) : Mouse scroll
        
        Zoom (with vertice scaling) : Maj + Mouse scroll
        
        Rotate : Ctrl + Mouse scroll
        """)
        
        self.dialog.show_all()
        self.dialog.connect("response", self.destroy)
        
    def destroy(self, *args):
        for widget in args:
            Gtk.Widget.destroy(widget)
        
        
class Handler:

    def onDeleteWindow(self, *windows):
        Gtk.main_quit(*windows)

    # Help button click handler
    def on_help_button_clicked(self, helpButton):
        self.helpWindow = HelpWindow()
    


g = Graph(directed = False)
v1 = g.add_vertex()
v2 = g.add_vertex()
v3 = g.add_vertex()
v4 = g.add_vertex()
v5 = g.add_vertex()

e1 = g.add_edge(v1, v2)
e2 = g.add_edge(v3, v4)
e3 = g.add_edge(v1, v4)


instance = PyCubic()
instance.displayGraph(g)
Gtk.main()
