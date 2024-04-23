#!/usr/bin/python3 -u
"""
Description: Python GTK widgets
Author: thnikk
"""
import json
from subprocess import check_output
from datetime import datetime
import os
import sys
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell
import common as c


class Widget:
    """ Widget class"""
    def __init__(self):
        self.window = Gtk.Window()
        self.window.get_style_context().add_class('window')

    def css(self, file):
        """ Load CSS from file """
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(file)
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def weather(self, cache_file):
        """ Weather widget """

        widget = c.box('v', style='widget')

        with open(
            os.path.expanduser(cache_file), 'r', encoding='utf-8'
        ) as file:
            cache = json.loads(file.read())

        today = cache['Today']['info'][0]
        today_box = c.box('h', style='today-box')

        today_left = c.box('v')
        widget.add(c.label(cache['City'], style='city'))
        # temp_box = c.box('h')
        # temp_box.add(c.label(today['temperature'], 'temp-label'))
        # temp_box.add(c.label(today['icon'], 'temp-icon'))
        # today_left.add(temp_box)
        temp = c.label(
            f"{today['temperature']}° {today['icon']}", 'today-weather')
        today_left.add(temp)

        extra = c.h_lines([
            f" {today['humidity']}%",
            f" {today['wind']}mph",
        ], style='extra')
        today_left.add(extra)

        today_right = c.box('v')
        today_right.pack_start(c.v_lines([
            today['description'],
            f"Feels like {today['feels_like']}°",
            f"{today['quality']} air quality"
        ], right=True), True, False, 0)

        today_box.pack_start(today_left, False, False, 0)

        # Add thing
        sun_box = c.box('v')

        try:
            sun_box.add(c.label(f' {today["sunset"]}pm', 'sun'))
        except KeyError:
            sun_box.add(c.label(f' {today["sunrise"]}am', 'sun'))
        today_box.pack_start(sun_box, False, False, 0)

        today_box.pack_end(today_right, False, False, 0)

        hourly_box = c.box('h', style='hourly-box')
        for hour in cache['Hourly']['info']:
            hour_box = c.box('v', style='hour-box')
            hour_box.add(c.label(f"{hour['temperature']}°"))
            hour_box.add(c.label(hour['icon'], style='icon-small'))
            hour_box.add(c.label(hour['time']))
            if hour != cache['Hourly']['info']:
                sep = Gtk.Separator.new(Gtk.Orientation.VERTICAL)
                hourly_box.add(sep)
            hourly_box.pack_start(hour_box, True, False, 0)

        daily_box = c.box('v', style='daily-box')
        for day in cache['Daily']['info']:
            day_box = c.box('h', style='day-box')
            day_box.add(c.label(day['time']))
            day_box.pack_end(
                c.label(f"{day['high']}° / {day['low']}°"), False, False, 0)
            day_box.pack_end(
                c.label(day['icon']), False, False, 100)
            if day != cache['Daily']['info']:
                sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
                daily_box.add(sep)
            daily_box.add(day_box)

        widget.add(today_box)

        heading_box = c.box('h')
        heading_box.add(c.label('Hourly forecast', style='title'))
        widget.add(heading_box)

        widget.add(hourly_box)

        heading_box = c.box('h')
        heading_box.add(c.label('5-day forecast', style='title'))
        widget.add(heading_box)

        widget.add(daily_box)

        self.window.add(widget)

    def start(self):
        """ Start bar """
        GtkLayerShell.init_for_window(self.window)

        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.BOTTOM, 1)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.RIGHT, 1)

        GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.BOTTOM, 0)
        GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.RIGHT, 0)

        GtkLayerShell.set_namespace(self.window, 'widget')

        self.window.show_all()
        self.window.connect('destroy', Gtk.main_quit)
        Gtk.main()


def main():
    """ Test """
    widget = Widget()
    css_path = "/".join(__file__.split('/')[:-1]) + '/style.css'
    try:
        widget.css(css_path)
    except gi.repository.GLib.GError:
        pass
    widget.weather('~/.cache/weather-widget.json')
    widget.start()


if __name__ == "__main__":
    main()
