#!/usr/bin/python3
# Gets CyberPower UPS info from pwrstat
import subprocess
import json

output = subprocess.run(["pwrstat", "-status"], check=False, capture_output=True).stdout.decode('utf-8').splitlines()

stats = {}

for line in output:
    if "." in line:
        key = line.split(".")[0].strip().lower().replace(" ","-")
        value = line.split("..")[-1].strip(".").strip()
        stats[key] = value

load = str( int(stats["load"].split(" ")[0]) - 126 )
tooltip = "<span color='#8fa1be' font_size='16pt'>UPS stats</span>\n" + \
        "Remaining runtime: " + stats["remaining-runtime"] + "\n" + \
        "Load: " + stats["load"] + "\n" + \
        "Battery Capacity: " + stats["battery-capacity"] 

print(json.dumps({"text": load, "tooltip": tooltip}))

