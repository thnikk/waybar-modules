#!/usr/bin/python3 -u
"""
Description: CyberPower UPS waybar module. Inspired by
https://github.com/bjonnh/cyberpower-usb-watcher
Author: thnikk
"""
import json
import argparse
import sys
import os
import hid


parser = argparse.ArgumentParser(description="CyberPower UPS module")
parser.add_argument('vendor', action='store', type=str, help='Vendor ID')
parser.add_argument('product', action='store', type=str, help='Product ID')
args = parser.parse_args()

cache_file = os.path.expanduser("~/.cache/ups.json")


class CyberPower:
    """ Class for CyberPower UPS """
    def __init__(self, vendor, product) -> None:
        self.device = hid.Device(
            path=hid.enumerate(vendor, product)[0]['path'])

    def load_watts(self) -> int:
        """ Get load """
        return round(self.capacity() * (self.load_percent()/100))

    def load_percent(self) -> int:
        """ Get load percentage """
        return self.device.get_feature_report(0x13, 2)[1]

    def capacity(self) -> int:
        """ Get capacity in watts """
        report = self.device.get_feature_report(0x18, 6)
        return report[2] * 256 + report[1]

    def runtime(self) -> int:
        """ Battery runtime """
        report = self.device.get_feature_report(0x08, 6)
        return int((report[3]*256+report[2])/60)

    def battery_percent(self) -> int:
        """ Battery percentage """
        return self.device.get_feature_report(0x08, 6)[1]

    def close(self) -> None:
        """ Close device """
        self.device.close()


def main():
    """ Main function """
    try:
        ups = CyberPower(int(args.vendor, 16), int(args.product, 16))
    except IndexError:
        sys.exit(1)
    output = json.dumps({
        "text": ups.load_watts(),
        "tooltip": f"<span color='#8fa1be' font_size='16pt'>UPS stats</span>\n"
        f"Runtime: {ups.runtime()} minutes\n"
        f"Load: {ups.load_watts()} Watts ({ups.load_percent()}%)\n"
        f"Battery: {ups.battery_percent()}%"
    })
    print(output)
    with open(cache_file, 'w', encoding='utf-8') as file:
        file.write(output)
    ups.close()


if __name__ == "__main__":
    try:
        main()
    except hid.HIDException:
        with open(cache_file, 'r', encoding='utf-8') as file:
            cache = json.load(file)
        print(json.dumps(cache))
