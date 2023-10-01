#!/usr/bin/python3
import json
import jc 
import subprocess

# Get upower output through subprocess
upower_output = subprocess.check_output(['upower', '-d'], text=True)
# Format output for json
upower_json = jc.parse('upower', upower_output)

device_icons = {
    "mouse": "",
    "gaming-input": "",
    "headphones": "",
}

battery_icons = [ "","","","","" ]
battery_icon = ""

out_dict = {
    "text": "",
    "alt": "",
    "tooltip": "",
}

# Iterate through devices
for device in upower_json:
    # Check to see if the detail section exists for the device
    if 'detail' in device.keys():
        # Check to see if the percentage isn't 0
        if device['detail']['percentage'] != 0.0:
            # Get the type of device
            name = device['detail']['type']
            # Only pull percentage up to . or % (first 2 digits)
            percent = int(str(device['detail']['percentage']).split('.', 1)[0].split('%', 1)[0])

            # Get battery
            if percent >= 100:
                battery_icon = ""
            elif percent >= 75:
                battery_icon = ""
            elif percent >= 50:
                battery_icon = ""
            elif percent >= 25:
                battery_icon = ""
            else:
                battery_icon = "<span color=\"#bf616a\"></span>"

            out_dict["text"] = battery_icon
            out_dict["alt"] = out_dict["alt"] + device_icons[name] + " " + battery_icon + " "
            out_dict["tooltip"] = out_dict["tooltip"] + name + " " + str(percent) + "\n"

# Remove trailing delimeters
if out_dict["text"].endswith(" "):
    out_dict["text"] = out_dict["text"].rstrip(' ')
if out_dict["alt"].endswith(" "):
    out_dict["alt"] = out_dict["alt"].rstrip(' ')
if out_dict["tooltip"].endswith("\n"):
    out_dict["tooltip"] = out_dict["tooltip"].rstrip('\n')


print(json.dumps(out_dict))
            
                
