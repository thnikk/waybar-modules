#!/usr/bin/python3
# Weather module for waybar using the less open OpenWeatherMap
import requests
import json
import os
import configparser
from datetime import datetime

config_file = os.path.expanduser("~/.config/pyweather.ini")
cache_file = os.path.expanduser("~/.cache/pyweather.json")

# Check for config file and create one if it doesn't exist
if not os.path.exists(config_file):
    print("Config not found, creating in", config_file)
    f = open(config_file, "a")
    # Example config
    default = """[settings]
# openweathermap api key
api_key = 
zip = 
country_code = 
"""
    f.write(default)
    f.close()
    print("Please set API key")
    exit(1)

# Get config file
config = configparser.ConfigParser()
config.read(config_file)

# Icon dictionary
icons = {
    "Sun": "",
    "Cloud": "",
    "Rain": "",
    "Snow": "",
    "Clear": "",
    # "Clear": "",
    "Overcast": "",
    "Haze": "",
    "Fog": "",
    "Mist": "",
}
# Default icon (if the description doesn't match anything in the dictionary)
icon = "?"

location = requests.get("http://api.openweathermap.org/geo/1.0/zip?zip=" + config["settings"]["zip"] + "," + config["settings"]["country_code"] + "&limit=1&appid=" + config["settings"]["api_key"]).json()
lat = str(location["lat"])
lon = str(location["lon"])

# Get info
r = requests.get("http://api.openweathermap.org/data/2.5/weather?lat=" + lat + "&lon=" + lon + "&units=imperial&appid=" + config["settings"]["api_key"])
with open(cache_file, "w") as json_file:
        # print("Updating cache file.")
        json_file.write(json.dumps(r.json(), indent=4))
        

# print(json.dumps(r.json()))
# exit(0)

# Get temperature and convert to int to remove decimal point
temp = int(r.json()["main"]["temp"])
# Get description
desc = r.json()["weather"][0]["main"]
# Get city
city = r.json()["name"]

# Look for matching icon
for key in icons:
    if key.lower() in desc.lower():
        icon = icons[key]

# Get pollution
aqi = requests.get("http://api.openweathermap.org/data/2.5/air_pollution?lat=" + lat + "&lon=" + lon + "&units=imperial&appid=" + config["settings"]["api_key"]).json()["list"][0]["main"]["aqi"] - 1
quality = [ "Good", "Fair", "Moderate", "Poor", "Very poor" ]

# Output dictionary
out_dict = {}
# Normal output
out_dict["text"] = icon + " " + str(temp) + "°F"

out_dict["tooltip"] = "<span color='#8fa1be' font='Nunito Bold 16'>" + r.json()["name"] + "</span>\n"
tooltip = {
    # "City": r.json()["name"],
    "Temperature": str(temp) + "°F",
    "Peaks": str(int(r.json()["main"]["temp_max"])) + "/" + str(int(r.json()["main"]["temp_min"])),
    "Description": r.json()["weather"][0]["description"].capitalize(),
    "Wind speed": str(r.json()["wind"]["speed"]) + " MPH",
    "Humidity": str(r.json()["main"]["humidity"]) + "%",
    "Air quality": quality[aqi],
}

for key, value in tooltip.items():
    out_dict["tooltip"] += key + ": " + value + "\n" 


# Get 5 day forecast
forecasts = requests.get("http://api.openweathermap.org/data/2.5/forecast?lat=" + lat + "&lon=" + lon + "&units=imperial&appid=" + config["settings"]["api_key"]).json()

# Set header for tooltip
out_dict["tooltip"] = out_dict["tooltip"] + "\n<span color='#8fa1be' font='Nunito Bold 16'>5 day forecast</span>\n"
# Today's peaks
# out_dict["tooltip"] = out_dict["tooltip"] + "Today: " + str(int(r.json()["main"]["temp_max"])) + "/" + str(int(r.json()["main"]["temp_min"])) + "\n"

# Separate 3 hour forecast into days
output = {}
for forecast in forecasts["list"]:
    date = forecast["dt_txt"].split(" ")[0]
    if date not in output.keys():
        output[date] = {"temp": [], "description": []}
    output[date]["temp"].append(int(forecast["main"]["temp"]))
    output[date]["description"].append(forecast["weather"][0]["main"])

# print(output)
# exit(0)

# Get high/low and day of week for each day
tooltip = ""
for date,info in output.items():
    dow = datetime.strptime(date, "%Y-%m-%d").strftime('%A')
    avg_dsc = max(set(info["description"]), key=info["description"].count)
    out_dict["tooltip"] += dow + ": " + avg_dsc + " " + str(max(info["temp"])) + "/" + str(min(info["temp"])) + "\n"

# Strip last newline off tooltip
out_dict["tooltip"] = out_dict["tooltip"].rstrip("\n")

# Print the whole thing as json
print(json.dumps(out_dict))
