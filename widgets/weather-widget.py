#!/usr/bin/python3 -u
"""
Description: Weather widget
Author: thnikk
"""
import argparse
import json
import os
import gi
from widget import Widget
import common as c
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def parse_args() -> argparse.ArgumentParser:
    """ Parse arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=str)
    return parser.parse_args()


def weather_widget(window, cache_file):
    """ Weather widget """

    widget = c.box('v', style='widget', spacing=20)

    with open(
        os.path.expanduser(cache_file), 'r', encoding='utf-8'
    ) as file:
        cache = json.loads(file.read())

    today = cache['Today']['info'][0]
    today_box = c.box('h', style='today-box')

    today_left = c.box('v')
    widget.add(c.label(cache['City'], style='heading'))
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

    widget.add(today_box)

    hourly_container = c.box('v', spacing=10)
    hourly_container.add(c.label('Hourly forecast', style='title', ha="start"))
    hourly_box = c.box('h', style='hourly-box')
    for hour in cache['Hourly']['info']:
        hour_box = c.box('v', style='hour-box')
        hour_box.add(c.label(f"{hour['temperature']}°"))
        icon = c.label(hour['icon'], style='icon-small')
        icon.props.tooltip_text = hour['description']
        hour_box.add(icon)
        hour_box.add(c.label(hour['time']))
        if hour != cache['Hourly']['info']:
            sep = Gtk.Separator.new(Gtk.Orientation.VERTICAL)
            hourly_box.add(sep)
        hourly_box.pack_start(hour_box, True, False, 0)
    hourly_container.add(hourly_box)
    widget.add(hourly_container)

    daily_container = c.box('v', spacing=10)
    daily_container.add(c.label(
        'Daily forecast', style='title', ha='start'))
    daily_box = c.box('v', style='daily-box')
    for day in cache['Daily']['info']:
        day_box = c.box('h', style='day-box')
        day_box.add(c.label(day['time']))
        day_box.pack_end(
            c.label(f"{day['high']}° / {day['low']}°"), False, False, 0)
        icon = c.label(day['icon'])
        icon.props.tooltip_text = day['description']
        day_box.pack_end(icon, False, False, 100)
        if day != cache['Daily']['info']:
            sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
            daily_box.add(sep)
        daily_box.add(day_box)
    daily_container.add(daily_box)
    widget.add(daily_container)

    window.window.add(widget)


def main():
    """ Weather widget """
    args = parse_args()
    widget = Widget(args.output)
    weather_widget(widget, '~/.cache/weather-widget.json')
    widget.start()


if __name__ == "__main__":
    main()
