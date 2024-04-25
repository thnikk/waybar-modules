#!/usr/bin/python3 -u
"""
Description:
Author:
"""
from subprocess import check_output, run, Popen
import argparse


def parse_args() -> argparse.ArgumentParser:
    """ Parse arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('script')
    parser.add_argument('-o', '--output', type=str)
    return parser.parse_args()


def find_py(process, match) -> bool:
    """ f """
    if '/usr/bin/python' in process[0]:
        for arg in process[1:]:
            if (
                '/' in arg and
                match in arg and
                __file__.split('/')[-1] not in arg
            ):
                return True
    return False


def get_processes(match):
    """ Get process list """
    process_list = {}
    for line in check_output(
        ['pgrep', '-af', match]
    ).decode('utf-8').splitlines():
        process_list[line.split()[0]] = line.split()[1:]

    output = {}
    for pid, process in process_list.items():
        if find_py(process, match):
            output[pid] = process
    return output


def main():
    """ Main function """
    args = parse_args()
    processes = get_processes('widget.py')

    script_path = "/".join(__file__.split('/')[:-1] + [args.script])

    # Kill all widget processes
    for pid in list(processes):
        run(['kill', pid], check=False)

    check = False
    for pid, process in processes.items():
        for arg in process:
            if args.script in arg:
                check = True
    if not check:
        if args.output:
            Popen([script_path, '-o', args.output])
        else:
            Popen([script_path])


if __name__ == "__main__":
    main()
