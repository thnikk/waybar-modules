#!/usr/bin/python3 -u
"""
Description: Genshin widget
Author: thnikk
"""
import argparse
import os
import json
from widget import Widget
import common as c


def parse_args() -> argparse.ArgumentParser:
    """ Parse arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=str)
    return parser.parse_args()


def hoyo_widget():
    """ Genshin widget """
    main_box = c.box('v', style='widget', spacing=20)
    label = c.label('Genshin Impact', style='heading')
    main_box.add(label)

    with open(
        os.path.expanduser('~/.cache/hoyo-stats.json'), 'r', encoding='utf-8'
    ) as file:
        cache = json.loads(file.read())['Genshin']

    # Top section
    top_box = c.box('h', spacing=20)
    top_box.pack_start(c.label(
        f" {cache['Resin']}", style='today-weather', va='fill', ha='start'),
        False, False, 0)
    right_box = c.box('v')
    for line in [
        f"{cache['Until next 40'].split(':')[0]} hours "
        f"{cache['Until next 40'].split(':')[1]} minutes",
        'until next 40 resin'
    ]:
        right_box.add(c.label(line, ha='end'))
    top_box.pack_end(right_box, False, False, 0)
    main_box.add(top_box)

    # Info section
    info_section = c.box('v', spacing=10)
    info_box = c.box('v', style='box')
    info = [
        [
            f" {cache['Dailies completed']}",
            f" {cache['Realm currency']}",
            f" {cache['Remaining boss discounts']}"
        ], [
            f" {cache['Abyss progress'].split()[0]}",
            f"{cache['Abyss progress'].split()[1][-1]} "
            f"{cache['Abyss progress'].split()[1][:-1]}"
        ]
    ]
    for line in info:
        info_line = c.box('h')
        for item in line:
            info_line.pack_start(
                c.label(item, style='inner_box'), True, False, 0)
            if item != line[-1]:
                info_line.add(c.sep('v'))
            info_box.add(info_line)
        if line != info[-1]:
            info_box.add(c.sep('h'))
    info_section.add(info_box)
    main_box.add(info_section)

    return main_box


def main():
    """ Weather widget """
    args = parse_args()
    widget = Widget(args.output)
    widget.add(hoyo_widget())
    widget.start()


if __name__ == "__main__":
    main()
