#!/usr/bin/python
#-*- coding:utf-8 -*-

from gi.repository import Gtk 
from graph_tool.all import *
import cub2graph, sys


class PyCubic:

    def __init__(self):

        self.builder = Gtk.Builder()
        self.builder.add_from_file("PyCubic.glade")
        self.graphFrame = self.builder.get_object("graph_frame")
        self.builder.connect_signals(Handler(self.builder, self.graphWidget))
        
    # Add the GraphWidget to display graph g
    def displayGraph(self, g):
        layout = graph_tool.draw.sfdp_layout(g)
        self.graphWidget = graph_tool.draw.GraphWidget(g, layout)
        self.graphWidget.show_all()
        self.graphFrame.add(self.graphWidget)


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
    
     
    def destroy(self, widget, *args):
        Gtk.Widget.hide(widget)
        
        
class Handler:

    def __init__(self, builder, graphWidget) :
        self.builder = builder
        self.graphWidget = graphWidget

    # Main window delete handler
    def onDeleteWindow(self, *windows):
        Gtk.main_quit(*windows)
        
    # Theta button click handler
    def on_theta_button_clicked(self, button):
        theta = ThetaHandler(self.graphWidget)
        self.graphWidget.connect("button_pressed_event", theta.thetabutton_pressed_event)
        
    # ThetaMinus button click handler
    def on_thetaMinus_button_clicked(self, button):
        theta = ThetaHandler(self.graphWidget)
        self.graphWidget.connect("button_pressed_event", theta.thetaMinusbutton_pressed_event)

    # Help button click handler
    def on_help_button_clicked(self, button):
        self.helpWindow = HelpWindow()
    
    # Quit Menu Item click handler
    def on_quit_menu_activate(self, menuItem):
        Gtk.main_quit(menuItem)
        
    # About Menu Item click handler
    def on_about_menu_activate(self, menuItem):
        self.aboutdialog = self.builder.get_object("about_dialog")
        self.aboutdialog.run()
        self.aboutdialog.hide()
        
        
class ThetaHandler:

    def __init__(self, graphWidget):
        self.graphWidget = graphWidget
        self.firstPick = None
        self.secondPick = None

    # GraphWidget click handler while Theta Operation
    def thetabutton_pressed_event(self, widget, event):
        if event.button == 1 : # and not event.state & Gdk.ModifierType.CONTROL_MASK :  # TODO Dafuq is la deuxième condition ?
            if self.graphWidget.picked == False :
                self.graphWidget.init_picked()
                self.graphWidget.queue.draw()
                if self.firstPick == None :
                    self.firstPick = self.graphWidget.picked
                elif self.secondPick == None :
                    self.secondPick = self.graphWidget.picked
                else :
                # TODO apply THETA operation, we have our two vertices
                
    
        # Restore to original behaviour
        self.graphWidget.connect("button_pressed_event", graphWidget.button_pressed_event)
        
    
    # GraphWidget click handler while ThetaMinus Operation
    def thetaMinusbutton_pressed_event(self, widget, event):
    
        # Restore to original behaviour
        self.graphWidget.connect("button_pressed_event", graphWidget.button_pressed_event)
    



with open(sys.argv[1]) as file :
    g = cub2graph._convert(file)

    instance = PyCubic()
    instance.displayGraph(g)
    Gtk.main()
