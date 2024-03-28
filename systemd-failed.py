#!/usr/bin/python3 -u
"""
Description: Improved version of the built-in systemd module.
Author: thnikk
"""
from subprocess import run
import json


def get_output(command) -> list:
    """ Get output of shell command """
    output = run(
        command, check=True, capture_output=True
    ).stdout.decode('utf-8').strip().splitlines()
    return [line.split()[1] for line in output]


def style(input_string, color=None, size=None, bg=None) -> str:
    """ Style text """
    input_string = str(input_string)
    output = ["<span"]
    if color:
        output.append(f"color='#{color}'")
    if size:
        output.append(f"font_size='{size}pt'")
    if bg:
        output.append(f"background_color='#{bg}'")
    output.append('>')
    return " ".join(output) + input_string + "</span>"


def main():
    """ Main function """
    failed_system = get_output(['systemctl', '--failed', '--legend=no'])
    failed_user = get_output(['systemctl', '--user', '--failed',
                              '--legend=no'])

    num_failed = len(failed_system) + len(failed_user)

    output = {'text': '', 'tooltip': ''}
    if num_failed >= 1:
        output['class'] = 'alert'
        output['text'] = f' {num_failed}'
        output['tooltip'] = (
            f'{style("Systemd failed units", size=16, color="8fa1be")}\n\n')
        for name, failed_list in {
            'System': failed_system, "User": failed_user
        }.items():
            if failed_list:
                failed_string = "\n".join(failed_list)
                output['tooltip'] += f'{name}:\n{failed_string}\n'
    output['tooltip'] = output['tooltip'].strip()

    print(json.dumps(output))


if __name__ == "__main__":
    main()
