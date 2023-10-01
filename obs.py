#!/usr/bin/python3
# Shows the current OBS scene and changes color if recording.
# Use with exec-if: pgrep OBS
# Uses obsws-python: https://github.com/aatikturk/obsws-python
import obsws_python as obs
import json
from datetime import datetime

output = {"text":"","alt":"","tooltip":""}
icon = ""

try:
    cl = obs.ReqClient(host='localhost', port=4455, password='password')
except:
    # print("Server not running.")
    output["text"] = "<span color=\"#d8dee977\">" + icon + "</span>"
    print(json.dumps(output))
    quit()

status = cl.get_record_status()
scene = cl.get_current_program_scene().current_program_scene_name

output["text"] = "{} {}".format(icon,scene)
if status.output_duration > 0:
    output["text"] = "<span color=\"#bf616a\">" + icon + "</span> " + str(int(status.output_duration/1000))
print(json.dumps(output))

