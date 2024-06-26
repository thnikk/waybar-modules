#!/usr/bin/python3 -u
"""
Description: Track updates from git repo
Author: thnikk
"""
import os
from subprocess import run, check_output, CalledProcessError
import argparse
import json
import re
from datetime import datetime, timezone
import sys
from common import print_debug
import tooltip as tt


class Git:
    """ Git class """
    def __init__(self, path):
        self.path = path
        self.name = self.get_name()

    def get_name(self) -> str:
        """ Get name of repo """
        name = check_output(
            ['git', '-C', os.path.expanduser(self.path),
             'config', '--get', 'remote.origin.url']
        ).decode().strip().split('/')[-1].split('.')[0].replace('-', ' ')
        return name.capitalize()

    def fetch(self) -> None:
        """ Fetch """
        try:
            run(
                ['git', '-C', self.path, 'fetch'],
                check=True, capture_output=True
            )
        except CalledProcessError as e:
            print(e.output)

    def commits(self):
        """ Get commits """

        def plural(num) -> str:
            """ Pluralize word """
            if num > 1:
                return 's'
            return ''

        def get_time(input_list) -> str:
            """ Get string of x days/minutes/hours ago """
            for value, word in enumerate(['day', 'hour', 'minute', 'second']):
                if input_list[value]:
                    return (
                        f"{input_list[value]} "
                        f"{word}{plural(input_list[value])} ago")
            return None

        try:
            command_output = run(
                [
                    'git', '-C', os.path.expanduser(self.path), 'log',
                    '--name-only', 'main..origin'
                ],
                check=True, capture_output=True
            ).stdout.decode('utf-8')
        except CalledProcessError:
            try:
                command_output = run(
                    [
                        'git', '-C', os.path.expanduser(self.path), 'log',
                        '--name-only', 'master..origin'
                    ],
                    check=True, capture_output=True
                ).stdout.decode('utf-8')
            except CalledProcessError as e:
                lines = e.stderr.decode('utf-8').splitlines()
                for line in lines:
                    print_debug(line)
                sys.exit(1)
        output = {}
        for line in command_output.splitlines():
            if re.match('^commit', line):
                chash = line.split()[1][:7]
                output[chash] = {
                    "author": None, "date": None, "msg": None, "files": []}
            elif re.match('^Author:', line):
                output[chash]['author'] = \
                    line.split(":")[1].split("<")[0].strip()
            elif re.match('^Date:', line):
                date = ':'.join(line.split(":")[1:]).strip()
                delta = datetime.now(timezone.utc) - datetime.strptime(
                    date, '%a %b %d %H:%M:%S %Y %z')
                dhms = [
                    delta.days, delta.seconds // 60 // 60,
                    delta.seconds // 60, delta.seconds]
                output[chash]['date'] = get_time(dhms)
            elif re.match('^ ', line):
                output[chash]['msg'] = line.strip().replace('&', 'and')
            else:
                if line:
                    output[chash]['files'].append(line)
        return output


def parse_args():
    """ Parse arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help='Path to git repo')
    parser.add_argument('-i', '--icon', type=str, default='')
    return parser.parse_args()


def main():
    """ Main function """
    args = parse_args()
    git = Git(os.path.expanduser(args.path))
    git.fetch()
    commits = git.commits()

    tooltip = []
    for commit, info in commits.items():
        tooltip.append(
            f"{tt.span(commit, 'blue')} {info['msg']} "
            f"({tt.span(info['date'], 'green')})"
        )
        for file in info['files']:
            tooltip.append(f'  {file}')
        tooltip.append('')

    if commits:
        print(json.dumps({
            "text": f"{args.icon} {len(commits)}",
            "tooltip": "\n".join(tooltip).strip(),
            "widget": {"name": git.name, "commits": commits}
        }))
    else:
        print(json.dumps({"text": ""}))


if __name__ == "__main__":
    main()
