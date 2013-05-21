#-*- coding:utf-8 -*-
"""PyCubic main window

Main object of the package, contains all the subwindows of the interface

"""

import os
import logging
from gi.repository import Gtk
from graph_tool.all import *
from graph_widget import GraphWidget

class PyCubic:
    """Main window"""

    def __init__(self):
        """Create a PyCubic window instance"""

        self.builder = Gtk.Builder()
        self.builder.add_from_file("PyCubic.glade")
        self.graphFrame = self.builder.get_object("graph_frame")
        self.treeView = self.builder.get_object("graph_treeview")
        self.statusBar = self.builder.get_object("statusbar")
        self.update_statusbar("Welcome to PyCubic!")
        self.treeView_menu = self.build_treeView_menu()
        
    def display_graph(self, g, layout=None):
        """Load GraphWidget and display graph g using layout (if available)
        
        Arguments:
        g -- a graph_tool.Graph
        
        Keyword arguments:
        layout -- a graph_tool.PropertyMap to be applied to the widget (default: None)
                  If True, loads a custom PropertyMap from layout file
        
        """
        if layout == None: # Generate a SFDP layout
            self.graphWidget = GraphWidget(self, g, layout=sfdp_layout(g))
        elif layout != True: # Load given PropertyMap
            self.graphWidget = GraphWidget(self, g, layout=layout)
        else: # Custom layout, load it
            try:
                self.graphWidget = GraphWidget(self, g, pos=g.vp["layout"])
            except KeyError: # just in case custom layout is invalid
                self.graphWidget = GraphWidget(self, g, layout=sfdp_layout(g))
        self.graphWidget.show_all()
        self.graphFrame.add(self.graphWidget)
        
    def clear_graph(self) :
        """Clear the GraphWidget and its graph"""
        self.graphWidget.destroy()
        self.graphWidget = None
    
    def build_treeView_menu(self):
        """Return the treeview right-click menu"""
        treeView_menu = Gtk.Menu()
        for icon, label, handler in [(Gtk.STOCK_EXECUTE, "Load", self.on_treeView_menu_load_button_handler),
                               (Gtk.STOCK_DELETE, "Delete", self.on_treeView_menu_delete_button_handler)]:
            menu_item = Gtk.ImageMenuItem(icon)
            menu_item.set_label(label)
            treeView_menu.append(menu_item)
            menu_item.connect("activate", handler)
            menu_item.show()
        return treeView_menu
    
    def build_treeStore(self) :
        """Prepare and fill the TreeStore"""
        filename = os.path.splitext(os.path.basename(self.filename))[0]
        self.treeStore = Gtk.TreeStore(str)
    
        # Fill the Tree Store   
        self.layoutList = dict()
        self.layouts = self.treeStore.append(None, ["Saved layouts"])
        for root, dirs, files in os.walk(os.path.join(os.getcwd(), "saved_layouts", filename)):
            for file in files :
                (name, ext) = os.path.splitext(file)
                if ext == ".graphml":
                    self.layoutList[name] = os.path.join(root, file)
                    self.treeStore.append(self.layouts, [name])
        pmatchings = self.treeStore.append(None, ["Perfect matchings"])
        self.treeStore.append(pmatchings, ["Unknown"]) # TODO
        
        # Generate the layout for this model
        treeviewcolumn = Gtk.TreeViewColumn(filename)
        self.treeView.append_column(treeviewcolumn)
        cellrenderertext = Gtk.CellRendererText()
        treeviewcolumn.pack_start(cellrenderertext, False)
        treeviewcolumn.add_attribute(cellrenderertext, "text", 0)
        
        self.treeView.set_model(self.treeStore)
        self.treeView.expand_all()
        
        # Connect button-press-event to its handler
        self.treeView.connect("button-press-event", self.on_treeview_button_press_event)
       
    def on_treeview_button_press_event(self, treeview, event):
        """Handle TreeView interactions"""
        layout_clicked = False
        x = int(event.x)
        y = int(event.y)
        time = event.time
        pthinfo = treeview.get_path_at_pos(x, y)
        if pthinfo is not None:
            path, col, cellx, celly = pthinfo
            treeview.grab_focus()
            treeview.set_cursor(path, col, 0)
            # Get label, but only if it's a layout
            treeiter = self.treeStore.get_iter(path)
            if self.treeStore.is_ancestor(self.layouts, treeiter):
                layout_clicked = True
                self.layout_name = self.treeStore.get_value(treeiter, 0)
                self.treeiter = treeiter
                
        # If left clicking, load graph
        if layout_clicked and event.button == 1:
            self.load_layout(self.layout_name)
        # If right clicking
        elif layout_clicked and event.button == 3:
            self.treeView_menu.popup(None, None, None, None, event.button, event.time)
        return True
        
    def on_treeView_menu_load_button_handler(self, menu_item):
        """Right-click menu "Load" button handler"""
        self.load_layout(self.layout_name)

    def on_treeView_menu_delete_button_handler(self, menu_item):
        """Right-click menu "Delete" button handler"""
        self.delete_layout(self.layout_name)
    
    def clear_treeStore(self) :
        """Clear TreeStore and TreeViewColumns"""
        self.treeStore = Gtk.TreeStore(str)
        for column in self.treeView.get_columns():
            self.treeView.remove_column(column)
        
    def activate_widget(self, widgetName):
        """Set widgetName to sensitive"""
        self.builder.get_object(widgetName).set_sensitive(True)
        
    def deactivate_widget(self, widgetName):
        """Set widgetName to insensitive"""
        self.builder.get_object(widgetName).set_sensitive(False)
        
    def reset_buttons(self):
        """Reset all buttons to default state"""
        self.graphWidget.re_init()
        self.activate_widget("save_layout_button")
        self.activate_widget("save_menu")
        self.activate_widget("exportPDF_menu")
        self.activate_widget("layoutMenu")    
        
    def update_statusbar(self, message):
        """Update statusbar with message"""
        self.statusBar.pop(0)
        self.statusBar.push(0, message)
    
    def load_layout(self, layout_name):
        """Load graph layout from layout_name corresponding .graphml file"""
        filename = os.path.join(os.getcwd(), 'saved_layouts',
                                os.path.basename(os.path.splitext(self.filename)[0]),
                                layout_name + '.graphml')
        try:
            g = load_graph(filename, fmt="xml")
            self.clear_graph()
            self.display_graph(g, layout=True)
            self.update_statusbar("Layout " + layout_name + " loaded successfully.")
            self.layout_name = layout_name
            self.reset_buttons()
        except Exception as e:
            logging.exception(e)
    
    def delete_layout(self, layout_name):
        """Delete layout_name corresponding .graphml file"""
        filename = os.path.join(os.getcwd(), 'saved_layouts',
                                os.path.basename(os.path.splitext(self.filename)[0]),
                                layout_name + '.graphml')
        try:
            os.remove(filename)
            try:
                os.rmdir(os.path.split(filename)[0])
            except OSError:
                pass # Directory not empty, pass
            self.update_statusbar("Layout " + layout_name + " deleted successfully.")
            self.treeStore.remove(self.treeiter)
            del self.layoutList[layout_name]
        except Exception as e:
            logging.exception(e)
