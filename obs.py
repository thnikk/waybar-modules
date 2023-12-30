#!/usr/bin/python3
"""
Shows the current OBS scene and changes color if recording.
Use with exec-if: pgrep OBS
Uses obsws-python: https://github.com/aatikturk/obsws-python
"""
import json
import sys
import obsws_python as obs

output = {}
ICON = ""

try:
    cl = obs.ReqClient(host='localhost', port=4455, password='password')
except ConnectionRefusedError:
    output["text"] = "<span color=\"#d8dee977\">" + ICON + "</span>"
    print(json.dumps(output))
    sys.exit(0)

status = cl.get_record_status()
scene = cl.get_current_program_scene().current_program_scene_name

output["text"] = f"{ICON} {scene}"
if status.output_duration > 0:
    output["text"] = (f"<span color=\"#bf616a\">{ICON}</span> "
                      f"{int(status.output_duration/1000)}")
print(json.dumps(output))
