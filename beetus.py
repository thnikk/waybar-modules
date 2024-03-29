#!/usr/bin/python3
"""
Waybar module for use with xdrip+ using the web service API
Shows sgv on bar and time since last received value and delta in the tooltip
Author: thnikk
"""
import json
from datetime import datetime
import os
import configparser
import sys
import pytz
import requests

# Define config location
config_file = os.path.expanduser("~/.config/beetus.ini")
# Check for config file and create one if it doesn't exist
if not os.path.exists(config_file):
    with open(config_file, "a", encoding='utf-8') as f:
        f.write("[settings]\napi_secret = \nip = \nport = ")
        f.close()

# Load config
config = configparser.ConfigParser()
config.read(config_file)

# Check if values are empty
if not config['settings']['api_secret'] \
        or not config['settings']['api_secret'] \
        or not config['settings']['api_secret']:
    print('{"text": "Set API key and IP+port in ~/.config/beetus.ini" }')
    sys.exit(0)

# Build header for http request with api key
h = {"api-secret": config['settings']['api_secret']}
cache_file = os.path.expanduser("~/.cache/beetus.json")
try:
    # Get response as json
    data = requests.get((f"http://{config['settings']['ip']}:"
                        f"{config['settings']['port']}/sgv.json"),
                        headers=h, timeout=3).json()
    # Write to cache file
    with open(cache_file, "w", encoding='utf-8') as cache:
        cache.write(json.dumps(data, indent=4))
except:
    # If there's an issue, use the cache file
    with open(cache_file, encoding='utf-8') as cache:
        data = json.load(cache)

# Create variables for easier management
sgv = data[0]["sgv"]
delta = data[0]["delta"]
direction = data[0]["direction"]
date = datetime.strptime(data[0]["dateString"], "%Y-%m-%dT%H:%M:%S.%f%z")
now = datetime.now(pytz.utc)

# Calculate minutes since last check
since_last = int((now - date).total_seconds() / 60)

# Dictionary lookup for arrow icons
arrows = {
    "DoubleUp": "↑↑",
    "SingleUp": "↑",
    "FortyFiveUp": "↗️",
    "Flat": "→",
    "FortyFiveDown": "↘️",
    "SingleDown": "↓",
    "DoubleDown": "↓↓"
}

# Main output dictionary
out_dict = {}

# Set "text" output (what normally shows up on the bar)
if since_last > 5:
    # Change color if stale value
    out_dict["text"] = (f" <span color='#ffffff33'>{sgv} "
                        f"{arrows[direction]}</span>")
else:
    out_dict["text"] = f" {sgv} {arrows[direction]}"

# Set tooltip text
if since_last == 1:
    # Change text to minute if 1 minute
    out_dict["tooltip"] = f"{since_last} minute ago\ndelta: {delta}"
elif since_last > 5:
    # Change color for stale value
    out_dict["tooltip"] = (f"<span color='#bf616a'>{since_last} minutes ago"
                           f"</span>\ndelta: {delta}")
else:
    # Otherwise print normal text
    out_dict["tooltip"] = f"{since_last} minutes ago\ndelta: {delta}"

# Print output
print(json.dumps(out_dict))
