#!/usr/bin/python3
"""
Shows number of pacman, aur, and flatpak updates.
Individual updates are listed in the tooltip (truncated at 50).
Requires pacman-contrib, paru, and flatpak for respective functionality.
Author: thnikk
"""
import subprocess
import json
import concurrent.futures

pool = concurrent.futures.ThreadPoolExecutor(max_workers=3)

# Visually differentiate matching packages
alert_list = ["linux", "linux-lts", "libvirt", "qemu", "discord"]

# Get updates for pacman and aur
package_managers = {"Pacman": [], "AUR": [], "Flatpak": []}


def get_updates(man, command):
    """ Get output of subprocess and split lines into list """
    package_managers[man] = subprocess.run(
            command, check=False, capture_output=True
            ).stdout.decode('utf-8').splitlines()


# Get updates in parallel
pool.submit(get_updates, "Pacman", ["checkupdates"])
pool.submit(get_updates, "AUR", ["paru", "-Qum"])
pool.submit(get_updates, "Flatpak", ["flatpak", "remote-ls", "--updates"])
pool.shutdown(wait=True)

# Get number of updates
num_updates = sum(len(v) for v in package_managers.values())

# Create an empty variable for updates tooltip
TOOLTIP = ""

# Iterate through package managers
for manager, packages in package_managers.items():
    # Only display package manager name if there are any new packages
    if len(packages) > 0:
        TOOLTIP += f"<span color='#8fa1be' font_size='16pt'>{manager}</span>\n"
    # Count number of packages
    PKG_COUNT = 0
    # Iterate through packages
    for package_string in packages:
        # Break up package info into parts
        if manager == "Flatpak":
            parts = package_string.split("\t")
            package = parts[0]
            version = parts[2]
        else:
            parts = package_string.split()
            package = parts[0]
            version = parts[3]
        # Shorten name if longer than 19 characters
        if len(package) > 20:
            package = package[:12] + "..." + package[len(package) - 5:]
        # Add spaces up to 20th character
        if len(package) < 20:
            package = package + (" " * (20 - len(package)))
        # Shorten version number if it's too long
        if len(version) > 10:
            version = version[:7] + "..."
        # Mark the package if it's in the alert list
        if package in alert_list:
            package = "<span color='#bf616a'>" + package + "</span>"
        # Format the rest to be pretty
        TOOLTIP += package + " <span color='#a3be8c'>" + version + "</span>\n"
        # Increase package count
        PKG_COUNT += 1
        # Break out of loop if more than 30 packages
        if PKG_COUNT > 30:
            # Say there are more that aren't included in the list
            TOOLTIP += f"{len(packages) - PKG_COUNT} more...\n"
            break
    if len(packages) > 0:
        TOOLTIP += "\n"

if not TOOLTIP:
    TOOLTIP = "<span font_size='16pt'>No updates</span>"

# Print formatted json
print(json.dumps({"text": num_updates, "tooltip": TOOLTIP.rstrip()}))
