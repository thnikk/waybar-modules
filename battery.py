#!/usr/bin/python3
# Module for getting combined battery percentage for a supplied argument.
# For example, running the script with the argument BAT would combine
# BAT0 and BAT1 if you're using a laptop with multiple batteries.
import os
import json
import argparse

# Path to all battery devices
device_path = "/sys/class/power_supply"

# Parse arguments for device
parser = argparse.ArgumentParser(description="Combined battery module")
parser.add_argument('name', action='store',
                    type=str, help='Part of device name to search for')
args = parser.parse_args()

# Combined levels and capacities
all_full = 0
all_now = 0

# Output tooltip
tooltip = ""


# Function to get percentage from level and capacity values
def get_percentage(now, full):
    return int((now / full) * 100)


# Iterate through all power supply devices
for device in os.listdir(device_path):
    # If the device is supplied as an argument
    if args.name[0] in device:
        # Get values
        device_full = int(open(
            device_path + "/" + device + "/energy_full").read())
        device_now = int(open(
            device_path + "/" + device + "/energy_now").read())
        # Add values to max
        all_full += device_full
        all_now += device_now
        # Get devices percentage
        device_percent = get_percentage(device_now, device_full)
        # Append individual battery percentage
        tooltip += device + ": " + str(device_percent) + "\n"

# Get combined battery percentage
all_percent = get_percentage(all_now, all_full)
# Set an icon for the combined percentage
if all_percent > 80:
    icon = " "
elif all_percent > 60:
    icon = " "
elif all_percent > 40:
    icon = " "
elif all_percent > 20:
    icon = " "
else:
    icon = " "

# Print json output
print(json.dumps({"text": icon + str(all_percent) + "%",
                  "tooltip": tooltip.rstrip()}))
