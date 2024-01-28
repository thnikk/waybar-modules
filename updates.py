#!/usr/bin/python3 -u
"""
Description: Waybar module for package updates
Author: thnikk
"""
import subprocess
import concurrent.futures
import json
import time

# You can add whatever package manager you want here with the appropriate
# command. Change the separator and values to get the package and version from
# each line.
config = {
    "Pacman": {
        "command": ["checkupdates"],
        "separator": ' ',
        "values": [0, -1]
    },
    "AUR": {
        "command": ["paru", "-Qum"],
        "separator": ' ',
        "values": [0, -1]
    },
    "Flatpak": {
        "command": ["flatpak", "remote-ls", "--updates"],
        "separator": '\t',
        "values": [0, 2]
    },
}

# Alert for these packages
alerts = ["linux", "discord", "qemu", "libvirt"]

pool = concurrent.futures.ThreadPoolExecutor(max_workers=len(config))


def get_output(command, separator, values) -> list:
    """ Get formatted command output """
    # Get line-separated output
    while True:
        try:
            output = subprocess.run(
                command, check=True, capture_output=True
            ).stdout.decode('utf-8').splitlines()
        except subprocess.CalledProcessError:
            time.sleep(1)
            continue
        break
    # Find lines containing alerts
    move = []
    for alert in alerts:
        for line in output:
            if alert in line:
                move.append(line)
    # And move them to the front of the list
    for line in move:
        output.remove(line)
        output.insert(0, line)
    # Split each line into [package, version]
    split_output = [
        [
            line.split(separator)[value] for value in values
        ] for line in output
    ]
    return split_output


def get_tooltip(package_managers) -> str:
    """ Generate tooltip string """
    tooltip = ""
    for name, packages in package_managers.items():
        # Skip if no packages
        if len(packages) == 0:
            continue
        # Package manager name
        tooltip += f"\n<span color='#8fa1be' font_size='16pt'>{name}</span>\n"
        for count, package in enumerate(packages):
            if count > 20:
                # Only show first 20 packages
                tooltip += f"{len(packages) - count} more...\n"
                break
            # Package name
            if len(package[0]) > 20:
                tooltip += f"{package[0][:17]}..."
            else:
                tooltip += f"{package[0]}"
            tooltip += " " * (20 - len(package[0]))
            # If version
            if len(package) > 1:
                # Version
                tooltip += f" <span color='#a3be8c'>{package[1]}</span>\n"
            else:
                # Otherwise just newline
                tooltip += "\n"
    return tooltip.strip()


def get_total(package_managers) -> int:
    """ Get total number of updates """
    return sum(len(packages) for packages in package_managers.values())


def main() -> None:
    """ Main function """
    # Initialize dictionary first to set the order based on the config
    package_managers = {name: [] for name in config}
    # Get output for each package manager
    for name, info in config.items():
        thread = pool.submit(
            get_output, info["command"], info["separator"], info["values"])
        package_managers[name] = thread.result()
    pool.shutdown(wait=True)
    # Create variable for output
    output = {
        "text": get_total(package_managers),
        "tooltip": get_tooltip(package_managers),
    }
    # Print for waybar
    print(json.dumps(output))


if __name__ == "__main__":
    main()
