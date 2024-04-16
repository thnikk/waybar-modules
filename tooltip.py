#!/usr/bin/python3 -u
"""
Description: Waybar tooltip library
Author: thnikk
"""


def colorize(text, color_alias) -> str:
    """ Colorize text """
    colors = {
        "red": "#bf616a",
        "blue": "8fa1be",
        "green": "a3be8c",
        "orange": "#d08770",
        "purple": "#b48ead",
        "yellow": "#ebcb8b",
    }
    try:
        color = colors[color_alias]
    except KeyError:
        color = color_alias
    return f'<span color="{color}">{text}</span>'
