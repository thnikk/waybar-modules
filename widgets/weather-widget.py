#!/usr/bin/python3 -u
"""
Description:
Author:
"""
from widget import Widget
import argparse


def parse_args() -> argparse.ArgumentParser:
    """ Parse arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=str)
    return parser.parse_args()


def main():
    """ Weather widget """
    args = parse_args()
    widget = Widget(args.output)
    css_path = "/".join(__file__.split('/')[:-1]) + '/style.css'
    widget.css(css_path)
    widget.weather('~/.cache/weather-widget.json')
    widget.start()


if __name__ == "__main__":
    main()
