from gi.repository import Gtk
from graph_from_file import GraphFromFile
from help_window import HelpWindow
import os
import logging

class Handlers:

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

    # Main window delete handler
    def onDeleteWindow(self, *windows):
        Gtk.main_quit(*windows)
        
    ## BUTTON HANDLERS ##
    
    # Save layout button click handler
    def on_save_layout_button_clicked(self, button):
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
    
    # OpenCub Menu Item click handler
    def on_open_menu_activate(self, menuItem):
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
    
        
    # Save Menu Item click handler
    def on_save_menu_activate(self, menuItem):
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
    
    # Export Item click handler
    def on_export_menu_activate(self, menuItem):
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
                    
                    elif not valid:
                        try_again = True
                        self.info_dialog("Wrong file format", "Only PDF, PS, SVG and PNG files are currently supported for exporting.", filechooser)
                    
                except Exception as e:
                    logging.exception("Error {} while exporting {}".format(e, filename))
                
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
