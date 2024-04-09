#!/usr/bin/python3 -u
"""
Description: Track updates from git repo
Author: thnikk
"""
import os
from subprocess import run, CalledProcessError
import argparse
import json


class Git:
    """ d """
    def __init__(self, path):
        self.path = path

    def fetch(self) -> None:
        """ Fetch """
        try:
            run(
                ['git', '-C', self.path, 'fetch'],
                check=True, capture_output=True
            )
        except CalledProcessError as e:
            print(e.output)

    def commits(self) -> list:
        """ Pull """
        return run(
            [
                "git", "-C", self.path, "log",
                "--pretty=format:%h - %s (%cr)", "--abbrev-commit",
                "--date=relative", "main..origin/main"
            ],
            check=True, capture_output=True
        ).stdout.decode('utf-8').replace('&', 'and').splitlines()


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
    if commits:
        print(json.dumps({
            "text": f"{args.icon} {len(commits)}",
            "tooltip": "\n".join(commits)
        }))
    else:
        print(json.dumps({"text": ""}))


if __name__ == "__main__":
    main()
