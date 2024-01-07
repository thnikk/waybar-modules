#!/usr/bin/python3
"""
Module for cyberpower UPS to show estimated power usage of system.
Author: thnikk
"""
import subprocess
import json
import argparse

# Get argument for offset
parser = argparse.ArgumentParser(description="")
parser.add_argument('-o', action='store',
                    type=int, help='Wattage offset to apply to normal value')
args = parser.parse_args()

# Only apply offset if argument is given
try:
    OFFSET = args.offset
except AttributeError:
    OFFSET = 0

# Get command output and split into lines
pwrstat = subprocess.run(
        ["pwrstat", "-status"],
        check=False,
        capture_output=True
        ).stdout.decode('utf-8').splitlines()

# Create empty dict for stats
stats = {}

# Parse info line by line from output
for line in pwrstat:
    if "." in line:
        key = line.split(".")[0].strip().lower().replace(" ", "-")
        value = line.split("..")[-1].strip(".").strip()
        stats[key] = value

# Get int for load and apply offset
LOAD = int(stats["load"].split(" ")[0]) - OFFSET

# Create tooltip
tooltip = "<span color='#8fa1be' font_size='16pt'>UPS stats</span>\n" + \
        "Remaining runtime: " + stats["remaining-runtime"] + "\n" + \
        "Load: " + stats["load"] + "\n" + \
        "Battery Capacity: " + stats["battery-capacity"]

# Create output dict and load with info
output = {
    "text": f"{LOAD}",
    "tooltip": f"{tooltip}",
}

# Apply class if load is high
if LOAD > 800:
    output["class"] = "hi-alert"

# Print output
print(json.dumps(output))
