#!/usr/bin/python3
"""
Module for getting combined battery percentage for a supplied argument.
For example, running the script with the argument BAT would combine
BAT0 and BAT1 if you're using a laptop with multiple batteries.
Author: thnikk
"""
import os
import json
import argparse

# Path to all battery devices
DEV_PATH = "/sys/class/power_supply"

# Parse arguments for device
parser = argparse.ArgumentParser(description="Combined battery module")
parser.add_argument('name', action='store',
                    type=str, help='Part of device name to search for')
args = parser.parse_args()

# Combined levels and capacities
ALL_FULL = 0
ALL_NOW = 0

# Output tooltip
TOOLTIP = ""


# Function to get percentage from level and capacity values
def get_percentage(now, full):
    """ Calculate percentage from current and max values """
    return int((now / full) * 100)


# Iterate through all power supply devices
for device in os.listdir(DEV_PATH):
    # If the device is supplied as an argument
    if args.name[0] in device:
        # Get values
        device_full = int(open(
            DEV_PATH + "/" + device + "/energy_full", encoding='utf-8').read())
        device_now = int(open(
            DEV_PATH + "/" + device + "/energy_now", encoding='utf-8').read())
        # Add values to max
        ALL_FULL += device_full
        ALL_NOW += device_now
        # Get devices percentage
        device_percent = get_percentage(device_now, device_full)
        # Append individual battery percentage
        TOOLTIP += device + ": " + str(device_percent) + "\n"

# Get combined battery percentage
all_percent = get_percentage(ALL_NOW, ALL_FULL)
icons = [" ", " ", " ", " ", " "]
icon = icons[all_percent // 25]

# Print json output
print(json.dumps({"text": icon + str(all_percent) + "%",
                  "tooltip": TOOLTIP.rstrip()}))
