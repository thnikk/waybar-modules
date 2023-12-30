#!/usr/bin/python3
"""
Module for cyberpower UPS to show estimated power usage of system.
Author: thnikk
"""
import subprocess
import json
import argparse

parser = argparse.ArgumentParser(description="")
parser.add_argument('name', action='store',
                    type=int, help='Part of device name to search for')
args = parser.parse_args()

output = subprocess.run(
        ["pwrstat", "-status"],
        check=False,
        capture_output=True
        ).stdout.decode('utf-8').splitlines()

stats = {}

for line in output:
    if "." in line:
        key = line.split(".")[0].strip().lower().replace(" ", "-")
        value = line.split("..")[-1].strip(".").strip()
        stats[key] = value

LOAD = str(int(stats["load"].split(" ")[0]) - 126)
tooltip = "<span color='#8fa1be' font_size='16pt'>UPS stats</span>\n" + \
        "Remaining runtime: " + stats["remaining-runtime"] + "\n" + \
        "Load: " + stats["load"] + "\n" + \
        "Battery Capacity: " + stats["battery-capacity"]

print(json.dumps({"text": LOAD, "tooltip": tooltip}))
