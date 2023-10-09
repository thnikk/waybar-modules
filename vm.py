#!/usr/bin/python3
# Shows number of running VMs and lists the running VMs in the tooltip.
import glob
import json

# Get domains
domains = [domain_path.split("/")[-1:][0].rstrip(".xml") for domain_path in glob.glob("/var/run/libvirt/qemu/*.xml")]

# Make tooltip
if len(domains) > 0:
    tooltip = "<span color='#8fa1be' font_size='16pt'>Running VMs</span>\n"
    for domain in domains:
        tooltip += domain + "\n"
else:
    tooltip = "No VMs running."

# Print output
print(json.dumps({"text": str(len(domains)), "tooltip": tooltip.rstrip()}))
