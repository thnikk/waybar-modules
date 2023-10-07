#!/usr/bin/python3
# Waybar module that shows pacman+aur updates.
# Requires pacman-contrib and paru
import subprocess
import json
import sys

# Visually differentiate matching packages
alert_list = [ "linux", "linux-lts", "libvirt", "qemu", "discord" ]

# Get updates for pacman and aur
package_managers = {
    "Pacman": subprocess.run(["checkupdates"], check=False, capture_output=True).stdout.decode('utf-8').splitlines(),
    "AUR": subprocess.run(["paru", "-Qum"], check=False, capture_output=True).stdout.decode('utf-8').splitlines(),
    "Flatpak": subprocess.run(["flatpak", "remote-ls", "--updates"], check=False, capture_output=True).stdout.decode('utf-8').splitlines()
}

# Get number of updates
num_updates = len(package_managers["Pacman"]) + len(package_managers["AUR"])

# Create an empty variable for updates tooltip
tooltip = ""

# Iterate through package managers
for manager,packages in package_managers.items():
    # Only display package manager name if there are any new packages
    if len(packages) > 0: 
        tooltip += "<span color='#8fa1be' font_size='16pt'>" + manager + "</span>\n"
    # Count number of packages
    pkg_count = 0
    # Iterate through packages
    for package in packages:
        # Break up package info into parts
        parts = package.split()
        # Shorten name if longer than 19 characters
        if len(parts[0]) > 19:
            parts[0] = parts[0][:11] + "..." + parts[0][len(parts[0]) - 5:]
        # Add spaces up to 20th character
        if len(parts[0]) < 20:
            parts[0] = parts[0] + (" " * (20 - len(parts[0])))
        # Mark the package if it's in the alert list
        if parts[0] in alert_list:
            parts[0] = "<span color='#bf616a'>" + parts[0] + "</span>"
        # Don't add version numbers for flatpak
        if manager != "Flatpak":
            version = parts[3]
        else:
            version = ""
        # Format the rest to be pretty
        tooltip += parts[0] + " <span color='#a3be8c'>" + version + "</span>\n"

        # Increase package count
        count+=1
        # Break out of loop if more than 50 packages
        if count > 50:
            # Say there are more that aren't included in the list
            tooltip += "{} more...\n".format(len(packages) - 50)
            break
    if len(packages) > 0: 
        tooltip += "\n"

if not tooltip:
    tooltip = "<span font_size='16pt'>No updates</span>"

# Print formatted json
print(json.dumps({"text": num_updates, "tooltip": tooltip.rstrip()}))
