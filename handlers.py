#-*- coding:utf-8 -*-
"""GTK handlers connected to .glade file

Define all the handlers of objects integrated in the .glade architecture file.
Responsible for all the dialogs.

"""

import os
import logging
from gi.repository import Gtk
from graph_from_file import GraphFromFile

class Handlers:
    """Regroup the handlers connected to .glade"""

    def __init__(self, instance) :
        """Initialize the handlers and deactivate all necessary buttons
        
        Arguments:
        intance -- the PyCubic object to which the handler should be connected"""
        self.instance = instance
        # Deactivate all necessary buttons until a graph is loaded
        self.instance.deactivate_widget("save_layout_button")
        self.instance.deactivate_widget("theta_button")
        self.instance.deactivate_widget("thetaMinus_button")
        self.instance.deactivate_widget("cancel_button")
        self.instance.deactivate_widget("save_menu")
        self.instance.deactivate_widget("exportPDF_menu")
        self.instance.deactivate_widget("layoutMenu")

    # Snippet for one-liner info dialogs
    def info_dialog(self, title, message, parent=None, msg_type=Gtk.MessageType.WARNING):
        """info_dialog(self, title, message, parent=None, msg_type=Gtk.MessageType.WARNING)
        
        Display a dialog with title and message.
        
        Arguments:
        title -- string, the title of the dialog
        message -- string, the message of the dialog
        
        Keyword arguments:
        parent -- the GTK parent to which attach the dialog (default: None)
        msg_type -- the GTK.MessageType to use (default: Gtk.MessageType.WARNING)
        
        """
        info_dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                                msg_type, Gtk.ButtonsType.CLOSE,
                                                title)
        info_dialog.format_secondary_text(message)
        info_dialog.run()
        info_dialog.destroy()

    def input_dialog(self, title, default_input="", parent=None):
        """Display a dialog with message title. Return the text, or None if canceled.
        
        Arguments:
        title -- string, the title of the dialog
        
        Keyword arguments:
        default_input -- the default string in the entry box (default: "")
        parent -- the GTK parent to which attach the dialog (default: None)
        
        """
        input_dialog = Gtk.MessageDialog(parent,
                              Gtk.DialogFlags.MODAL,
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

    def onDeleteWindow(self, *windows):
        """Main window delete handler"""
        Gtk.main_quit(*windows)
        
    def on_save_layout_button_clicked(self, button):
        """Save layout button click handler"""
        try:
            default_input = self.instance.layout_name
        except AttributeError:
            default_input="awesome_snark"
        layout_name = self.input_dialog("Choose layout name",
                                        default_input,
                                        parent=self.instance.builder.get_object("MainWindow"))
        if layout_name != None:
            layout_name = layout_name.strip().replace(' ', '_')
            if layout_name != '':
                self.instance.graphWidget.save_layout(layout_name)
            else:
                self.info_dialog("Error", "Invalid name", parent=self.instance.builder.get_object("MainWindow"))
        
    def on_theta_button_clicked(self, button):
        """Theta button click handler"""
        logging.debug("Theta button clicked")
        self.instance.update_statusbar("Theta operation. Please pick a vertex.")
        self.instance.graphWidget.theta_clicked()
            
        
    def on_thetaMinus_button_clicked(self, button):
        """ThetaMinus button click handler"""
        logging.debug("Theta Minus button clicked")
        self.instance.update_statusbar("ThetaMinus operation. Please pick a vertex.")
        self.instance.graphWidget.thetaMinus_clicked()
        
    def on_cancel_button_clicked(self, button):
        """Cancel button click handler"""
        logging.debug("Cancel")
        self.instance.update_statusbar("Operations cancelled.")
        self.instance.graphWidget.cancel_operations()
        
    def on_help_button_clicked(self, button):
        """Help button click handler"""
        info_dialog = self.info_dialog("Graph manipulation shortcuts", """ 
        Select vertice: Left Click
        
        Unselect: Right Click
        
        Select multiple vertices: Maj + Left click dragging
        
        Move vertice: Left Click dragging
        
        Pan graph: Middle Click dragging / Ctrl + Left Click dragging
        
        Zoom (no vertice scaling): Mouse scroll
        
        Zoom (with vertice scaling): Maj + Mouse scroll
        
        Rotate: Ctrl + Mouse scroll
        """, msg_type=Gtk.MessageType.INFO)
        
    def add_filters(self, dialog):
        """Set CUB/G6/GraphML file filters for FileChooserDialog dialog
        
        Arguments:
        dialog - FileChooserDialog instance to which attach the filters
        
        """
        filter_graph = Gtk.FileFilter()
        filter_graph.set_name("CUB, G6 or GraphML files")
        filter_graph.add_pattern("*.cub")
        filter_graph.add_pattern("*.g6")
        filter_graph.add_pattern("*.graphml")
        dialog.add_filter(filter_graph)
    
        filter_cub = Gtk.FileFilter()
        filter_cub.set_name("CUB files")
        filter_cub.add_pattern("*.cub")
        dialog.add_filter(filter_cub)
        
        filter_g6 = Gtk.FileFilter()
        filter_g6.set_name("G6 files")
        filter_g6.add_pattern("*.g6")
        dialog.add_filter(filter_g6)
        
        filter_graphml = Gtk.FileFilter()
        filter_graphml.set_name("GraphML files")
        filter_graphml.add_pattern("*.graphml")
        dialog.add_filter(filter_graphml)

    def on_open_menu_activate(self, menuItem):
        """OpenCub Menu Item click handler"""
        logging.debug("Opening a file")
        filechooser = Gtk.FileChooserDialog("Open a file", None, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(filechooser)
        try:
            filechooser.set_current_folder(os.path.split(self.instance.filename)[0])
        except AttributeError:
            pass # first opening
        response = filechooser.run()

        if response == Gtk.ResponseType.OK:
            filename = filechooser.get_filename()
            self.instance.filename = filename
            logging.debug("File chosen: {}".format(filename))
            
            (name, ext) = os.path.splitext(filename)
            try:
                custom_layout = False
                if 'cub' in ext:
                    with open(filename, 'rb') as f:
                        g = GraphFromFile.from_cub(f)
                elif 'g6' in ext:
                    with open(filename, 'rb') as f:
                        g = GraphFromFile.from_g6(f)
                elif 'graphml' in ext:
                    g = load_graph(filename, "xml")
                    custom_layout = True
                else:
                    self.info_dialog("Wrong file format", "Only CUB, G6 and GraphML files are currently supported.", filechooser)
                        
                try:
                    self.instance.clear_graph() # Clear the graph
                    self.instance.clear_treeStore()
                except AttributeError:
                    pass # No graph loaded yet, just pass
                                       
                if custom_layout:
                    self.instance.display_graph(g, True)
                else:
                    self.instance.display_graph(g)
                self.instance.filename = filename
                self.instance.reset_buttons()
                self.instance.update_statusbar("File " + os.path.basename(filename) + " loaded successfully.")
                self.instance.build_treeStore()
            except Exception as e:
                logging.exception("Error {} while converting {}".format(e, filename))
            
        elif response == Gtk.ResponseType.CANCEL:
            logging.debug("Cancelling")

        filechooser.destroy()
    
    def on_save_menu_activate(self, menuItem):
        """Save Menu Item click handler"""
        logging.debug("Saving to a file")
        filechooser = Gtk.FileChooserDialog("Save a file", None, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        filechooser.set_do_overwrite_confirmation(True)
        filechooser.set_filename(self.instance.filename)
        filechooser.set_current_folder(os.path.split(self.instance.filename)[0])
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
                    if 'cub' in ext:
                        with open(filename, 'wb') as f:
                            self.instance.graphWidget.to_cub(f)
                    elif 'g6' in ext:
                        with open(filename, 'wb') as f:
                             self.instance.graphWidget.to_g6(f)
                    elif 'graphml' in ext:
                        self.instance.graphWidget.to_graphml(filename)
                    else:
                        try_again = True
                        self.info_dialog("Wrong file format", "Only CUB, G6 and GraphML files are currently supported.", filechooser)
                    
                    self.instance.filename = filename
                    self.instance.clear_treeStore()
                    self.instance.build_treeStore()
                    self.instance.update_statusbar("File " + os.path.basename(filename) + " saved successfully.")
                except Exception as e:
                    logging.exception("Error {} while converting {}".format(e, filename))
                
            elif response == Gtk.ResponseType.CANCEL:
                logging.debug("Cancelling")

        filechooser.destroy()
    
    def on_export_menu_activate(self, menuItem):
        """Export Menu Item click handler"""
        logging.debug("Exporting to a file")
        filechooser = Gtk.FileChooserDialog("Export graph", None, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        filechooser.set_do_overwrite_confirmation(True)
        filechooser.set_filename(os.path.splitext(self.instance.filename)[0] + '.pdf')
        filechooser.set_current_folder(os.path.split(self.instance.filename)[0])
        filechooser.set_current_name(os.path.splitext(os.path.basename(self.instance.filename))[0] + '.pdf')

        filter_all = Gtk.FileFilter()
        filter_all.set_name("PDF, PS, SVG or PNG files")
        filter_all.add_pattern("*.pdf")
        filter_all.add_pattern("*.ps")
        filter_all.add_pattern("*.svg")
        filter_all.add_pattern("*.png")
        filechooser.add_filter(filter_all)
        
        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name("PDF files")
        filter_pdf.add_pattern("*.pdf")
        filechooser.add_filter(filter_pdf)
        
        filter_ps = Gtk.FileFilter()
        filter_ps.set_name("PS files")
        filter_ps.add_pattern("*.ps")
        filechooser.add_filter(filter_ps)
        
        filter_svg = Gtk.FileFilter()
        filter_svg.set_name("SVG files")
        filter_svg.add_pattern("*.svg")
        filechooser.add_filter(filter_svg)
        
        filter_png = Gtk.FileFilter()
        filter_png.set_name("PNG files")
        filter_png.add_pattern("*.pdf")
        filechooser.add_filter(filter_png)
        
        saved = False
        try_again = True
        while try_again:
            try_again = False
            response = filechooser.run()

            if response == Gtk.ResponseType.OK:
                filename = filechooser.get_filename()
                logging.debug("File chosen: {}".format(filename))
                (name, ext) = os.path.splitext(filename)
                try:
                    valid = False
                    for check in ['pdf', 'ps', 'svg', 'png']:
                        if check in ext:
                            valid = True
                            ask_quality = True
                            while ask_quality:
                                ask_quality = False
                                quality = self.input_dialog("Export quality", default_input="600,600", parent=filechooser)
                                if quality != None:
                                    try:
                                        width, height = quality.strip().split(',')
                                        quality = (int(width), int(height))
                                        self.instance.graphWidget.export(filename, quality)
                                        self.instance.update_statusbar("Graph successfully exported to " + os.path.basename(filename) + "!")
                                        saved = True
                                    except ValueError:
                                        ask_quality = True
                                        self.info_dialog("Error", "Invalid input: must be formatted as \"Width,Height\" (integers)", parent=instance.builder.get_object("MainWindow"))
                    
                    if not saved:
                        try_again = True                    
                        if not valid:
                            self.info_dialog("Wrong file format", "Only PDF, PS, SVG and PNG files are currently supported for exporting.", filechooser)
                    
                except Exception as e:
                    logging.exception("Error {} while exporting {}".format(e, filename))
                
            elif response == Gtk.ResponseType.CANCEL:
                logging.debug("Cancelling")

        filechooser.destroy()

    def on_quit_menu_activate(self, menuItem):
        """Quit Menu Item click handler"""
        Gtk.main_quit(menuItem)
        
    def on_random_menu_activate(self, menuItem):
        """Random Layout Menu click handler"""
        self.instance.graphWidget.change_default_layout("random")

    def on_sfdp_menu_activate(self, menuItem):
        """SFDP Layout Menu click handler"""
        self.instance.graphWidget.change_default_layout("sfdp")

    def on_arf_menu_activate(self, menuItem):
        """ARF Layout Menu click handler"""
        self.instance.graphWidget.change_default_layout("arf")

    def on_fruchter_menu_activate(self, menuItem):
        """Fruchter Layout Menu click handler"""
        self.instance.graphWidget.change_default_layout("fruchter")

    def on_about_menu_activate(self, menuItem):
        """About Menu Item click handler"""
        self.aboutdialog = self.instance.builder.get_object("about_dialog")
        self.aboutdialog.run()
        self.aboutdialog.hide()
