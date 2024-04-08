#!/usr/bin/python3 -u
"""
Description: CyberPower UPS module for PowerPanel Business.
Author: thnikk
"""
import json
import sys
import os
import argparse
import requests


def parse_args():
    """ Parse arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('profile')
    parser.add_argument('-w', '--wattage', type=int, default=1000)
    parser.add_argument('-o', '--offset', type=int, default=0)
    return parser.parse_args()


def get_config():
    """ Load config or exit """
    path = os.path.expanduser('~/.config/waybar-ups-ppb.json')
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.loads(file.read())
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(e.args, file=sys.stderr)
        print(json.dumps(
            {"text": "Config error", "class": "red"}
        ))
        sys.exit(0)


class CyberPower:  # pylint: disable=too-few-public-methods
    """ Class for CyberPower UPS """
    def __init__(self, ip, auth, capacity) -> None:
        status_full = requests.get(
            f"http://{ip}:3052/local/rest/v1/ups/status", timeout=3,
            headers={
                'Authorization': auth
            }
        )
        if status_full.status_code != 200:
            print(
                f"Request failed with code {status_full.status_code}",
                file=sys.stderr)
            sys.exit(0)
        self.status = status_full.json()

        self.capacity = capacity
        self.load_percent = int(self.status["output"]["loads"][0].split()[0])
        self.runtime = self.status['battery']['remainingRunTimeFormated']\
            .replace('.', '')
        self.battery_percent = int(
                self.status['battery']['capacity'].split()[0])

    def load_watts(self) -> int:
        """ Get load """
        return round(
                (self.load_percent/100) * self.capacity
        )


def main():
    """ Main function """
    args = parse_args()
    config = get_config()

    try:
        ups = CyberPower(
            config[args.profile]['ip'],
            config[args.profile]['auth'],
            args.wattage)
    except IndexError:
        sys.exit(1)
    output = json.dumps({
        "text": ups.load_watts() - args.offset,
        "tooltip": f"<span color='#8fa1be' font_size='16pt'>UPS stats</span>\n"
        f"Runtime: {ups.runtime}\n"
        f"Load: {ups.load_percent}%\n"
        f"Battery: {ups.battery_percent}%"
    })
    print(output)


if __name__ == "__main__":
    main()
