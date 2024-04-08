#!/usr/bin/python3 -u
"""
Description:
Author:
"""
import sys
from datetime import datetime
import inspect


def debug_print(msg):
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
