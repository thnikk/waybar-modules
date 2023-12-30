#!/usr/bin/python3 -u
""" Show stats for Genshin and HSR in waybar module """
import sys
import asyncio
import json
from datetime import datetime, timezone
import os
import configparser
import genshin

cache_file = os.path.expanduser("~/.cache/hoyo-stats.json")
config_file = os.path.expanduser("~/.config/hoyo-stats.ini")

# Create cache file if it doesn't exist
if not os.path.exists(config_file):
    with open(config_file, "a", encoding='utf-8') as f:
        f.write("[settings]\nltuid = \nltoken = \ngenshin_id = \nhsr_id =")
        f.close()
# Load config from cache
config = configparser.ConfigParser()
config.read(config_file)


def config_fail():
    """ Print info to waybar on fail """
    print(json.dumps({"text": ("Set up hoyo module in "
                               "~/.config/hoyo-stats.json")}))


def time_diff(now, future, rate):
    """ Calculate time difference and return string """
    max_time = future - now
    until_next = (max_time.seconds // 60) % (rate * 40)
    return f"{until_next // 60}:{until_next % 60}"


async def main():
    """ Main function """
    cookies = {
            "ltuid": config["settings"]["ltuid"],
            "ltoken": config["settings"]["ltoken"]
            }
    # Get current time
    time_now = datetime.now(timezone.utc)

    # Main output dictionary
    main_dict = {}

    try:
        if config["settings"]["genshin_id"]:
            # Get genshin info
            genshin_client = genshin.Client(cookies)
            genshin_notes = await genshin_client.get_notes()
            genshin_user = await genshin_client.get_full_genshin_user(
                    config["settings"]["genshin_id"])
            com_prog = genshin_notes.completed_commissions + \
                int(genshin_notes.claimed_commission_reward)
            main_dict["Genshin"] = {
                "Resin": genshin_notes.current_resin,
                "Until next 40": time_diff(
                    time_now, genshin_notes.resin_recovery_time, 8),
                "Dailies completed": f"{com_prog}/5",
                "Remaining boss discounts": genshin_notes.remaining_resin_discounts,
                "Realm currency": genshin_notes.current_realm_currency,
                "Abyss progress": (f"{genshin_user.abyss.current.max_floor} "
                                   f"{genshin_user.abyss.current.total_stars}"
                                   )
            }
    except KeyError:
        pass

    try:
        if config["settings"]["hsr_id"]:
            # Get HSR info
            hsr_client = genshin.Client(cookies, game=genshin.Game.STARRAIL)
            hsr_notes = await hsr_client.get_starrail_notes()
            hsr_user = await hsr_client.get_starrail_challenge(
                    config["settings"]["hsr_id"])
            moc_floors = [floor.name for floor in hsr_user.floors]
            daily_prog = hsr_notes.current_train_score // 100
            main_dict["HSR"] = {
                "Trailblaze power": hsr_notes.current_stamina,
                "Until next 40": time_diff(
                    time_now, hsr_notes.stamina_recovery_time, 6),
                "Dailies completed": f"{daily_prog}/5",
                "Remaining boss discounts": hsr_notes.remaining_weekly_discounts,
                "SU weekly score": "{}/{}".format(hsr_notes.current_rogue_score,
                                                  hsr_notes.max_rogue_score),
                "MoC progress": f"{len(moc_floors)} {hsr_user.total_stars}"
            }
    except KeyError:
        pass

    # Write dictionary to json file
    with open(cache_file, "w", encoding='utf-8') as save_file:
        save_file.write(json.dumps(main_dict, indent=4))

# Check modification date
try:
    mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
    mod_seconds = (datetime.now() - mod_time).total_seconds()
    if mod_seconds > 60*2:
        asyncio.run(main())
except FileNotFoundError:
    asyncio.run(main())


# Load cache from file
cache = {}
with open(cache_file, encoding='utf-8') as json_file:
    cache = json.load(json_file)

text = []
tooltip = []

if not cache:
    config_fail()
    sys.exit(0)

for game, data in cache.items():

    if game == "Genshin":
        dailies = int(data["Dailies completed"].split("/")[0])
        # Set color based on status
        if dailies < 5 and data["Realm currency"] >= 2000:
            ICON = "<span color=\"#d08770\"> </span>"
        elif data["Realm currency"] >= 2000:
            ICON = "<span color=\"#ebcb8b\"> </span>"
        elif dailies < 5:
            ICON = "<span color=\"#bf616a\"> </span>"
        else:
            ICON = "  "
        text.append(ICON + str(data["Resin"]))
    elif game == "HSR":
        su_points = int(data["SU weekly score"].split("/")[0])
        su_max = int(data["SU weekly score"].split("/")[1])
        dailies = int(data["Dailies completed"].split("/")[0])
        if dailies < 5:
            ICON = "<span color=\"#bf616a\"> </span>"
        elif su_points < su_max and datetime.today().weekday() >= 5:
            ICON = "<span color=\"#ebcb8b\"> </span>"
        else:
            ICON = " "
        text.append(ICON + str(data["Trailblaze power"]))

    # Create tooltip
    tooltip.append(
            ("<span color='#8fa1be' font_size='16pt'>"
             f"{game} Stats</span>\n") +
            '\n'.join(
                f'{key}: {value}' for key, value in data.items()))

# Print output as json
print(json.dumps({"text": "  ".join(text), "tooltip": "\n\n".join(tooltip)}))
