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
from common import Cache


def parse_args():
    """ Parse arguments """
    parser = argparse.ArgumentParser(description="CyberPower UPS module")
    parser.add_argument('vendor', action='store', type=str, help='Vendor ID')
    parser.add_argument('product', action='store', type=str, help='Product ID')
    parser.add_argument(
        '-o', '--offset', type=int, default=0, help='Wattage offset')
    return parser.parse_args()


class CyberPower:
    """ Class for CyberPower UPS """
    def __init__(self, vendor, product, offset) -> None:
        self.device = hid.Device(
            path=hid.enumerate(vendor, product)[0]['path'])
        self.offset = offset
        self.status_report = self.device.get_feature_report(0x0b, 3)[1]

    def load_watts(self) -> int:
        """ Get load """
        return round(self.capacity() * (self.load_percent()/100) / 10) * 10

    def offset_watts(self) -> int:
        """ Get offset watts """
        return self.load_watts() - self.offset

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

    def ac(self) -> bool:
        """ AC status """
        return bool(self.status_report & 1)

    def charging(self) -> bool:
        """ Charging status """
        return bool(self.status_report & 2)

    def full(self) -> bool:
        """ Full status """
        return bool((self.status_report & 16) > 0)

    def close(self) -> None:
        """ Close device """
        self.device.close()


def main():
    """ Main function """
    args = parse_args()
    cache = Cache(os.path.expanduser("~/.cache/ups.json"))
    try:
        try:
            ups = CyberPower(
                int(args.vendor, 16),
                int(args.product, 16),
                args.offset
            )
        except IndexError:
            sys.exit(1)
        output = json.dumps({
            "text": ups.offset_watts(),
            "tooltip": "\n".join([
                "<span color='#8fa1be' "
                "font_size='16pt'>UPS stats</span>",
                f"Runtime: {ups.runtime()} minutes",
                f"Load: {ups.load_watts()} Watts ({ups.load_percent()}%)",
                f"Battery: {ups.battery_percent()}%",
                f"AC power: {ups.ac()}",
                f"Charging: {ups.charging()}",
                f"Battery full: {ups.full()}",
            ])
        })
        if not ups.ac():
            output['class'] = 'red'
        print(output)
        cache.save(output)
        ups.close()
    except hid.HIDException:
        print(json.dumps(cache.load()))


if __name__ == "__main__":
    main()
