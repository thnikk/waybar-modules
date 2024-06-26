#!/usr/bin/python3 -u
"""
Description: Clock module with calendar tooltip that shows events.
Events are stored locally in ~/.config/calendar-events.json
Author: thnikk
"""
from datetime import datetime
import calendar
import re
import json
import time
import os
import tooltip as tt


def highlight(cal, day, color, bg=None) -> str:
    """ Highlight day """
    # Deconstruct
    days = "\n".join(cal.split('\n')[2:])
    # Substitute
    days = re.sub(day, tt.span(day, color, bg=bg), days)
    # Reconstruct
    cal = "\n".join(cal.split('\n')[:2] + days.split('\n'))
    return cal


def add_tag(cal, day, tag) -> str:
    """ Add a tag to a day """
    # Deconstruct
    days = "\n".join(cal.split('\n')[2:])
    # Substitute
    days = re.sub(day, f'<{tag}>{day}</{tag}>', days)
    # Reconstruct
    cal = "\n".join(cal.split('\n')[:2] + days.split('\n'))
    return cal


def auto_color(event) -> str:
    """ Automatically set color based on words in event """
    colors = {"appointment": "#bf616a", "birthday": "#8fa1b3"}
    for event_lookup, color in colors.items():
        if event_lookup in event.lower():
            return color
    return '#a3be8c'


def event_list(events, now) -> str:
    """ Get list of events as string """
    output = []
    output_dict = {"today": [], "month": []}
    for date, event in events.items():
        if str(now.month) == date.split('/')[0]:
            if str(now.day) == date.split('/')[1]:
                output_dict['today'].append(event)
            elif now.day < int(date.split('/')[1]):
                output_dict['month'].append(f'{date} - {event}')
    if output_dict['today']:
        output.append(tt.heading('Today'))
        for event in output_dict['today']:
            output.append(tt.span(event, auto_color(event)))
    if output_dict['month']:
        output.append(tt.heading('Upcoming'))
        for event in output_dict['month']:
            output.append(tt.span(event, auto_color(event)))
    return "\n".join(output)


def generate_calendar(events) -> str:
    """ Get full calendar as string for tooltip """
    now = datetime.now()
    day = now.strftime("%d").lstrip('0')
    cal = calendar.month(
        int(now.strftime("%y")),
        int(now.strftime("%m").lstrip('0'))
    )
    for date, event in events.items():
        if str(now.month) == date.split('/')[0]:
            if str(now.day) == date.split('/')[1]:
                cal = highlight(cal, date.split('/')[1],
                                "#2b303b", auto_color(event))
            else:
                cal = highlight(cal, date.split('/')[1], auto_color(event))
    if f'{now.month}/{now.day}' not in list(events):
        cal = highlight(cal, day, "#1c1f26", "#d8dee9")

    cal = cal.split('\n')
    cal[1] = tt.span(cal[1], color="#ffffff99")
    cal = "\n".join(cal).rstrip()

    return cal + "\n" + event_list(events, now)


def main() -> None:
    """ Main function """

    # Example events
    events = {
        f"{datetime.now().month}/14": "Appointment",
        f"{datetime.now().month}/24": "Birthday",
        f"{datetime.now().month}/25": "Test event"
    }

    try:
        with open(
            os.path.expanduser('~/.config/calendar-events.json'),
            'r', encoding='utf-8'
        ) as file:
            events = json.loads(file.read())
    except FileNotFoundError:
        pass

    while True:
        current_time = datetime.now().strftime("%I:%M %m/%d")
        output = {
            "text": f" {current_time}",
            "tooltip": generate_calendar(events).rstrip()
        }

        current_date = f'{datetime.now().month}/{datetime.now().day}'
        if current_date in list(events):
            try:
                mtime = datetime.fromtimestamp(
                    os.path.getmtime(
                        os.path.expanduser(
                            '~/.cache/hide-calendar-notification')
                    )
                )
                if mtime.date() != datetime.now().date():
                    raise ValueError
            except (FileNotFoundError, ValueError):
                output['text'] += tt.span(' ', auto_color(
                    events[current_date]))

        print(json.dumps(output))
        time.sleep(1)


if __name__ == "__main__":
    main()
