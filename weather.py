#!/usr/bin/python3 -u
""" Weather module for waybar using open-meteo """
import json
from datetime import datetime
import os.path
import configparser
import sys
import requests

config_file = os.path.expanduser("~/.config/weather.ini")
# Check for config file and create one if it doesn't exist
if not os.path.exists(config_file):
    with open(config_file, "a", encoding='utf-8') as f:
        f.write("[settings]\nzip = \nnight_icons = true\nhourly_hours = ")
        f.close()

# Get config file
config = configparser.ConfigParser()
config.read(config_file)

# Prompt user for zip code
postal_code = config["settings"]["zip"]
if not postal_code:
    print(json.dumps({"text": "Set zip code in ~/.config/weather.ini"}))
    sys.exit(0)

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


def update_cache(url, file, today):
    """ Update cache file with json reponse from request """
    try:
        # Get the modify date of the file
        date_modified = datetime.fromtimestamp(
            os.path.getmtime(file)).strftime('%Y-%m-%d')
    except FileNotFoundError:
        date_modified = None
    # Check if the file exists and if the date modified is today
    if os.path.exists(file) and (date == date_modified or today is False):
        with open(file, encoding='utf-8') as cache:
            data = json.load(cache)
    else:
        data = requests.get(url, timeout=5).json()
        with open(file, "w", encoding='utf-8') as cache:
            cache.write(json.dumps(data, indent=4))
    return data


# Get latitude and longitude for given zip code
geocode_file = os.path.expanduser("~/.cache/geocode.json")
geocode_url = (
    "https://geocoding-api.open-meteo.com/v1/search?name="
    f"{postal_code}&count=1&language=en&format=json")

geocode = update_cache(geocode_url, geocode_file, False)

LAT = str(geocode["results"][0]['latitude'])
LON = str(geocode["results"][0]['longitude'])
tz = geocode["results"][0]['timezone']
city = geocode["results"][0]['name']

# Get weather data
weather_file = os.path.expanduser("~/.cache/weather.json")
weather_url = (
    f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
    "&hourly=temperature_2m,relativehumidity_2m,weathercode,windspeed_10m,"
    "winddirection_10m&daily=weathercode,temperature_2m_max,"
    "temperature_2m_min,sunrise,sunset,wind_speed_10m_max,"
    f"wind_direction_10m_dominant&temperature_unit=fahrenheit&timezone={tz}")

weather = update_cache(weather_url, weather_file, True)

# Get AQI if new day
pollution_file = os.path.expanduser("~/.cache/pollution.json")
pollution_url = (
    "https://air-quality-api.open-meteo.com/v1/air-quality?"
    f"latitude={LAT}&longitude={LON}&hourly=us_aqi"
    f"&timezone={tz}")

pollution = update_cache(pollution_url, pollution_file, True)

# Print header for daily weather
TOOLTIP = "<span color='#8fa1be' font_size='16pt'>Today</span>\n"


def deg_to_card(num):
    """ Convert degrees to cardinal direction """
    val = int((num/22.5)+.5)
    arr = ["N", "NNE", "NE", "ENE", "E", "ESE",  "SE",  "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return arr[(val % 16)]


def deg_to_ascii(deg) -> str:
    """ Convert degrees to ascii arrow """
    arrows = ["↑", "↗", "→", "↘", "↓", "↙", "←", "↖"]
    return arrows[round(int(deg)/45)]


# Get data for current hour
time_now = weather["hourly"]["time"][hour]
CODE_NOW = str(weather["hourly"]["weathercode"][hour])
TEMP_NOW = str(int(weather["hourly"]["temperature_2m"][hour]))
HUMIDITY_NOW = str(weather["hourly"]["relativehumidity_2m"][hour])
WINDSPEED_NOW = str(weather["hourly"]["windspeed_10m"][hour])
winddirection_now = deg_to_ascii(weather["hourly"]["winddirection_10m"][hour])
sunrise = int(datetime.strptime(
    weather["daily"]["sunrise"][0], "%Y-%m-%dT%H:%M").strftime("%H"))
sunset = int(datetime.strptime(
    weather["daily"]["sunset"][0], "%Y-%m-%dT%H:%M").strftime("%H"))
try:
    AQI = int(pollution["hourly"]["us_aqi"][hour])
except TypeError:
    AQI = -1

# Air quality
if AQI == -1:
    QUALITY = "Unknown"
if AQI <= 50:
    QUALITY = "Good"
elif AQI <= 100:
    QUALITY = "Moderate"
elif AQI <= 150:
    QUALITY = "Unhealty"
elif AQI <= 200:
    QUALITY = "Unhealthy"
elif AQI <= 300:
    QUALITY = "Very unhealthy"
elif AQI <= 500:
    QUALITY = "Hazardous"
else:
    QUALITY = "Unknown"

# Add data to tooltip
TOOLTIP += f"City: {city}\n"
TOOLTIP += f"Description: {weather_lookup[CODE_NOW][1]}\n"
TOOLTIP += f"Temperature: {TEMP_NOW}°F\n"
TOOLTIP += f"Humidity: {HUMIDITY_NOW}%\n"
TOOLTIP += f"Wind: {WINDSPEED_NOW}mph {winddirection_now}\n"
TOOLTIP += f"Air quality: {QUALITY}\n"

# Next n hours
try:
    hourly_hours = int(config["settings"]["hourly_hours"])
    if hourly_hours > 0:
        TOOLTIP += ("\n<span color='#8fa1be' font_size='16pt'>"
                    "Hourly forecast</span>\n")
        current_hour = now.strftime("%Y-%m-%dT%H:00")
        current_hour_index = weather["hourly"]["time"].index(current_hour)
        for i in range(current_hour_index + 1,
                       current_hour_index + hourly_hours + 1):
            hourly_hour = datetime.strptime(weather["hourly"]["time"][i],
                                            "%Y-%m-%dT%H:%M")
            WC = str(weather['hourly']['weathercode'][i])
            TOOLTIP += (
                f"{hourly_hour.strftime('%l%P')}: "
                f"{int(weather['hourly']['temperature_2m'][i])} "
                f"{weather_lookup[WC][1]}"
                "\n"
                )
except KeyError:
    TOOLTIP += ("\n<span color='#bf616a'>Please set hourly_hours\n"
                "in ~/.config/weather.ini</span>\n")

# Print header for weekly forecast
TOOLTIP += "\n<span color='#8fa1be' font_size='16pt'>7 day forecast</span>\n"

# Split weekly data
for x in range(7):
    date = datetime.strptime(weather["daily"]["time"][x], "%Y-%m-%d")
    dow = date.strftime("%A")
    CODE = str(weather["daily"]["weathercode"][x])
    TEMP_MAX = str(int(weather["daily"]["temperature_2m_max"][x]))
    TEMP_MIN = str(int(weather["daily"]["temperature_2m_min"][x]))
    WIND_MAX = str(int(weather["daily"]["wind_speed_10m_max"][x]))
    WIND_DIR = int(weather["daily"]["wind_direction_10m_dominant"][x])
    WIND_TEXT = deg_to_card(WIND_DIR)
    WIND_ARROW = deg_to_card(WIND_DIR)
    # Add formatted line to tooltip
    TOOLTIP += (f"{dow[:2]}: {TEMP_MAX}/{TEMP_MIN} "
                f"{WIND_MAX} {WIND_ARROW} "
                f"{weather_lookup[CODE][1]}\n")

# Get boolean from config if exists, otherwise enable night icons
try:
    NIGHT_ICONS = config.getboolean('settings', 'night_icons')
except (KeyError, configparser.NoOptionError):
    NIGHT_ICONS = 1
if NIGHT_ICONS == 1:
    night_hour = now.strftime("%-H")
    # Change icon if night time
    if int(night_hour) < sunrise or int(night_hour) > sunset:
        weather_lookup["0"][0] = ""

# Print data formatted for waybar
print(json.dumps({"text": f"{weather_lookup[CODE_NOW][0]} {TEMP_NOW}°F",
                  "tooltip": TOOLTIP.rstrip()}))
