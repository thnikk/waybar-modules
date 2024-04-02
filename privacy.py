#!/usr/bin/python3 -u
"""
Description: Privacy module that doesn't crash waybar.
Author: thnikk
"""
from subprocess import run
import json


def json_output(command):
    """ Get json for command output """
    output = run(
        command, capture_output=True, check=True
    ).stdout.decode('utf-8')
    return json.loads(output)


def get_prop(full_props, prop_list):
    """ Return first prop in prop list found in full_props """
    for prop in prop_list:
        try:
            return full_props[prop]
        except KeyError:
            pass
    return None


def get_categories(pw):
    """ Get dictionary of running strings by programs """
    running = {}
    for item in pw:
        try:
            if (
                item['info']['state'] == 'running' and
                'Stream/Input' in item['info']['props']['media.class']
            ):
                mtype = item['info']['props']['media.class'].split('/')[-1]
                program = get_prop(
                    item['info']['props'],
                    ['application.process.binary', 'node.name'])
                try:
                    running[mtype]
                except KeyError:
                    running[mtype] = []
                if program not in running[mtype]:
                    running[mtype].append(program)
        except KeyError:
            pass
    return running


def main():
    """ Main function """
    pw = json_output(['pw-dump'])
    categories = get_categories(pw)

    output = {'class': 'green'}

    icon_lookup = {'Audio': '', 'Video': ''}
    icon = " ".join([icon_lookup[category] for category in categories])
    output['text'] = icon

    tooltip = []
    for category, progs in categories.items():
        tooltip.append(
            f'<span color="#8fa1be" font_size="16pt">{category}:</span>')
        for prog in progs:
            tooltip.append(prog)
    output['tooltip'] = '\n'.join(tooltip)
    print(json.dumps(output))


if __name__ == "__main__":
    main()
