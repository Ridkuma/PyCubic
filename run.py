#!/usr/bin/python
#-*- coding:utf-8 -*-
"""PyCubic run script"""

from gi.repository import Gtk
from pycubic import PyCubic
from handlers import Handlers

# Run the GUI when called as main program
if __name__ == "__main__":
    instance = PyCubic()
    instance.builder.connect_signals(Handlers(instance))
    Gtk.main()
