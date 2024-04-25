#!/usr/bin/python3 -u
"""
Description: Python GTK widgets
Author: thnikk
"""
import json
from subprocess import check_output
from datetime import datetime
import calendar
import os
import sys
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
    def __init__(self, monitor=None):
        self.window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.window.get_style_context().add_class('window')
        self.monitor = monitor

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

        sun_box = c.box('v')
        try:
            sun_box.add(c.label(f' {today["sunset"]}pm', 'sun'))
        except KeyError:
            sun_box.add(c.label(f' {today["sunrise"]}am', 'sun'))
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

        try:
            with open(
                os.path.expanduser('~/.config/calendar-events.json'),
                'r', encoding='utf-8'
            ) as file:
                events = json.loads(file.read())
        except FileNotFoundError:
            events = {
                "4/3": "UFO sighting",
                "4/21": "Dentist appointment",
                "4/28": "Birthday"
            }

        for count, month in enumerate([last_month, current_month, next_month]):
            for week in month:
                for day, styles in week:
                    if count == 1 and day == now.day:
                        styles.append('today')
                    date = (
                        f"{diff_month(now.year, now.month, count - 1)[1]}"
                        f"/{day}"
                    )
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

        for offset, month in enumerate(['Last', 'This', 'Next']):
            month_events = {
                date: event for date, event in events.items()
                if date.split('/', maxsplit=1)[0] == str(
                    diff_month(now.year, now.month, offset-1)[1])
            }

            if month_events:
                event_section = c.box('v', spacing=10)
                event_line = c.box('h')
                event_line.add(c.label(f'{month} month'))
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
