#!/usr/bin/python3 -u
"""
Description:
Author:
"""
import sys
from datetime import datetime
import inspect
import json


def print_debug(msg):
    """ Print debug message """
    # Get filename of program calling this function
    frame = inspect.stack()[1]
    name = frame[0].f_code.co_filename.split('/')[-1].split('.')[0]
    # Color the name using escape sequences
    colored_name = f"\033[38;5;3m{name}\033[0;0m"
    # Get the time in the same format as waybar
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    # Print the debug message
    print(f'[{timestamp}] [{colored_name}] {msg}', file=sys.stderr)


class Cache:
    """ Cache managment function """
    def __init__(self, cache_file):
        self.cache_file = cache_file

    def save(self, cache):
        """ Save cache to file """
        with open(self.cache_file, 'w', encoding='utf-8') as file:
            file.write(json.dumps(cache, indent=4))

    def load(self):
        """ Load cache from file """
        with open(self.cache_file, 'r', encoding='utf-8') as file:
            return json.loads(file.read())
