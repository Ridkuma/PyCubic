#!/usr/bin/python
#-*- coding:utf-8 -*-

from gi.repository import Gtk
from graph_tool.all import *
import cub2g6, g62cub, tempfile, sys, logging, os, cPickle


class PyCubic:

    def __init__(self):

        self.builder = Gtk.Builder()
        self.builder.add_from_file("PyCubic.glade")
        self.graphFrame = self.builder.get_object("graph_frame")
        self.treeView = self.builder.get_object("graph_treeview")
        self.statusBar = self.builder.get_object("statusbar")
        self.update_statusbar("Welcome to PyCubic!")
        
    # Add the GraphWidget to display graph g
    def display_graph(self, g, layout = None):
        if layout == None :
            layout = sfdp_layout(g)
        self.graphWidget = GraphWidgetCustom(self, g, layout)
        self.graphWidget.show_all()
        self.graphFrame.add(self.graphWidget)
        
    # Clear the current graph
    def clear_graph(self) :
        self.graphWidget.destroy()
        self.graphWidget = None
        self.clear_treeStore()
    
    # Save layout to .layout file
    def save_layout(self, layout_name):
        filename = os.path.join(os.getcwd(), 'saved_layouts',
                                os.path.basename(os.path.splitext(self.filename)[0]),
                                layout_name + '.layout')
        if not os.path.exists(os.path.split(filename)[0]):
            os.makedirs(os.path.split(filename)[0])
        with open(filename, 'wb') as f:
            try:
                cPickle.dump(self.graphWidget, f)
            except Exception as e:
                logging.exception(e)
        if not layout_name in self.layoutList:
            self.layoutList[layout_name] = filename
            self.treeStore.append(self.layouts, [layout_name])
        
    # Load layout from .layout file
    def load_layout(self, layout_name):
        filename = os.path.join(os.getcwd(), 'saved_layouts',
                                os.path.basename(os.path.splitext(self.filename)[0]),
                                layout_name + '.layout')
        with open(filename, 'rb') as f:
            self.graphWidget = cPickle.load(f)
            
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
                if ext == ".layout" :
                    self.layoutList[name] = os.path.join(root, file)
                    self.treeStore.append(self.layouts, [name])
        pmatchings = self.treeStore.append(None, ["Perfect matchings"])
        self.treeStore.append(pmatchings, ["Unknown"])
        
        # Generate the layout for this model
        treeviewcolumn = Gtk.TreeViewColumn(filename)
        self.treeView.append_column(treeviewcolumn)
        cellrenderertext = Gtk.CellRendererText()
        treeviewcolumn.pack_start(cellrenderertext, False)
        treeviewcolumn.add_attribute(cellrenderertext, "text", 0)
        
        self.treeView.set_model(self.treeStore)
        self.treeView.expand_all()
    
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
        
    # Set the statusbar message to display
    def update_statusbar(self, message) :
        self.statusBar.pop(0)
        self.statusBar.push(0, message)
    
        
class GraphWidgetCustom(graph_tool.draw.GraphWidget):

    def __init__(self, instance, g, layout) :
        super(GraphWidgetCustom, self).__init__(g, layout, update_layout = False)
        self.instance = instance
        self.modified = False
        self.theta = False
        self.thetaMinus = False
        self.removed = self.g.new_vertex_property("bool")
        self.removed.a = False
        self.pinned = self.g.new_vertex_property("bool")
        self.pinned.a = True
        self.firstPick = None
        self.secondPick = None
        self.newVertex1 = None
        self.newVertex2 = None
    
    # Custom Button Press Event, implementing Theta operations
    def button_press_event(self, widget, event):
        # Desactivate Layout Changing (or the prop map pointers will derpyderp)
        self.instance.deactivate_widget("layoutMenu")
        
        # Theta operation handler
        if self.theta == True :
            self.init_picked()
            self.queue_draw()
            # Get first vertex picked
            if self.firstPick == None :
                self.firstPick = self.g.vertex(self.picked)
                self.picked = None
                self.instance.update_statusbar("Select a second vertex, which will define the picked edge.")
            # Get second vertex picked
            elif self.secondPick == None :
                self.secondPick = self.g.vertex(self.picked)
                self.picked = None
                
                # Check if the picked vertices are neighbours
                edge = self.g.edge(self.firstPick, self.secondPick)
                if edge == None :
                    logging.info("Incorrect edge selection")
                    self.instance.update_statusbar("Incorrect edge selection, cancelling operations...")
                    self.cancel_operations()
                else :
                    # Insert new vertex between picked vertices
                    newVertex = self.g.add_vertex()
                    self.g.add_edge(self.firstPick, newVertex)
                    self.g.add_edge(self.secondPick, newVertex)
                    self.g.remove_edge(edge)
                    if self.newVertex1 == None :
                        # Stock the new vertex, and wait for the second edge pick
                        self.newVertex1 = newVertex
                        self.instance.update_statusbar("First edge saved, pick a vertex for the second edge.")
                        self.firstPick = None
                        self.secondPick = None
                    else :
                        # Create the second new vertex
                        self.instance.update_statusbar("Applying Theta Operation...")
                        self.newVertex2 = newVertex
                        self.g.add_edge(self.newVertex1, self.newVertex2)
                        # Generate random position for new vertices
                        self.instance.update_statusbar("Updating objects' positions...")
                        tempPos = random_layout(self.g)
                        # Set these to 'moveable'
                        self.pinned[self.newVertex1] = False
                        self.pinned[self.newVertex2] = False
                        # Add new positions to the current layout
                        self.pos[self.newVertex1] = tempPos[self.newVertex1]
                        self.pos[self.newVertex2] = tempPos[self.newVertex2]
                        # Change the position to place these the best way possible
                        # without moving the other nodes
                        newPos = sfdp_layout(self.g, pin = self.pinned, K = 0.1, pos = self.pos)
                        self.pos = newPos
                        # Set them back to immutable
                        self.pinned[self.newVertex1] = True
                        self.pinned[self.newVertex2] = True
                        # Add them to the vertex matrix
                        self.vertex_matrix.add_vertex(self.newVertex1)
                        self.vertex_matrix.add_vertex(self.newVertex2)
                        # Update widget
                        self.instance.update_statusbar("Updating widget...")
                        self.regenerate_surface(lazy=False)
                        # End operation
                        if not self.modified : 
                            self.set_to_modified()
                        self.cancel_operations()
                        self.instance.update_statusbar("Done.")
                
        # Theta Minus operation handler
        elif self.thetaMinus == True :
            self.init_picked()
            self.queue_draw()
            # Get first vertex picked
            if self.firstPick == None :
                self.firstPick = self.g.vertex(self.picked)
                self.picked = None
                self.instance.update_statusbar("Select a second vertex, which will define the picked edge.")
            # Get second vertex picked
            elif self.secondPick == None :
                self.secondPick = self.g.vertex(self.picked)
                self.picked = None
                
                # Check if the picked vertices are neighbours
                if self.g.edge(self.firstPick, self.secondPick) == None :
                    logging.info("Incorrect edge selection")
                    self.instance.update_statusbar("Incorrect edge selection, cancelling operations...")
                    self.cancel_operations()
                else :
                    # Create edges between neighbours
                    self.instance.update_statusbar("Applying ThetaMinus operation...")
                    neighbours = [self.g.vertex_index[v] for v in self.firstPick.all_neighbours()]
                    neighbours.remove(int(self.secondPick))
                    self.g.add_edge(neighbours[0], neighbours[1])
                    neighbours = [self.g.vertex_index[v] for v in self.secondPick.all_neighbours()]
                    neighbours.remove(int(self.firstPick))
                    self.g.add_edge(neighbours[0], neighbours[1])
                    # Remove all edges from picked vertices
                    self.g.clear_vertex(self.firstPick)
                    self.g.clear_vertex(self.secondPick)
                    # Remove picked vertices
                    self.selected.fa = False
                    self.queue_draw()
                    # Update the "removed" filter
                    self.instance.update_statusbar("Updating widget...")
                    self.removed[self.firstPick] = True
                    self.removed[self.secondPick] = True
                    # Update the widget's vertex matrix
                    self.vertex_matrix.remove_vertex(self.firstPick)
                    self.vertex_matrix.remove_vertex(self.secondPick)
                    # Apply the filter
                    self.g.set_vertex_filter(self.removed, inverted=True)
                    # Update graph display
                    self.regenerate_surface(lazy=False)
                    self.queue_draw()
                    # End
                    if not self.modified :
                        self.set_to_modified()
                    self.cancel_operations()
                    self.instance.update_statusbar("Done.")
        
        # Default behaviour, inherited    
        else : 
            super(GraphWidgetCustom, self).button_press_event(widget, event)
            self.instance.update_statusbar("Ready.")
    
    # Theta clicked
    def theta_clicked(self):
        self.instance.deactivate_widget("theta_button")
        self.instance.deactivate_widget("thetaMinus_button")
        self.instance.activate_widget("cancel_button")
        self.theta = True
    
    # ThetaMinus clicked
    def thetaMinus_clicked(self):      
        self.instance.deactivate_widget("theta_button")
        self.instance.deactivate_widget("thetaMinus_button")
        self.instance.activate_widget("cancel_button")
        self.thetaMinus = True
      
          
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
        self.newVertex1 = None
        self.newVertex2 = None
        
    # Change parameters if the graph has been modified
    def set_to_modified(self):
        self.modified = True
        filename = self.instance.filename
        name, ext = os.path.splitext(os.path.basename(filename))
        name += "-new" + ext
        self.instance.filename = os.path.join(os.path.dirname(filename), name)
        self.instance.clear_treeStore()
        self.instance.build_treeStore()
        
            
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
        self.instance.update_statusbar(algo.capitalize() + " layout applied.")
        
    # Convert self.g to CUB format in Python File Object f
    def save2cub(self, f):
        g = self.g.copy() # local copy of the graph
        g.purge_vertices() # purge hidden vertices
        
        f.write(str(g.num_vertices()) + '\n')
        for v in g.vertices():
            line = str(g.vertex_index[v])
            for neighbour in v.all_neighbours():
                line += '\t' + str(g.vertex_index[neighbour])
            f.write(line + '\n')
            
        self.modified = False
        
    # Convert self.g to G6 format in Python File Object f
    def save2g6(self, f):
        temp_file = tempfile.NamedTemporaryFile()
        self.save2cub(temp_file)
        temp_file.seek(0)
        cub2g6._convert(temp_file, f)
        temp_file.close()
        self.modified = False

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

    def __init__(self, instance) :
        self.instance = instance
        # Deactivate all necessary buttons until a graph is loaded
        self.instance.deactivate_widget("save_layout_button")
        self.instance.deactivate_widget("theta_button")
        self.instance.deactivate_widget("thetaMinus_button")
        self.instance.deactivate_widget("cancel_button")
        self.instance.deactivate_widget("save_menu")
        self.instance.deactivate_widget("exportPDF_menu")
        self.instance.deactivate_widget("layoutMenu")
   
    # Reset buttons when graph is loaded
    def reset_buttons(self):
        self.instance.graphWidget.cancel_operations()
        self.instance.activate_widget("save_layout_button")
        self.instance.activate_widget("save_menu")
        self.instance.activate_widget("exportPDF_menu")
        self.instance.activate_widget("layoutMenu")

    # Snippet for one-liner info dialogs
    def info_dialog(self, title, message, parent=None):
        info_dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                                Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE,
                                                title)
        info_dialog.format_secondary_text(message)
        info_dialog.run()
        info_dialog.destroy()

    # Snipper for one-liner input dialog
    def input_dialog(self, title, default_input="", parent=None):
        """Display a dialog with a text entry. Return the text, or None if canceled."""
        input_dialog = Gtk.MessageDialog(parent,
                              Gtk.DialogFlags.DESTROY_WITH_PARENT,
                              Gtk.MessageType.OTHER,
                              Gtk.ButtonsType.OK_CANCEL,
                              title)
        entry = Gtk.Entry()
        entry.set_text(default_input)
        entry.show()
        input_dialog.vbox.pack_end(entry, True, True, 0)
        entry.connect('activate', lambda _: input_dialog.response(Gtk.ResponseType.OK))
        input_dialog.set_default_response(Gtk.ResponseType.OK)

        response = input_dialog.run()
        text = entry.get_text().decode('utf8')
        input_dialog.destroy()
        if response == Gtk.ResponseType.OK:
            return text
        else:
            return None

    # Main window delete handler
    def onDeleteWindow(self, *windows):
        Gtk.main_quit(*windows)
        
    ## BUTTON HANDLERS ##
    
    # Save layout button click handler
    def on_save_layout_button_clicked(self, button):
        layout_name = self.input_dialog("Choose layout name",
                                        default_input="awesome_snark",
                                        parent=instance.builder.get_object("MainWindow"))
        if layout_name != None:
            layout_name = layout_name.strip().replace(' ', '_')
            if layout_name != '':
                self.instance.save_layout(layout_name)
                # TODO refresh saved layout list
            else:
                self.info_dialog("Error", "Invalid name", parent=instance.builder.get_object("MainWindow"))
        
    # Theta button click handler
    def on_theta_button_clicked(self, button):
        logging.debug("Theta button clicked")
        self.instance.update_statusbar("Theta operation. Please pick a vertex.")
        self.instance.graphWidget.theta_clicked()
            
        
    # ThetaMinus button click handler
    def on_thetaMinus_button_clicked(self, button):
        logging.debug("Theta Minus button clicked")
        self.instance.update_statusbar("ThetaMinus operation. Please pick a vertex.")
        self.instance.graphWidget.thetaMinus_clicked()
        
    # Cancel button click handler
    def on_cancel_button_clicked(self, button):
        logging.debug("Cancel")
        self.instance.update_statusbar("Operations cancelled.")
        self.instance.graphWidget.cancel_operations()
        

    # Help button click handler
    def on_help_button_clicked(self, button):
        self.helpWindow = HelpWindow()
        
    ## MENU HANDLERS ##
    
    # Filters for file selection in FileChooserDialog objects
    def add_filters(self, dialog):
        filter_graph = Gtk.FileFilter()
        filter_graph.set_name("CUB or G6 files")
        filter_graph.add_pattern("*.cub")
        filter_graph.add_pattern("*.g6")
        dialog.add_filter(filter_graph)
    
        filter_cub = Gtk.FileFilter()
        filter_cub.set_name("CUB files")
        filter_cub.add_pattern("*.cub")
        dialog.add_filter(filter_cub)
        
        filter_g6 = Gtk.FileFilter()
        filter_g6.set_name("G6 files")
        filter_g6.add_pattern("*.g6")
        dialog.add_filter(filter_g6)
    
    # OpenCub Menu Item click handler
    def on_open_menu_activate(self, menuItem):
        logging.debug("Opening a file")
        filechooser = Gtk.FileChooserDialog("Open a file", None, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(filechooser)
        response = filechooser.run()

        if response == Gtk.ResponseType.OK:
            filename = filechooser.get_filename()
            self.instance.filename = filename
            logging.debug("File chosen: {}".format(filename))
            
            (name, ext) = os.path.splitext(filename)
            try:
                if '.cub' in ext:
                    with open(filename, 'rb') as f:
                        g = GraphFromFile.from_cub(f)
                elif '.g6' in ext:
                    with open(filename, 'rb') as f:
                        g = GraphFromFile.from_g6(f)
                else:
                    self.info_dialog("Wrong file format", "Only CUB and G6 files are currently supported.", filechooser)
                        
                try:
                    self.instance.clear_graph() # Clear the graph
                except AttributeError:
                    pass # No graph loaded yet, just pass
                                       
                self.instance.display_graph(g)
                self.instance.filename = filename
                self.reset_buttons()
                self.instance.update_statusbar("File " + os.path.basename(filename) + " loaded successfully.")
                self.instance.build_treeStore()
            except Exception as e:
                logging.exception("Error {} while converting {}".format(e, filename))
            
        elif response == Gtk.ResponseType.CANCEL:
            logging.debug("Cancelling")

        filechooser.destroy()
    
        
    # Save Menu Item click handler
    def on_save_menu_activate(self, menuItem):
        logging.debug("Saving to a file")
        filechooser = Gtk.FileChooserDialog("Save a file", None, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        filechooser.set_do_overwrite_confirmation(True)
        filechooser.set_filename(self.instance.filename)
        filechooser.set_current_name(os.path.basename(self.instance.filename))

        self.add_filters(filechooser)
        
        try_again = True
        while try_again:
            try_again = False
            response = filechooser.run()

            if response == Gtk.ResponseType.OK:
                filename = filechooser.get_filename()
                logging.debug("File chosen: {}".format(filename))
                (name, ext) = os.path.splitext(filename)
                try:
                    if '.cub' in ext:
                        with open(filename, 'wb') as f:
                            self.instance.graphWidget.save2cub(f)
                            self.instance.update_statusbar("File " + os.path.basename(filename) + " saved successfully.")
                    elif '.g6' in ext:
                        with open(filename, 'wb') as f:
                             self.instance.graphWidget.save2g6(f)
                             self.instance.update_statusbar("File " + os.path.basename(filename) + " saved successfully.")
                    else:
                        try_again = True
                        self.info_dialog("Wrong file format", "Only CUB and G6 files are currently supported.", filechooser)
                            
                except Exception as e:
                    logging.exception("Error {} while converting {}".format(e, filename))
                
            elif response == Gtk.ResponseType.CANCEL:
                logging.debug("Cancelling")

        filechooser.destroy()
    
    # Quit Menu Item click handler
    def on_quit_menu_activate(self, menuItem):
        Gtk.main_quit(menuItem)
        
    # Random Layout Menu click handler
    def on_random_menu_activate(self, menuItem):
        self.instance.graphWidget.change_default_layout("random")
        
    # SFDP Layout Menu click handler
    def on_sfdp_menu_activate(self, menuItem):
        self.instance.graphWidget.change_default_layout("sfdp")
        
    # ARF Layout Menu click handler
    def on_arf_menu_activate(self, menuItem):
        self.instance.graphWidget.change_default_layout("arf")
        
    # Fruchter Layout Menu click handler
    def on_fruchter_menu_activate(self, menuItem):
        self.instance.graphWidget.change_default_layout("fruchter")
        
    # About Menu Item click handler
    def on_about_menu_activate(self, menuItem):
        self.aboutdialog = self.instance.builder.get_object("about_dialog")
        self.aboutdialog.run()
        self.aboutdialog.hide()


class GraphFromFile:
    @classmethod
    def from_cub(self, cub_file):
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
                graph_dict[end_node].remove(start_node)
                graph.add_edge(graph.vertex(start_node), graph.vertex(end_node))
             
        return graph

    @classmethod
    def from_g6(self, g6_file):
        """Convert a G6 Python File Object and return a graph-tool Graph Object"""
        temp_file = tempfile.NamedTemporaryFile()
        g62cub._convert(g6_file, temp_file)
        temp_file.seek(0)
        graph = self.from_cub(temp_file)
        temp_file.close()
        return graph

# Run the GUI
if __name__ == "__main__":
    instance = PyCubic()
    instance.builder.connect_signals(Handler(instance))
    Gtk.main()
