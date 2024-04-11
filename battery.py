#!/usr/bin/python3
"""
Description: Module for getting combined battery percentages.
Author: thnikk
"""
from glob import glob
import sys
import json
import argparse


def parse_args():
    """ Parse arguments"""
    parser = argparse.ArgumentParser(description="Combined battery module")
    parser.add_argument('-n', '--name',
                        type=str, help='Part of device name to search for')
    return parser.parse_args()


# Function to get percentage from level and capacity values
def get_percentage(now, full):
    """ Calculate percentage from current and max values """
    return int((now / full) * 100)


def main():
    """ Main function """
    all_full = 0
    all_now = 0
    tooltip = []

    args = parse_args()

    # Iterate through all power supply devices
    for device in glob('/sys/class/power_supply/*'):
        # If the device is supplied as an argument
        if args.name and args.name in device:
            continue
        try:
            # Get values
            with open(
                f"{device}/energy_full", 'r', encoding='utf-8'
            ) as file:
                device_full = int(file.read())
            with open(
                f"{device}/energy_now", 'r', encoding='utf-8'
            ) as file:
                device_now = int(file.read())
        except FileNotFoundError:
            continue
        # Add values to max
        all_full += device_full
        all_now += device_now
        # Get devices percentage
        device_percent = get_percentage(device_now, device_full)
        # Append individual battery percentage
        tooltip.append(f"{device}: {str(device_percent)}")

    if not all_full:
        print("No batteries found.")
        sys.exit(1)

    # Get combined battery percentage
    all_percent = get_percentage(all_now, all_full)
    icons = [" ", " ", " ", " ", " "]
    icon = icons[all_percent // 25]

    # Print json output
    print(json.dumps({"text": icon + str(all_percent) + "%",
                      "tooltip": "\n".join(tooltip)}))


if __name__ == "__main__":
    main()
