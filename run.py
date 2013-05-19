#!/usr/bin/python
#-*- coding:utf-8 -*-



from pycubic import PyCubic
from handlers import Handlers
from gi.repository import Gtk

# Run the GUI
if __name__ == "__main__":
    instance = PyCubic()
    instance.builder.connect_signals(Handlers(instance))
    Gtk.main()
