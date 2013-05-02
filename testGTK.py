#!/usr/bin/python
#-*- coding:utf-8 -*-

from gi.repository import Gtk, Gdk
from graph_tool.all import *
import cub2graph, sys


class PyCubic:

    def __init__(self):

        self.builder = Gtk.Builder()
        self.builder.add_from_file("PyCubic.glade")
        self.graphFrame = self.builder.get_object("graph_frame")
        
    # Add the GraphWidget to display graph g
    def displayGraph(self, g):
        layout = graph_tool.draw.sfdp_layout(g)
        self.graphWidget = GraphWidgetCustom(g, layout)
        self.graphWidget.show_all()
        self.graphFrame.add(self.graphWidget)
        
class GraphWidgetCustom(graph_tool.draw.GraphWidget):

    def __init__(self, g, layout) :
        super(GraphWidgetCustom, self).__init__(g, layout)
        self.theta = False
        self.thetaMinus = False
        self.firstPick = None
        self.secondPick = None
    
    def button_press_event(self, widget, event):
        if self.theta == True :
            print "Theta"
            self.graphWidget.init_picked()
            self.graphWidget.queue.draw()
            if self.firstPick == None :
                self.firstPick = self.graphWidget.picked
            elif self.secondPick == None :
                self.secondPick = self.graphWidget.picked
            else :
                print "Pouet"
                # TODO apply THETA operation, we have our two vertices
                self.theta = False
                
        elif self.thetaMinus == True :
            print "ThetaMinus"
            
        else : 
            super(self, widget, event)


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
        print "Theta button clicked"
        # TODO Desactivate Theta operations buttons
        # TODO Update the Status bar
        self.graphWidget.theta = True
        
    # ThetaMinus button click handler
    def on_thetaMinus_button_clicked(self, button):
        print "Theta Minus button clicked"
        theta = ThetaHandler(self.graphWidget)
        self.graphWidget.connect("button_press_event", theta.thetaMinusbutton_pressed_event)

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


with open(sys.argv[1]) as file :
    g = cub2graph._convert(file)

    instance = PyCubic()
    instance.displayGraph(g)
    instance.builder.connect_signals(Handler(instance.builder, instance.graphWidget))
    Gtk.main()
