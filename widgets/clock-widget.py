#!/usr/bin/python3 -u
"""
Description: Python GTK widgets
Author: thnikk
"""
import json
from subprocess import check_output
from datetime import datetime, timedelta
import os
import sys
import calendar
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell
import common as c


def diff_month(year, month, diff):
    """ Find year and month difference """
    if diff < 0 and month == 1:
        month = 12 - (diff + 1)
        year = year - 1
    elif diff > 0 and month == 12:
        month = 1 + (diff - 1)
        year = year + 1
    else:
        month = month + diff
    return year, month


def cal_list(year, month, style=None):
    """ Get calendar list for month and append style to boxes """
    cal = calendar.Calendar(6)
    return [
        [
            [day, [style]] for day in month
            if day
        ]
        for month in
        cal.monthdayscalendar(year, month)
    ]


def event_lookup(event):
    """ Get style for event """
    event_types = {
        "birthday": "blue",
        "appointment": "orange",
    }

    for event_type, style in event_types.items():
        if event_type in event.lower():
            return style
    return "green"


class Widget:
    """ Widget class"""
    def __init__(self):
        self.window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.window.get_style_context().add_class('window')

    def css(self, file):
        """ Load CSS from file """
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(file)
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def calendar(self):
        """ Draw calendar """
        widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        widget.get_style_context().add_class("widget")

        now = datetime.now()

        cal_section = c.box('v')
        month_label = c.label(now.strftime('%B'), style='month-label')
        cal_section.add(month_label)

        # Create calendar box
        row = c.box('h', spacing=10)
        for dow in ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]:
            dow_label = c.label(dow, style='dow')
            row.add(dow_label)
        cal_box = c.box('v')
        cal_box.add(row)

        last_month = cal_list(*diff_month(now.year, now.month, -1), 'old')[-2:]
        current_month = cal_list(now.year, now.month)
        next_month = cal_list(*diff_month(now.year, now.month, 1), 'old')[:2]

        events = {
            "4/3": "UFO sighting",
            "4/21": "Dentist appointment",
            "4/28": "Birthday"
        }

        with open(
            os.path.expanduser('~/.config/calendar-events.json'),
            'r', encoding='utf-8'
        ) as file:
            events = json.loads(file.read())

        month_events = {
            date: event for date, event in events.items()
            if date.split('/', maxsplit=1)[0] == str(now.month)
        }

        for week in current_month:
            for day, styles in week:
                if day == now.day:
                    styles.append('today')
                date = f"{now.month}/{day}"
                if date in list(events):
                    event_style = event_lookup(events[date])
                    styles.append('event')
                    styles.append(event_style)

        combined_month = []
        if len(last_month[-1]) < 7:
            combined_month += last_month[:-1]
            combined_month += [last_month[-1] + current_month[0]]
            combined_month += current_month[1:]
        else:
            combined_month = last_month + current_month
        if len(next_month[0]) < 7:
            mixed_month = [combined_month[-1] + next_month[0]]
            del combined_month[-1]
            combined_month += mixed_month + next_month[1:]
        lines = c.box('v')
        for week in combined_month:
            line = c.box('h', spacing=10)
            for day, styles in week:
                day_label = c.label(day)
                for style in styles:
                    if style:
                        day_label.get_style_context().add_class(style)
                day_label.get_style_context().add_class('day')
                line.add(day_label)
            lines.add(line)

        cal_box.add(lines)
        cal_section.add(cal_box)
        widget.add(cal_section)

        if month_events:
            event_section = c.box('v', spacing=10)
            event_line = c.box('h')
            event_line.add(c.label('Events'))
            event_section.add(event_line)

            events_box = c.box('v', style='events-box')
            for date, event in month_events.items():
                event_box = c.box('h', style='event-box', spacing=10)
                event_dot = c.label('', style='event-dot')
                event_day = c.label(date, style='event-day')
                event_label = c.label(event)
                event_style = event_lookup(event)
                event_dot.get_style_context().add_class(event_style)
                event_box.pack_start(event_dot, False, True, 0)
                event_box.pack_start(event_day, False, True, 0)
                event_box.pack_start(event_label, False, True, 0)
                events_box.add(event_box)

                if day is not list(events)[-1]:
                    sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
                    events_box.add(sep)
            event_section.add(events_box)
            widget.add(event_section)

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
    widget.calendar()
    widget.start()


if __name__ == "__main__":
    main()
