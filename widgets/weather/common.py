#!/usr/bin/python3 -u
"""
Description:
Author:
"""
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell


def v_lines(lines, right=False, style=None) -> Gtk.Box:
    """ Takes list and returns GTK nested boxes """
    container = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL, spacing=0)
    if style:
        container.get_style_context().add_class(style)
    for line in lines:
        line_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        text = Gtk.Label()
        text.set_label(f'{line}')
        if right:
            line_box.pack_end(text, False, False, 0)
        else:
            line_box.pack_start(text, False, False, 0)
        container.pack_start(line_box, True, False, 0)
    return container


def h_lines(lines, style=None) -> Gtk.Box:
    """ Takes list and returns GTK nested boxes """
    container = Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    if style:
        container.get_style_context().add_class(style)
    for line in lines:
        text = Gtk.Label()
        text.set_label(f'{line}')
        container.pack_start(text, True, False, 0)
    return container


def box(orientation, spacing=0, style=None):
    """ Create box """
    if orientation == 'v':
        obox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=spacing)
    else:
        obox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing)
    if style:
        obox.get_style_context().add_class(style)
    return obox


def label(input_text, style=None):
    """ Create label """
    text = Gtk.Label()
    text.set_text(f'{input_text}')
    if style:
        text.get_style_context().add_class(style)
    return text


def iconify(dictionary, exclude=None, include=None):
    """ Create list and replace keys with icons """
    icons = {
        "temperature": "",
        "feels_like": "",
        "humidity": "",
        "wind": "",
        "quality": "",
        "sunrise": "",
        "sunset": "",
        "high": "",
        "low": ""
    }

    output = []
    for key, value in dictionary.items():
        if exclude:
            if key in exclude:
                continue
        if include:
            if key not in include:
                continue
        if key == 'time':
            output.append(value)
            continue
        try:
            output.append(f'{icons[key]} {value}')
        except KeyError:
            pass
    return output


def make_section(
    days, icon_class='icon-large', style='section-box'
) -> Gtk.Box:
    """ thing """
    section_box = box('h', 10, style)
    for day in days:
        day_box = box('v', 10, 'day-box')
        main_box = box('h', 20, 'main-box')
        main_box.add(label(day['icon'], icon_class))

        icon_list = iconify(
            day, exclude=['quality', 'sunset'])
        icon_lines = v_lines(icon_list)
        main_box.add(icon_lines)
        day_box.add(main_box)

        bottom_list = iconify(
            day, include=['quality', 'sunset'])
        bottom_lines = h_lines(bottom_list)
        day_box.add(bottom_lines)

        section_box.pack_start(day_box, True, False, 0)
        if day != days[-1]:
            sep = Gtk.Separator.new(Gtk.Orientation.VERTICAL)
            section_box.add(sep)

    return section_box
