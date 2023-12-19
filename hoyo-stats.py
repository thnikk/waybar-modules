#!/usr/bin/python3 -u
import asyncio
import genshin
import json
from datetime import datetime, timezone
import os
import configparser

cache_file = os.path.expanduser("~/.cache/hoyo-stats.json")
config_file = os.path.expanduser("~/.config/hoyo-stats.ini")

# Create cache file if it doesn't exist
if not os.path.exists(config_file):
    f = open(config_file, "a")
    f.write("[settings]\nltuid = \nltoken = \ngenshin_id = \nhsr_id =")
    f.close()
# Load config from cache
config = configparser.ConfigParser()
config.read(config_file)


def config_fail():
    print(json.dumps({"text": "Set up hoyo module in ~/.config/hoyo-stats.json"}))


def time_diff(now, future, rate):
    max_time = future - now
    until_next = (max_time.seconds // 60) % (rate * 40)
    return "{}:{}".format(until_next // 60, until_next % 60)


async def main():
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
            gn = await genshin_client.get_notes()
            gu = await genshin_client.get_full_genshin_user(
                    config["settings"]["genshin_id"])
            main_dict["Genshin"] = {
                "Resin": gn.current_resin,
                "Until next 40": time_diff(
                    time_now, gn.resin_recovery_time, 8),
                "Dailies completed": "{}/{}".format(
                    gn.completed_commissions + int(gn.claimed_commission_reward),
                    "5"),
                "Remaining boss discounts": gn.remaining_resin_discounts,
                "Realm currency": gn.current_realm_currency,
                "Abyss progress": "{} {}".format(
                    gu.abyss.current.max_floor,
                    gu.abyss.current.total_stars),
            }
    except KeyError:
        pass

    try:
        if config["settings"]["hsr_id"]:
            # Get HSR info
            hsr_client = genshin.Client(cookies, game=genshin.Game.STARRAIL)
            hn = await hsr_client.get_starrail_notes()
            hu = await hsr_client.get_starrail_challenge(
                    config["settings"]["hsr_id"])
            moc_floors = [floor.name for floor in hu.floors]
            main_dict["HSR"] = {
                "Trailblaze power": hn.current_stamina,
                "Until next 40": time_diff(
                    time_now, hn.stamina_recovery_time, 6),
                "Dailies completed": "{}/{}".format(
                    hn.current_train_score // 100,
                    "5"
                    ),
                "Remaining boss discounts": hn.remaining_weekly_discounts,
                "SU weekly score": "{}/{}".format(hn.current_rogue_score,
                                                  hn.max_rogue_score),
                "MoC progress": "{} {}".format(
                    len(moc_floors),
                    hu.total_stars),
            }
    except KeyError:
        pass

    # Write dictionary to json file
    with open(cache_file, "w") as json_file:
        json_file.write(json.dumps(main_dict, indent=4))

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
with open(cache_file) as json_file:
    cache = json.load(json_file)

text = []
tooltip = []

if not cache:
    config_fail()
    exit(0)

for game, data in cache.items():

    if game == "Genshin":
        dailies = int(data["Dailies completed"].split("/")[0])
        # Set color based on status
        if dailies < 5 and data["Realm currency"] >= 2000:
            icon = "<span color=\"#d08770\"> </span>"
        elif data["Realm currency"] >= 2000:
            icon = "<span color=\"#ebcb8b\"> </span>"
        elif dailies < 5:
            icon = "<span color=\"#bf616a\"> </span>"
        else:
            icon = "  "
        text.append(icon + str(data["Resin"]))
    elif game == "HSR":
        su_points = int(data["SU weekly score"].split("/")[0])
        su_max = int(data["SU weekly score"].split("/")[1])
        dailies = int(data["Dailies completed"].split("/")[0])
        if dailies < 5:
            icon = "<span color=\"#bf616a\"> </span>"
        elif su_points < su_max and datetime.today().weekday() >= 5:
            icon = "<span color=\"#ebcb8b\"> </span>"
        else:
            icon = " "
        text.append(icon + str(data["Trailblaze power"]))

    # Create tooltip
    tooltip.append(
            ("<span color='#8fa1be' font_size='16pt'>"
             "{} Stats</span>\n").format(game) +
            '\n'.join(
                '{}: {}'.format(key, value) for key, value in data.items()))

# Print output as json
print(json.dumps({"text": "  ".join(text), "tooltip": "\n\n".join(tooltip)}))
