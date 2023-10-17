#!/usr/bin/python3
# Shows number of pacman, aur, and flatpak updates.
# Individual updates are listed in the tooltip (truncated at 50).
# Requires pacman-contrib, paru, and flatpak for respective functionality.
import subprocess
import json

# Visually differentiate matching packages
alert_list = ["linux", "linux-lts", "libvirt", "qemu", "discord"]

# Get updates for pacman and aur
package_managers = {
    "Pacman": subprocess.run(
        ["checkupdates"], check=False, capture_output=True
        ).stdout.decode('utf-8').splitlines(),
    "AUR": subprocess.run(
        ["paru", "-Qum"], check=False, capture_output=True
        ).stdout.decode('utf-8').splitlines(),
    "Flatpak": subprocess.run(
        ["flatpak", "remote-ls", "--updates"], check=False, capture_output=True
        ).stdout.decode('utf-8').splitlines()
}

# Get number of updates
num_updates = sum(len(v) for v in package_managers.values())

# Create an empty variable for updates tooltip
tooltip = ""

# Iterate through package managers
for manager, packages in package_managers.items():
    # Only display package manager name if there are any new packages
    if len(packages) > 0:
        tooltip += ("<span color='#8fa1be' font_size='16pt'>{}</span>\n"
                    ).format(manager)
    # Count number of packages
    pkg_count = 0
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
        tooltip += package + " <span color='#a3be8c'>" + version + "</span>\n"
        # Increase package count
        pkg_count += 1
        # Break out of loop if more than 50 packages
        if pkg_count > 50:
            # Say there are more that aren't included in the list
            tooltip += "{} more...\n".format(len(packages) - pkg_count)
            break
    if len(packages) > 0:
        tooltip += "\n"

if not tooltip:
    tooltip = "<span font_size='16pt'>No updates</span>"

# Print formatted json
print(json.dumps({"text": num_updates, "tooltip": tooltip.rstrip()}))
