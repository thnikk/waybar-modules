#!/usr/bin/python3 -u
"""
Description: Newer OpenMeteo weather module that takes a zip code as an
argument instead of in a config file.
Author: thnikk
"""
from datetime import datetime, timedelta
import json
import os
import sys
import argparse
import requests

parser = argparse.ArgumentParser(
    description="Get weather formatted for waybar")
parser.add_argument(
    'zip', type=str, help="Zip code")
parser.add_argument(
    '-n', action='store_true', help="Enable night icons")
parser.add_argument(
    '-f', type=int, const=5, nargs='?',
    help="How many hours to show in tooltip (default is 5)")
args = parser.parse_args()


class OpenMeteo():  # pylint: disable=too-few-public-methods
    """ Class for OpenMeteo """
    def __init__(self, zip_code):
        """ Initialize class"""
        geo = self.__cache__(
            os.path.expanduser(f"~/.cache/geocode-{zip_code}.json"),
            "https://geocoding-api.open-meteo.com/v1/search?name="
            f"{zip_code}&count=1&language=en&format=json",
            zip_code
        )
        self.latitude = geo['results'][0]['latitude']
        self.longitude = geo['results'][0]['longitude']
        self.timezone = geo['results'][0]['timezone']
        self.city = geo['results'][0]['name']
        self.weather = Weather(
            self.latitude, self.longitude, self.timezone, zip_code)
        self.pollution = Pollution(
            self.latitude, self.longitude, self.timezone, zip_code)

    def __cache__(self, path, url, zip_code):
        """ Update cache file if enough time has passed. """
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            if str(zip_code) not in data['results'][0]['postcodes']:
                raise ValueError("Updated postcode")
            print(f"Loading data from cache at {path}.", file=sys.stderr)
        except (FileNotFoundError, ValueError):
            print("Fetching new geocode data.", file=sys.stderr)
            data = requests.get(url, timeout=3).json()
            with open(path, 'w', encoding='utf-8') as file:
                file.write(json.dumps(data, indent=4))
        return data


def lookup(code, mode, night=False):
    """ Get description for weather code """
    weather_lookup = {
        0:  ["", "Clear"],
        1:  ["", "Mostly clear"],
        2:  ["", "Partly cloudy"],
        3:  ["", "Overcast"],
        45: ["", "Fog"],
        48: ["", "Depositing rime fog"],
        51: ["", "Light drizzle"],
        53: ["", "Moderate drizzle"],
        55: ["", "Dense drizzle"],
        56: ["", "Light freezing drizzle"],
        57: ["", "Dense freezing drizzle"],
        61: ["", "Slight rain"],
        63: ["", "Moderate rain"],
        65: ["", "Heavy rain"],
        66: ["", "Light freezing rain"],
        67: ["", "Heavy freezing rain"],
        71: ["", "Slight snow"],
        73: ["", "Moderate snow"],
        75: ["", "Heavy snow"],
        77: ["", "Snow grains"],
        80: ["", "Slight rain showers"],
        81: ["", "Moderate rain showers"],
        82: ["", "Violent rain showers"],
        85: ["", "Slight snow showers"],
        86: ["", "Heavy snow showers"],
        95: ["", "Thunderstorm"],
        96: ["", "Slight hailing thunderstorm"],
        99: ["", "Heavy hailing thunderstorm"]
    }
    if night:
        weather_lookup[0][0] = ""
    return weather_lookup[code][mode]


class Weather():  # pylint: disable=too-few-public-methods
    """ Get daily weather data """
    def __init__(self, lat, lon, timezone, zip_code):
        weather = self.__cache__(
            os.path.expanduser(f"~/.cache/weather-{zip_code}.json"),
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&"
            f"longitude={lon}&"
            "&hourly=temperature_2m,relativehumidity_2m,weathercode,"
            "windspeed_10m,winddirection_10m&daily=weathercode,"
            "temperature_2m_max,temperature_2m_min,sunrise,sunset,"
            "wind_speed_10m_max,wind_direction_10m_dominant&"
            "temperature_unit=fahrenheit&"
            f"timezone={timezone}",
            timedelta(hours=1)
        )
        self.hourly = Hourly(weather)
        self.daily = Daily(weather)

    def __cache__(self, path, url, delta) -> dict:
        """ Update cache file if enough time has passed. """
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if (datetime.now() - mtime) > delta:
                raise ValueError('old')
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            print(f"Loading data from cache at {path}.", file=sys.stderr)
        except (FileNotFoundError, ValueError):
            print("Fetching new data.", file=sys.stderr)
            data = requests.get(url, timeout=3).json()
            with open(path, 'w', encoding='utf-8') as file:
                file.write(json.dumps(data, indent=4))
        return data


class Hourly():
    """ Parse hourly data and split into objects """
    def __init__(self, weather):
        self.weathercodes = weather['hourly']['weathercode']
        self.temperatures = weather['hourly']['temperature_2m']
        self.windspeeds = weather['hourly']['windspeed_10m']
        self.humidities = weather['hourly']['relativehumidity_2m']

    def code(self, index):
        """ Get weathercode """
        return self.weathercodes[index]

    def description(self, index):
        """ Get description """
        return lookup(self.code(index), 1)

    def icon(self, index, night=False):
        """ Get icon """
        return lookup(self.code(index), 0, night)

    def temp(self, index):
        """ Get temperature """
        return round(self.temperatures[index])

    def wind(self, index):
        """ Get windspeed """
        return self.windspeeds[index]

    def humidity(self, index):
        """ Get humidity """
        return self.humidities[index]


class Daily():
    """ Parse daily data and split into objects """
    def __init__(self, weather):
        self.sunrise = int(datetime.strptime(
            weather["daily"]["sunrise"][0],
            "%Y-%m-%dT%H:%M").strftime("%H"))
        self.sunset = int(datetime.strptime(
            weather["daily"]["sunset"][0],
            "%Y-%m-%dT%H:%M").strftime("%H"))
        self.weathercodes = weather['daily']['weathercode']
        self.lows = weather['daily']['temperature_2m_min']
        self.highs = weather['daily']['temperature_2m_max']
        self.windspeeds = weather['daily']['wind_speed_10m_max']
        self.winddirs = weather['daily']['wind_direction_10m_dominant']

    def code(self, index):
        """ Get weathercode """
        return self.weathercodes[index]

    def description(self, index) -> str:
        """ Get description of weather """
        return lookup(self.code(index), 1)

    def low(self, index) -> int:
        """ Get min temperature """
        return round(self.lows[index])

    def high(self, index) -> int:
        """ Get max temperature """
        return round(self.highs[index])

    def wind(self, index) -> int:
        """ Get max wind speed """
        return round(self.windspeeds[index])

    def direction(self, index) -> int:
        """ Get max wind speed """
        return round(self.winddirs[index])


class Pollution():
    """ Get daily polution data """
    def __init__(self, lat, lon, timezone, zip_code) -> None:
        pollution = self.__cache__(
            os.path.expanduser(f"~/.cache/pollution-{zip_code}.json"),
            "https://air-quality-api.open-meteo.com/v1/air-quality?"
            f"latitude={lat}&longitude={lon}&hourly=us_aqi"
            f"&timezone={timezone}",
            timedelta(days=1)
        )
        self.aqi = pollution["hourly"]["us_aqi"]

    def __cache__(self, path, url, delta) -> dict:
        """ Update cache file if enough time has passed. """
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if (datetime.now() - mtime) > delta:
                raise ValueError('old')
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            print(f"Loading data from cache at {path}.", file=sys.stderr)
        except (FileNotFoundError, ValueError):
            print("Fetching new data.", file=sys.stderr)
            data = requests.get(url, timeout=3).json()
            with open(path, 'w', encoding='utf-8') as file:
                file.write(json.dumps(data, indent=4))
        return data

    def __aqi_to_desc__(self, value) -> str:
        """ Get description for aqi """
        for desc in [
            (50, "Good"), (100, "Moderate"), (150, "Unhealthy"),
            (200, "Unhealthy"), (300, "Very unhealthy"), (500, "Hazardous")
        ]:
            if 0 < value < desc[0]:
                return desc[1]
        return "Unknown"

    def description(self, index) -> str:
        """ Get air quality description for given hour """
        return self.__aqi_to_desc__(self.aqi[index])


def tooltip(om, index, hours) -> str:
    """ Generate tooltip """
    output = (
        "<span color='#8fa1be' font_size='16pt'>Today</span>\n"
        f"City: {om.city}\n"
        f"Description: {om.weather.hourly.description(index)}\n"
        f"Temperature: {om.weather.hourly.temp(index)}\n"
        f"Humidity: {om.weather.hourly.humidity(index)}%\n"
        f"Wind: {om.weather.hourly.wind(index)} mph\n"
        f"Air quality: {om.pollution.description(index)}\n"
        "\n<span color='#8fa1be' font_size='16pt'>Hourly forecast</span>\n"
    )

    hourly_output = []
    for hour in range(1, (hours or 5) + 1):
        text = (datetime.now() + timedelta(hours=hour)).strftime("%l%P")
        hourly_output.append(
            f"{text}: {om.weather.hourly.temp(hour)} "
            f"{om.weather.hourly.description(hour)}"
        )
    # Strip whitespace from hour if all shown hours have whitespace
    if set(item[0] for item in hourly_output) == {' '}:
        hourly_output = [item[1:] for item in hourly_output]
    output += "\n".join(hourly_output) + "\n"

    output += (
        "\n<span color='#8fa1be' font_size='16pt'>"
        "Weekly forecast</span>\n"
    )

    for day in range(0, 6):
        abbr = (datetime.now() + timedelta(days=day)).strftime('%A')[:2]
        output += (
            f"{abbr}: "
            f"{om.weather.daily.low(day)}/{om.weather.daily.high(day)} "
            f"{om.weather.daily.wind(day)} "
            f"{om.weather.daily.description(day)}\n"
        )
    return output.strip()


def main():
    """ Main function """
    om = OpenMeteo(args.zip)
    now = datetime.now()
    hour_now = int(now.strftime('%H'))
    night = (
        om.weather.daily.sunrise > hour_now
        or hour_now > om.weather.daily.sunset) and args.n

    print(json.dumps(
        {
            "text": f"{om.weather.hourly.icon(hour_now, night)} "
            f"{om.weather.hourly.temp(hour_now)}°F",
            "tooltip": tooltip(om, hour_now, args.f)
        }
    ))


if __name__ == "__main__":
    main()
