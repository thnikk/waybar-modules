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


def sep(orientation, style=None):
    """ Separator """
    if orientation == 'v':
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
    if orientation == 'h':
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    if style:
        separator.get_style_context().add_class(style)
    return separator


def label(input_text, style=None, va=None, ha=None, he=False, wrap=None):
    """ Create label """
    text = Gtk.Label()
    text.set_text(f'{input_text}')
    if style:
        text.get_style_context().add_class(style)

    options = {
        "fill": Gtk.Align.FILL, "start": Gtk.Align.START,
        "end": Gtk.Align.END, "center": Gtk.Align.CENTER
    }

    try:
        text.props.valign = options[va]
    except KeyError:
        pass

    try:
        text.props.halign = options[ha]
    except KeyError:
        pass
    if isinstance(he, bool):
        text.props.hexpand = he

    if isinstance(wrap, int):
        text.props.wrap = True
        text.set_max_width_chars(wrap)

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
