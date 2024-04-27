#!/usr/bin/python3 -u
"""
Description:
Author:
"""
from subprocess import Popen
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell


def scroll(width=-1, height=-1, style=None):
    """ Create scrollable window """
    window = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
    window.set_max_content_width(width)
    window.set_min_content_width(width)
    window.set_min_content_height(height)
    window.set_max_content_height(height)
    window.set_propagate_natural_width(True)
    window.set_shadow_type(Gtk.ShadowType.NONE)
    # window.set_overlay_scrolling(False)
    window.set_policy(
        hscrollbar_policy=Gtk.PolicyType.NEVER,
        vscrollbar_policy=Gtk.PolicyType.ALWAYS
    )
    if style:
        window.get_style_context().add_class(style)
    return window


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


def click_link(module, url):
    """ Click action """
    del module
    Popen(['xdg-open', url])


def button(input_text, style=None, url=None):
    """ Button """
    __button__ = Gtk.Button.new_with_label(input_text)
    if style:
        __button__.get_style_context().add_class(style)
    if url:
        __button__.connect('clicked', click_link, url)
    return __button__


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
