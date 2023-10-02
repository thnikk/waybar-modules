#!/usr/bin/python3
# Waybar module for use with xdrip+ using the web service API
# Shows sgv on bar and time since last received value and delta in the tooltip

import requests
import json
from datetime import datetime
import sys
import os
import pytz
import configparser

# Define config location
config_file = os.path.expanduser("~/.config/beetus.ini")
# Check for config file and create one if it doesn't exist
if not os.path.exists(config_file):
    f = open(config_file, "a")
    f.write("[settings]\napi_secret = \nip = \nport = ")
    f.close()

# Load config
config = configparser.ConfigParser()
config.read(config_file)

# Check if values are empty
if not config['settings']['api_secret'] or not config['settings']['api_secret'] or not config['settings']['api_secret']:
    print('{"text": "Set API key and IP+port in ~/.config/beetus.ini" }')
    exit(0)

# Build header for http request with api key
h = { "api-secret": config['settings']['api_secret']}
try:
    # Get response as json
    data = requests.get("http://{}:{}/sgv.json".format(config['settings']['ip'],config['settings']['port']), headers=h, timeout=3).json()
    # Write to cache file
    with open(cache_file) as cache:
        cache.write(json.dumps(data, indent=4))
except:
    # If there's an issue, use the cache file
    cache_file = os.path.expanduser("~/.cache/beetus.json")
    with open(cache_file) as cache:
        data = json.load(cache)

# Create variables for easier management
sgv = data[0]["sgv"]
delta = data[0]["delta"]
direction = data[0]["direction"]
date = datetime.strptime(data[0]["dateString"], "%Y-%m-%dT%H:%M:%S.%f%z")
now = datetime.now(pytz.utc)

# Calculate minutes since last check
since_last = int((now - date).total_seconds() / 60 )

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
out_dict={}

# Set "text" output (what normally shows up on the bar)
if since_last > 5:
    # Change color if stale value
    out_dict["text"]=" <span color='#ffffff33'>{} {}</span>".format(sgv, arrows[direction])
else:
    out_dict["text"]=" {} {}".format(sgv, arrows[direction])

# Set tooltip text
if since_last == 1:
    # Change text to minute if 1 minute
    out_dict["tooltip"] = "{} minute ago\ndelta: {}".format(since_last, delta)
elif since_last > 5:
    # Change color for stale value
    out_dict["tooltip"] = "<span color='#bf616a'>{} minutes ago</span>\ndelta: {}".format(since_last, delta)
else:
    # Otherwise print normal text
    out_dict["tooltip"] = "{} minutes ago\ndelta: {}".format(since_last, delta)

# Print output
print(json.dumps(out_dict))
