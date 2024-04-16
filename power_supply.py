#!/usr/bin/python3 -u
"""
Description:
Author:
"""
import glob
import json

devices = []

for path in glob.glob('/sys/class/power_supply/*'):
    with open(f'{path}/uevent', encoding='utf-8') as file:
        device = {}
        for line in file.read().splitlines():
            name = line.split('=')[0].split('_')[-1].lower()
            device[name] = line.split('=')[1]
        devices.append(device)

print(json.dumps(devices, indent=4))
