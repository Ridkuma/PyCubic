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
    def display_graph(self, g):
        layout = sfdp_layout(g)
        self.graphWidget = GraphWidgetCustom(self, g, layout)
        self.graphWidget.show_all()
        self.graphFrame.add(self.graphWidget)
        
    # Clear the current graph
    def clear_graph(self) :
        self.graphWidget.destroy()
        self.graphWidget = None
        
    # Set a widget to sensitive
    def activate_widget(self, widgetName) :
        self.builder.get_object(widgetName).set_sensitive(True)
        
    # Set a widget to insensitive
    def deactivate_widget(self, widgetName) :
        self.builder.get_object(widgetName).set_sensitive(False)
    
        
class GraphWidgetCustom(graph_tool.draw.GraphWidget):

    def __init__(self, instance, g, layout) :
        super(GraphWidgetCustom, self).__init__(g, layout, update_layout = False)
        self.instance = instance
        self.theta = False
        self.thetaMinus = False
        self.firstPick = None
        self.secondPick = None
    
    # Custom Button Press Event, implementing Theta operations
    def button_press_event(self, widget, event):
        # Desactivate Layout Changing (or the prop map pointers will derpyderp)
        self.instance.deactivate_widget("layoutMenu")
        
        # Theta operation handler
        if self.theta == True :
            print "Theta"
            self.init_picked()
            self.queue_draw()
            if self.firstPick == None :
                self.firstPick = self.picked
                self.picked = None
                print "First Pick"
            elif self.secondPick == None :
                self.secondPick = self.picked
                self.picked = None
                print "Second Pick"
                
                print "Fin Theta"
                
                # TODO apply THETA operation, we have our two vertices
                self.g.clear_vertex(self.firstPick)
                self.g.clear_vertex(self.secondPick)
                self.g.remove_vertex(self.firstPick, True)
                self.g.remove_vertex(self.secondPick, True)
                self.reset_layout()
                self.regenerate_surface()
                self.theta = False
                self.firstPick = None
                self.secondPick = None
                self.reactivate_operations()
                
                
        # Theta Minus operation handler
        elif self.thetaMinus == True :
            print "ThetaMinus"
            self.thetaMinus = False
            self.reactivate_operations()
        
        # Default behaviour, inherited    
        else : 
            super(GraphWidgetCustom, self).button_press_event(widget, event)
            
    # Reactivate Theta and ThetaMinus buttons
    def reactivate_operations(self):
        self.instance.activate_widget("theta_button")
        self.instance.activate_widget("thetaMinus_button")
        self.instance.deactivate_widget("cancel_button")
        
    # Cancel all current operations
    def cancel_operations(self):
        self.reactivate_operations()
        self.theta = False
        self.thetaMinus = False
        self.firstPick = None
        self.secondPick = None
            
    # Dynamically change the graph layout with various algorithms
    def change_default_layout(self, algo) :
        if algo == "random" :
            self.pos = random_layout(self.g)
        elif algo == "sfdp" :
            self.pos = sfdp_layout(self.g)
        elif algo == "arf" :
            self.pos = arf_layout(self.g)
        elif algo == "fruchter" :
            self.pos = fruchterman_reingold_layout(self.g)
        self.regenerate_surface()
        self.fit_to_window()


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
        
    ## BUTTON HANDLERS ##
        
    # Theta button click handler
    def on_theta_button_clicked(self, button):
        print "Theta button clicked"
        self.builder.get_object("theta_button").set_sensitive(False)
        self.builder.get_object("thetaMinus_button").set_sensitive(False)
        self.builder.get_object("cancel_button").set_sensitive(True)
        # TODO Update the Status bar
        self.graphWidget.theta = True
        
    # ThetaMinus button click handler
    def on_thetaMinus_button_clicked(self, button):
        print "Theta Minus button clicked"
        self.builder.get_object("theta_button").set_sensitive(False)
        self.builder.get_object("thetaMinus_button").set_sensitive(False)
        # TODO Update the Status bar
        self.graphWidget.thetaMinus = True
        
    # Cancel button click handler
    def on_cancel_button_clicked(self, button):
        print "Cancel"
        self.graphWidget.cancel_operations()
        

    # Help button click handler
    def on_help_button_clicked(self, button):
        self.helpWindow = HelpWindow()
        
    ## MENU HANDLERS ##
    
    # Quit Menu Item click handler
    def on_quit_menu_activate(self, menuItem):
        Gtk.main_quit(menuItem)
        
    # Random Layout Menu click handler
    def on_random_menu_activate(self, menuItem):
        self.graphWidget.change_default_layout("random")
        
    # SFDP Layout Menu click handler
    def on_sfdp_menu_activate(self, menuItem):
        self.graphWidget.change_default_layout("sfdp")
        
    # ARF Layout Menu click handler
    def on_arf_menu_activate(self, menuItem):
        self.graphWidget.change_default_layout("arf")
        
    # Fruchter Layout Menu click handler
    def on_fruchter_menu_activate(self, menuItem):
        self.graphWidget.change_default_layout("fruchter")
        
    # About Menu Item click handler
    def on_about_menu_activate(self, menuItem):
        self.aboutdialog = self.builder.get_object("about_dialog")
        self.aboutdialog.run()
        self.aboutdialog.hide()


with open(sys.argv[1]) as file :
    g = cub2graph._convert(file)

    instance = PyCubic()
    instance.display_graph(g)
    instance.builder.connect_signals(Handler(instance.builder, instance.graphWidget))
    Gtk.main()
