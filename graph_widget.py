#-*- coding:utf-8 -*-
"""Custom GraphWidget implementation

Display the graph using GTK and handle graph modifications and save.
Call cub2g6.py for G6 file format save.

"""

import os
import logging
import tempfile
from graph_tool.all import *
import cub2g6

class GraphWidget(graph_tool.draw.GraphWidget):
    """GTK widget displaying a graph.
    
    Inherit from graph_tool.draw.GraphWidget.
    
    """

    def __init__(self, instance, g, pos=None, layout=None) :
        """GraphWidget creation"""
        if pos == None:
            super(GraphWidget, self).__init__(g, layout, update_layout = False)
        else:
            super(GraphWidget, self).__init__(g, pos, update_layout = False)
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
        self.rollbackEdge = None
    
    def button_press_event(self, widget, event):
        """Implement Theta operations"""
        # Desactivate Layout Changing (or the prop map pointers will go nuts)
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
                    self.rollbackEdge = (self.firstPick, self.secondPick)
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
                        self.re_init()
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
                    self.re_init()
                    self.instance.update_statusbar("Done.")
        
        # Default behaviour, inherited    
        else : 
            super(GraphWidget, self).button_press_event(widget, event)
            self.instance.update_statusbar("Ready.")
    
    def theta_clicked(self):
        """Set Theta state"""
        self.instance.deactivate_widget("theta_button")
        self.instance.deactivate_widget("thetaMinus_button")
        self.instance.activate_widget("cancel_button")
        self.theta = True
    
    def thetaMinus_clicked(self): 
        """Set ThetaMinus state"""     
        self.instance.deactivate_widget("theta_button")
        self.instance.deactivate_widget("thetaMinus_button")
        self.instance.activate_widget("cancel_button")
        self.thetaMinus = True
      
    def reactivate_operations(self):
        """Reset buttons to original state"""
        self.instance.activate_widget("theta_button")
        self.instance.activate_widget("thetaMinus_button")
        self.instance.deactivate_widget("cancel_button")
        
    def cancel_operations(self):
        """Cancel all current operations"""
        if self.newVertex1 != None :
            self.g.clear_vertex(self.newVertex1)
            self.g.remove_vertex(self.newVertex1)
        if self.rollbackEdge != None :
            self.g.add_edge(self.rollbackEdge[0], self.rollbackEdge[1])
        self.re_init()
        
    def re_init(self) :
        """Reinitialize widget"""
        self.reactivate_operations()
        self.theta = False
        self.thetaMinus = False
        self.firstPick = None
        self.secondPick = None
        self.newVertex1 = None
        self.newVertex2 = None
        self.rollbackEdge = None
        
    def set_to_modified(self):
        """Set graph state to "modified" to avoid problems"""
        self.modified = True
        filename = self.instance.filename
        name, ext = os.path.splitext(os.path.basename(filename))
        name += "-new" + ext
        self.instance.filename = os.path.join(os.path.dirname(filename), name)
        self.instance.clear_treeStore()
        self.instance.build_treeStore()
        
            
    def change_default_layout(self, algo):
        """Dynamically change the graph layout using algo
        
        Arguments:
        algo -- string of ['random', 'sfdp', 'arf', 'fruchter']
        
        """
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
        
    def to_cub(self, f):
        """Save current graph to CUB format in file object f"""
        g = self.g.copy() # local copy of the graph
        g.purge_vertices() # purge hidden vertices
        
        f.write(str(g.num_vertices()) + '\n')
        for v in g.vertices():
            line = str(g.vertex_index[v])
            for neighbour in v.all_neighbours():
                line += '\t' + str(g.vertex_index[neighbour])
            f.write(line + '\n')
            
        self.modified = False

    def to_g6(self, f):
        """Save current graph to G6 format in file object f"""
        temp_file = tempfile.NamedTemporaryFile()
        self.to_cub(temp_file)
        temp_file.seek(0)
        cub2g6._convert(temp_file, f)
        temp_file.close()
        self.modified = False
        
    def to_graphml(self, filename):
        """Save current graph to GraphML format in file f"""
        g = self.g.copy() # local copy of the graph
        g.purge_vertices() # purge hidden vertices
        self.g.vp["layout"] = self.pos
        self.g.save(filename, "xml")           
        self.modified = False
        
    # Export self.g to filename
    def export(self, filename, quality):
        """Export current graph to PDF/PS/SVG/PNG depending of filename and quality
        
        Arguments:
        filename -- string, where to export the graph
        quality -- tuple of integers, quality of the export
        
        """
        g = self.g.copy() # local copy of the graph
        g.purge_vertices() # purge hidden vertices
        graph_draw(g, pos=self.pos, output=filename, output_size=quality)
        
    def save_layout(self, layout_name):
        """Save current layout to GraphML format in file layout_name and update TreeView"""
        filename = os.path.join(os.getcwd(), 'saved_layouts',
                                os.path.basename(os.path.splitext(self.instance.filename)[0]),
                                layout_name + '.graphml')
        if not os.path.exists(os.path.split(filename)[0]):
            os.makedirs(os.path.split(filename)[0])
        try:
            self.g.vp["layout"] = self.pos
            self.g.save(str(filename), fmt="xml")
        except Exception as e:
            logging.exception(e)
        if not layout_name in self.instance.layoutList:
            self.instance.layoutList[layout_name] = filename
            treeiter = self.instance.treeStore.append(self.instance.layouts, [layout_name])
            self.instance.treeView.expand_to_path(self.instance.treeStore.get_path(treeiter))
        self.instance.update_statusbar("Layout " + layout_name + " saved successfully.")
