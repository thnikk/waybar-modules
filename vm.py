#!/usr/bin/python3
"""
Description: Shows number of running VMs and lists the running VMs in the
tooltip.
Author: thnikk
"""
import glob
import json
import tooltip as tt


def get_libvirt():
    """ Get domains with list comprehension """
    return [
        domain_path.split("/")[-1:][0].rstrip(".xml")
        for domain_path in glob.glob("/var/run/libvirt/qemu/*.xml")]


def main():
    """ Main function """
    domains = get_libvirt()
    if not domains:
        print(json.dumps({"text": ""}))
        return

    print(json.dumps({
        "text": f" {str(len(domains))}",
        "tooltip": "\n".join([tt.heading('Running VMs')] + domains),
        "widget": {"libvirt": domains}
    }))


if __name__ == "__main__":
    main()
