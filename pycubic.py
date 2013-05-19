from gi.repository import Gtk
from graph_tool.all import *
from graph_widget import GraphWidget
import os
import logging

class PyCubic:

    def __init__(self):

        self.builder = Gtk.Builder()
        self.builder.add_from_file("PyCubic.glade")
        self.graphFrame = self.builder.get_object("graph_frame")
        self.treeView = self.builder.get_object("graph_treeview")
        self.statusBar = self.builder.get_object("statusbar")
        self.update_statusbar("Welcome to PyCubic!")
        self.treeView_menu = self.build_treeView_menu()
        
    # Add the GraphWidget to display graph g
    def display_graph(self, g, layout=None):
        if layout == None:
            self.graphWidget = GraphWidget(self, g, layout=sfdp_layout(g))
        elif layout != True:
            self.graphWidget = GraphWidget(self, g, layout=layout)
        # Custom layout, load it
        else:
            try:
                self.graphWidget = GraphWidget(self, g, pos=g.vp["layout"])
            except KeyError: # just in case custom layout is invalid
                self.graphWidget = GraphWidget(self, g, layout=sfdp_layout(g))
        self.graphWidget.show_all()
        self.graphFrame.add(self.graphWidget)
        
    # Clear the current graph
    def clear_graph(self) :
        self.graphWidget.destroy()
        self.graphWidget = None
    
    # Prepare the right click treeview menu
    def build_treeView_menu(self):
        treeView_menu = Gtk.Menu()
        for icon, label, handler in [(Gtk.STOCK_EXECUTE, "Load", self.on_treeView_menu_load_button_handler),
                               (Gtk.STOCK_DELETE, "Delete", self.on_treeView_menu_delete_button_handler)]:
            menu_item = Gtk.ImageMenuItem(icon)
            menu_item.set_label(label)
            treeView_menu.append(menu_item)
            menu_item.connect("activate", handler)
            menu_item.show()
        return treeView_menu
    
    # Prepare and fill the Tree Store  
    def build_treeStore(self) :
        filename = os.path.splitext(os.path.basename(self.filename))[0]
        self.treeStore = Gtk.TreeStore(str)
    
        # Fill the Tree Store   
        self.layoutList = dict()
        self.layouts = self.treeStore.append(None, ["Saved layouts"])
        for root, dirs, files in os.walk(os.path.join(os.getcwd(), "saved_layouts", filename)) :
            for file in files :
                (name, ext) = os.path.splitext(file)
                if ext == ".graphml" :
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
   
    # Button press event handler    
    def on_treeview_button_press_event(self, treeview, event):
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
        
    # Right click menu "Load" handler
    def on_treeView_menu_load_button_handler(self, menu_item):
        self.load_layout(self.layout_name)

    
    # Right click menu "Delete" handler
    def on_treeView_menu_delete_button_handler(self, menu_item):
        self.delete_layout(self.layout_name)
    
    # Clear the current TreeStore and TreeViewColumns
    def clear_treeStore(self) :    
        self.treeStore = Gtk.TreeStore(str)
        for column in self.treeView.get_columns() :
            self.treeView.remove_column(column)
        
    # Set a widget to sensitive
    def activate_widget(self, widgetName) :
        self.builder.get_object(widgetName).set_sensitive(True)
        
    # Set a widget to insensitive
    def deactivate_widget(self, widgetName) :
        self.builder.get_object(widgetName).set_sensitive(False)
        
    # Reset buttons when graph is loaded
    def reset_buttons(self):
        self.graphWidget.re_init()
        self.activate_widget("save_layout_button")
        self.activate_widget("save_menu")
        self.activate_widget("exportPDF_menu")
        self.activate_widget("layoutMenu")    
        
    # Set the statusbar message to display
    def update_statusbar(self, message):
        self.statusBar.pop(0)
        self.statusBar.push(0, message)
    
    # Load layout layout_name from .graphml file
    def load_layout(self, layout_name):
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
    
    # Delete layout layout_name
    def delete_layout(self, layout_name):
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
