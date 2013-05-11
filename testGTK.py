#!/usr/bin/python
#-*- coding:utf-8 -*-

from gi.repository import Gtk
from graph_tool.all import *
import cub2graph, sys, logging, os


class PyCubic:

    def __init__(self):

        self.builder = Gtk.Builder()
        self.builder.add_from_file("PyCubic.glade")
        self.graphFrame = self.builder.get_object("graph_frame")
        self.treeView = self.builder.get_object("graph_treeview")
        
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
        self.treeStore = Gtk.TreeStore(str)
        for column in self.treeView.get_columns() :
            self.treeView.remove_column(column)
    
    # Prepare and fill the Tree Store  
    def build_treeStore(self, filename) :
        self.treeStore = Gtk.TreeStore(str)
    
        # Fill the Tree Store   
        self.layoutList = dict()
        layouts = self.treeStore.append(None, ["Saved layouts"])
        for root, dirs, files in os.walk(os.path.join(os.getcwd(), "saved_layouts", filename)) :
            for file in files :
                (name, ext) = os.path.splitext(file)
                if ext == ".layout" :
                    self.layoutList[name] = os.path.join(root,file)
                    self.treeStore.append(layouts, [name])
        pmatchings = self.treeStore.append(None, ["Perfect matchings"])
        self.treeStore.append(pmatchings, ["Unknown"])
        
        # Generate the layout for this model
        treeviewcolumn = Gtk.TreeViewColumn(filename)
        self.treeView.append_column(treeviewcolumn)
        cellrenderertext = Gtk.CellRendererText()
        treeviewcolumn.pack_start(cellrenderertext, False)
        treeviewcolumn.add_attribute(cellrenderertext, "text", 0)
        
        self.treeView.set_model(self.treeStore)
        
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
            print "Theta"
            self.init_picked()
            self.queue_draw()
            # Get first vertex picked
            if self.firstPick == None :
                self.firstPick = self.g.vertex(self.picked)
                self.picked = None
                print "First Pick"
            # Get second vertex picked
            elif self.secondPick == None :
                self.secondPick = self.g.vertex(self.picked)
                self.picked = None
                print "Second Pick"
                
                # Check if the picked vertices are neighbours
                edge = self.g.edge(self.firstPick, self.secondPick)
                if edge == None :
                    print "Incorrect edge selection"
                    self.cancel_operations()
                else :
                    # Insert new vertex between picked vertices
                    newVertex = self.g.add_vertex()
                    print "Vertex added"
                    self.g.add_edge(self.firstPick, newVertex)
                    self.g.add_edge(self.secondPick, newVertex)
                    self.g.remove_edge(edge)
                    if self.newVertex1 == None :
                        # Stock the new vertex, and wait for the second edge pick
                        self.newVertex1 = newVertex
                        self.firstPick = None
                        self.secondPick = None
                    else :
                        # Create the second new vertex
                        self.newVertex2 = newVertex
                        self.g.add_edge(self.newVertex1, self.newVertex2)
                        # Update graph widget
                        tempPos = random_layout(self.g)
                        self.pinned[self.newVertex1] = False
                        self.pinned[self.newVertex2] = False
                        self.pos[self.newVertex1] = tempPos[self.newVertex1]
                        self.pos[self.newVertex2] = tempPos[self.newVertex2]
                        newPos = sfdp_layout(self.g, pin = self.pinned, K = 0.1, pos = self.pos)
                        self.pos = newPos
                        self.vertex_matrix.add_vertex(self.newVertex1)
                        self.vertex_matrix.add_vertex(self.newVertex2)
                        self.regenerate_surface(lazy=False)
                        self.cancel_operations()
                        print "Fin Theta"
                
        # Theta Minus operation handler
        elif self.thetaMinus == True :
            self.init_picked()
            self.queue_draw()
            # Get first vertex picked
            if self.firstPick == None :
                self.firstPick = self.g.vertex(self.picked)
                self.picked = None
            # Get second vertex picked
            elif self.secondPick == None :
                self.secondPick = self.g.vertex(self.picked)
                self.picked = None
                
                # Check if the picked vertices are neighbours
                if self.g.edge(self.firstPick, self.secondPick) == None :
                    print "Incorrect edge selection"
                    self.cancel_operations()
                else :
                    # Create edges between neighbours
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
                    self.cancel_operations()
        
        # Default behaviour, inherited    
        else : 
            super(GraphWidgetCustom, self).button_press_event(widget, event)
    
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
        self.instance.deactivate_widget("theta_button")
        self.instance.deactivate_widget("thetaMinus_button")
        self.instance.deactivate_widget("cancel_button")
        self.instance.deactivate_widget("saveAs_menu")
        self.instance.deactivate_widget("exportPDF_menu")
        self.instance.deactivate_widget("layoutMenu")
   
    # Reset buttons when graph is loaded
    def reset_buttons(self):
        self.instance.graphWidget.cancel_operations()
        self.instance.activate_widget("saveAs_menu")
        self.instance.activate_widget("exportPDF_menu")
        self.instance.activate_widget("layoutMenu")

    # Snippet for one-liner info dialogs
    def info_dialog(self, title, message, dialog=None):
        info_dialog = Gtk.MessageDialog(dialog, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                                Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE,
                                                title)
        info_dialog.format_secondary_text(message)
        info_dialog.run()
        info_dialog.destroy()

    # Main window delete handler
    def onDeleteWindow(self, *windows):
        Gtk.main_quit(*windows)
        
    ## BUTTON HANDLERS ##
        
    # Theta button click handler
    def on_theta_button_clicked(self, button):
        print "Theta button clicked"
        # TODO Update the Status bar
        self.instance.graphWidget.theta_clicked()
            
        
    # ThetaMinus button click handler
    def on_thetaMinus_button_clicked(self, button):
        print "Theta Minus button clicked"
        # TODO Update the Status bar
        self.instance.graphWidget.thetaMinus_clicked()
        
    # Cancel button click handler
    def on_cancel_button_clicked(self, button):
        print "Cancel"
        self.instance.graphWidget.cancel_operations()
        

    # Help button click handler
    def on_help_button_clicked(self, button):
        self.helpWindow = HelpWindow()
        
    ## MENU HANDLERS ##
    
    # Filters for file selection in FileChooserDialog objects
    def add_filters(self, dialog):
        filter_cub = Gtk.FileFilter()
        filter_cub.set_name("Cub files")
        filter_cub.add_pattern("*.cub")
        dialog.add_filter(filter_cub)
        
        filter_graphml = Gtk.FileFilter()
        filter_graphml.set_name("GraphML files")
        filter_graphml.add_pattern("*.graphml")
        dialog.add_filter(filter_graphml)
    
    # OpenCub Menu Item click handler
    def on_open_menu_activate(self, menuItem):
        logging.debug("Opening a file")
        filechooser = Gtk.FileChooserDialog("Open a file", None, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(filechooser)
        response = filechooser.run()

        if response == Gtk.ResponseType.OK:
            filename = filechooser.get_filename()
            logging.debug("File chosen: {}".format(filename))
            
            (name, ext) = os.path.splitext(filename)
            try:
                if '.cub' in ext:
                    with open(filename) as f:
                        g = cub2graph._convert(f)
                elif '.graphml' in ext:
                    with open(filename) as f:
                        g = load_graph(f, "xml") # TODO: doesn't work
                        
                try:
                    self.instance.clear_graph() # Clear the graph
                except AttributeError:
                    pass # No graph loaded yet, just pass
                                       
                self.instance.display_graph(g)
                self.reset_buttons()
                self.instance.build_treeStore(os.path.splitext(os.path.basename(filename))[0])
            except Exception as e:
                logging.exception("Error {} while converting {}".format(e, filename))
                # This should not be needed since we filter openable files
                # But we keep it anyway just in case
                self.info_dialog("Wrong file format", "Only CUB and GraphML files are currently supported.", filechooser)
            
        elif response == Gtk.ResponseType.CANCEL:
            logging.debug("Cancelling")

        filechooser.destroy()
    
        
    # SaveAs Menu Item click handler
    def on_saveAs_menu_activate(self, menuItem):
        logging.debug("Saving to a file")
        filechooser = Gtk.FileChooserDialog("Save a file", None, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(filechooser)
        response = filechooser.run()

        if response == Gtk.ResponseType.OK:
            filename = filechooser.get_filename()
            logging.debug("File chosen: {}".format(filename))
            (name, ext) = os.path.splitext(filename)
            try:
                if '.cub' in ext:
                    with open(filename, 'w') as f:
                        self.instance.graphWidget.save2cub(f)
                elif '.graphml' in ext:
                    with open(filename, 'w') as f:
                        g = save_graph(f, "xml") # TODO: doesn't work
                        
            except Exception as e:
                logging.exception("Error {} while converting {}".format(e, filename))
                # This should not be needed since we filter save fileformats
                # But we keep it anyway just in case
                self.info_dialog("Wrong file format", "Only CUB and GraphML files are currently supported.", filechooser)
            
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


# Run the GUI
if __name__ == "__main__":
    instance = PyCubic()
    instance.builder.connect_signals(Handler(instance))
    Gtk.main()
