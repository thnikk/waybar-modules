#!/usr/bin/python3 -u
"""
Description: Updates widget
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


def update_widget():
    """ Update widget """
    main_box = c.box('v', style='widget', spacing=20)
    label = c.label('Updates', style='heading')
    main_box.add(label)

    with open(
        os.path.expanduser('~/.cache/updates.json'), 'r', encoding='utf-8'
    ) as file:
        cache = json.loads(file.read())

    for manager, packages in cache.items():
        if not packages:
            continue
        manager_box = c.box('v', spacing=10)
        heading = c.label(manager, style='title', ha='start')
        manager_box.add(heading)
        packages_box = c.box('v', style='events-box')
        max_len = 12
        if len(packages) > max_len:
            packages = packages[:max_len-1] + [
                [f'{len(packages) - max_len} more...', '']]
        for package in packages:
            package_box = c.box('h', style='event-box', spacing=20)
            package_label = c.button(
                package[0], style='none',
                url=f'https://archlinux.org/packages/{package[0]}')
            package_box.pack_start(package_label, False, False, 0)
            package_box.pack_end(
                c.label(package[1], style='green'), False, False, 0)
            packages_box.add(package_box)
            if package != packages[-1]:
                packages_box.pack_start(c.sep('h'), 1, 1, 0)
        manager_box.add(packages_box)
        main_box.add(manager_box)

    return main_box


def main():
    """ Main function """
    args = parse_args()
    widget = Widget(args.output)
    widget.add(update_widget())
    widget.start()


if __name__ == "__main__":
    main()
