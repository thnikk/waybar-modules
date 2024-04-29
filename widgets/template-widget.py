#!/usr/bin/python3 -u
"""
Description: Template widget
Author: thnikk
"""
import argparse
from widget import Widget
import common as c


def parse_args() -> argparse.ArgumentParser:
    """ Parse arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=str)
    parser.add_argument('-p', '--position', type=str)
    return parser.parse_args()


def test_widget():
    """ Simple test widget """
    main_box = c.box('v', style='widget', spacing=20)
    main_box.add(c.label('Test widget', style='heading'))

    return main_box


def main():
    """ Main function """
    args = parse_args()
    widget = Widget(args.output, args.position)
    widget.window.add(test_widget())
    widget.start()


if __name__ == "__main__":
    main()
