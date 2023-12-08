#!/usr/bin/python3
# Weather module for waybar using open-meteo
import requests
import json
from datetime import datetime
import os.path
import configparser

config_file = os.path.expanduser("~/.config/weather.ini")
# Check for config file and create one if it doesn't exist
if not os.path.exists(config_file):
    f = open(config_file, "a")
    f.write("[settings]\nzip = \nnight_icons = true\nhourly_hours = ")
    f.close()

# Get config file
config = configparser.ConfigParser()
config.read(config_file)

# Prompt user for zip code
postal_code = config["settings"]["zip"]
if not postal_code:
    print(json.dumps({"text": "Set zip code in ~/.config/weather.ini"}))
    exit()

# Icon and text for weather codes
weather_lookup = {
    "0":  ["", "Clear"],
    "1":  ["", "Mostly clear"],
    "2":  ["", "Partly cloudy"],
    "3":  ["", "Overcast"],
    "45": ["", "Fog"],
    "48": ["", "Depositing rime fog"],
    "51": ["", "Light drizzle"],
    "53": ["", "Moderate drizzle"],
    "55": ["", "Dense drizzle"],
    "56": ["", "Light freezing drizzle"],
    "57": ["", "Dense freezing drizzle"],
    "61": ["", "Slight rain"],
    "63": ["", "Moderate rain"],
    "65": ["", "Heavy rain"],
    "66": ["", "Light freezing rain"],
    "67": ["", "Heavy freezing rain"],
    "71": ["", "Slight snow"],
    "73": ["", "Moderate snow"],
    "75": ["", "Heavy snow"],
    "77": ["", "Snow grains"],
    "80": ["", "Slight rain showers"],
    "81": ["", "Moderate rain showers"],
    "82": ["", "Violent rain showers"],
    "85": ["", "Slight snow showers"],
    "86": ["", "Heavy snow showers"],
    "95": ["", "Thunderstorm"],
    "96": ["", "Slight hailing thunderstorm"],
    "99": ["", "Heavy hailing thunderstorm"]
}

# Get current time
now = datetime.now()
hour = int(now.strftime('%H'))
date = now.strftime('%Y-%m-%d')


def updateCache(url, file, today):
    try:
        # Get the modify date of the file
        date_modified = datetime.fromtimestamp(
            os.path.getmtime(file)).strftime('%Y-%m-%d')
    except FileNotFoundError:
        pass
    # Check if the file exists and if the date modified is today
    if os.path.exists(file) and (date == date_modified or today is False):
        with open(file) as cache:
            data = json.load(cache)
    else:
        data = requests.get(url).json()
        with open(file, "w") as cache:
            cache.write(json.dumps(data, indent=4))
    return data


# Get latitude and longitude for given zip code
geocode_file = os.path.expanduser("~/.cache/geocode.json")
geocode_url = (
    "https://geocoding-api.open-meteo.com/v1/search?name="
    "{}&count=1&language=en&format=json").format(postal_code)

geocode = updateCache(geocode_url, geocode_file, False)

lat = str(geocode["results"][0]['latitude'])
lon = str(geocode["results"][0]['longitude'])
tz = geocode["results"][0]['timezone']
city = geocode["results"][0]['name']

# Get weather data
weather_file = os.path.expanduser("~/.cache/weather.json")
weather_url = (
    "https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}"
    "&hourly=temperature_2m,relativehumidity_2m,weathercode,windspeed_10m,"
    "winddirection_10m&daily=weathercode,temperature_2m_max,"
    "temperature_2m_min,sunrise,sunset&temperature_unit=fahrenheit"
    "&timezone={}").format(lat, lon, tz)

weather = updateCache(weather_url, weather_file, True)

# Get AQI if new day
pollution_file = os.path.expanduser("~/.cache/pollution.json")
pollution_url = (
    "https://air-quality-api.open-meteo.com/v1/air-quality?"
    "latitude={}&longitude={}&hourly=us_aqi"
    "&timezone={}").format(lat, lon, tz)

pollution = updateCache(pollution_url, pollution_file, True)

# Print header for daily weather
tooltip = "<span color='#8fa1be' font_size='16pt'>Today</span>\n"


# Convert degrees to cardinal direction
def degToCompass(num):
    val = int((num/22.5)+.5)
    arr = ["N", "NNE", "NE", "ENE", "E", "ESE",  "SE",  "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return arr[(val % 16)]


# Get data for current hour
time_now = weather["hourly"]["time"][hour]
code_now = str(weather["hourly"]["weathercode"][hour])
temp_now = str(int(weather["hourly"]["temperature_2m"][hour]))
humidity_now = str(weather["hourly"]["relativehumidity_2m"][hour])
windspeed_now = str(weather["hourly"]["windspeed_10m"][hour])
winddirection_now = degToCompass(weather["hourly"]["winddirection_10m"][hour])
sunrise = int(datetime.strptime(
    weather["daily"]["sunrise"][0], "%Y-%m-%dT%H:%M").strftime("%H"))
sunset = int(datetime.strptime(
    weather["daily"]["sunset"][0], "%Y-%m-%dT%H:%M").strftime("%H"))
aqi = int(pollution["hourly"]["us_aqi"][hour])

# Air quality
if aqi <= 50:
    quality = "Good"
elif aqi <= 100:
    quality = "Moderate"
elif aqi <= 150:
    quality = "Unhealty"
elif aqi <= 200:
    quality = "Unhealthy"
elif aqi <= 300:
    quality = "Very unhealthy"
elif aqi <= 500:
    quality = "Hazardous"

# Add data to tooltip
tooltip += "City: {}\n".format(city)
tooltip += "Description: {}\n".format(weather_lookup[code_now][1])
tooltip += "Temperature: {}°F\n".format(temp_now)
tooltip += "Humidity: {}%\n".format(humidity_now)
tooltip += "Wind: {}mph {}\n".format(windspeed_now, winddirection_now)
tooltip += "Air quality: {}\n".format(quality)

# Next n hours
try:
    hourly_hours = int(config["settings"]["hourly_hours"])
    if hourly_hours > 0:
        tooltip += "\n<span color='#8fa1be' font_size='16pt'>Hourly forecast</span>\n"
        current_hour = now.strftime("%Y-%m-%dT%H:00")
        current_hour_index = weather["hourly"]["time"].index(current_hour)
        for i in range(current_hour_index, current_hour_index + hourly_hours):
            hour = datetime.strptime(weather["hourly"]["time"][i], "%Y-%m-%dT%H:%M")
            tooltip += "{}: {} {}\n".format(
                hour.strftime("%l%P"),
                weather["hourly"]["temperature_2m"][i],
                weather_lookup[str(weather["hourly"]["weathercode"][i])][1],
                )
except KeyError:
    tooltip += "\n<span color='#bf616a'>Please set hourly_hours\nin ~/.config/weather.ini</span>\n"

# Print header for weekly forecast
tooltip += "\n<span color='#8fa1be' font_size='16pt'>7 day forecast</span>\n"

# Split weekly data
for x in range(7):
    date = datetime.strptime(weather["daily"]["time"][x], "%Y-%m-%d")
    dow = date.strftime("%A")
    code = str(weather["daily"]["weathercode"][x])
    temp_max = str(int(weather["daily"]["temperature_2m_max"][x]))
    temp_min = str(int(weather["daily"]["temperature_2m_min"][x]))
    # Add formatted line to tooltip
    tooltip += "{}: {}/{} {}\n".format(
        dow[:2], temp_max, temp_min, weather_lookup[code][1])

# Get boolean from config if exists, otherwise enable night icons
try:
    night_icons = config.getboolean('settings', 'night_icons')
except (KeyError, configparser.NoOptionError):
    night_icons = 1
if night_icons == 1:
    # Change icon if night time
    if hour < sunrise or hour > sunset:
        weather_lookup["0"][0] = ""

# Print data formatted for waybar
print(json.dumps({"text": "{} {}°F".format(
    weather_lookup[code_now][0], temp_now), "tooltip": tooltip.rstrip()}))
