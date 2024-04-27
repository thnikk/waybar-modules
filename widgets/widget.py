#!/usr/bin/python3 -u
"""
Description: Python GTK widgets
Author: thnikk
"""
import json
from subprocess import check_output
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell


class Widget:
    """ Widget class"""
    def __init__(self, monitor=None):
        self.window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.window.get_style_context().add_class('window')
        self.monitor = monitor
        css_path = "/".join(__file__.split('/')[:-1]) + '/style.css'
        self.css(css_path)

    def css(self, file):
        """ Load CSS from file """
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(file)
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def add(self, box):
        self.window.add(box)

    def start(self):
        """ Start bar """
        GtkLayerShell.init_for_window(self.window)

        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.BOTTOM, 1)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.RIGHT, 1)

        GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.BOTTOM, 10)
        GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.RIGHT, 10)

        GtkLayerShell.set_namespace(self.window, 'widget')

        try:
            if not self.monitor:
                raise ValueError

            monitors = [
                info['name'] for info in
                json.loads(check_output(["swaymsg", "-t", "get_outputs"]))
            ]

            display = Gdk.Display.get_default()
            GtkLayerShell.set_monitor(
                self.window,
                Gdk.Display.get_monitor(display, monitors.index(self.monitor))
            )
        except ValueError:
            pass

        self.window.show_all()
        self.window.connect('destroy', Gtk.main_quit)
        Gtk.main()
