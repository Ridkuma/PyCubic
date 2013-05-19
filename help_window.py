from gi.repository import Gtk

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
