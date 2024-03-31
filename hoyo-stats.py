#!/usr/bin/python3 -u
""" Show stats for Genshin and HSR in waybar module """
import sys
import asyncio
import json
from datetime import datetime, timezone
import os
import time
import configparser
import argparse
import requests
import genshin

cache_file = os.path.expanduser("~/.cache/hoyo-stats.json")
config_file = os.path.expanduser("~/.config/hoyo-stats.ini")


def get_args():
    """ Get arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-g', '--game', default='genshin', help='Game to get info for')
    args = parser.parse_args()
    return args


def get_config():
    """ Get or create config file """
    # Create config file if it doesn't exist
    if not os.path.exists(config_file):
        with open(config_file, "a", encoding='utf-8') as f:
            f.write("[settings]\nltuid = \nltoken = \ngenshin_id = ")
            f.close()
    # Load config from cache
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def wait_network() -> None:
    """ Wait for network connection """
    while True:
        try:
            requests.get('https://www.2dkun.xyz', timeout=3)
            return
        except requests.exceptions.ConnectionError:
            time.sleep(3)


def config_fail():
    """ Print info to waybar on fail """
    print(json.dumps({"text": ("Set up hoyo module in "
                               "~/.config/hoyo-stats.ini")}))


def time_diff(now, future, rate):
    """ Calculate time difference and return string """
    max_time = future - now
    until_next = (max_time.seconds // 60) % (rate * 40)
    return f"{until_next // 60}:{until_next % 60}"


def old(old, now, min_diff):
    """ Check age of datetime objects """
    diff = (datetime.now() - old).total_seconds()
    if diff > 60*min_diff:
        return True
    return False


async def generate_cache(config, game):
    """ Main function """
    wait_network()
    cookies = {
            "ltuid": config["settings"]["ltuid"],
            "ltoken": config["settings"]["ltoken"]
            }
    # Get current time
    time_now = datetime.now(timezone.utc)

    with open(cache_file, encoding='utf-8') as json_file:
        cache = json.load(json_file)

    if game == 'genshin':
        try:
            if old(
                datetime.fromtimestamp(cache['Genshin']['timestamp']),
                time_now, 5
            ):
                raise ValueError
        except (KeyError, ValueError):
            # Get genshin info
            genshin_client = genshin.Client(cookies)
            genshin_notes = await genshin_client.get_notes()
            genshin_user = await genshin_client.get_full_genshin_user(
                    config["settings"]["genshin_id"])
            com_prog = genshin_notes.completed_commissions + \
                int(genshin_notes.claimed_commission_reward)
            cache['Genshin'] = {
                "Resin": genshin_notes.current_resin,
                "Until next 40": time_diff(
                    time_now, genshin_notes.resin_recovery_time, 8),
                "Dailies completed": f"{com_prog}/5",
                "Remaining boss discounts":
                genshin_notes.remaining_resin_discounts,
                "Realm currency": genshin_notes.current_realm_currency,
                "Abyss progress": (
                    f"{genshin_user.abyss.current.max_floor} "
                    f"{genshin_user.abyss.current.total_stars}"
                    ),
                "timestamp": datetime.timestamp(time_now)
            }

    if game == 'hsr':
        try:
            if old(
                datetime.fromtimestamp(cache['HSR']['timestamp']),
                time_now, 5
            ):
                raise ValueError
        except (KeyError, ValueError):
            # Get HSR info
            hsr_client = genshin.Client(cookies, game=genshin.Game.STARRAIL)
            hsr_notes = await hsr_client.get_starrail_notes()
            hsr_user = await hsr_client.get_starrail_challenge(
                    config["settings"]["hsr_id"])
            moc_floors = [floor.name for floor in hsr_user.floors]
            daily_prog = hsr_notes.current_train_score // 100
            cache["HSR"] = {
                "Trailblaze power": hsr_notes.current_stamina,
                "Until next 40":
                time_diff(time_now, hsr_notes.stamina_recovery_time, 6),
                "Dailies completed": f"{daily_prog}/5",
                "Remaining boss discounts":
                hsr_notes.remaining_weekly_discounts,
                "SU weekly score":
                f"{hsr_notes.current_rogue_score}/"
                f"{hsr_notes.max_rogue_score}",
                "MoC progress": f"{len(moc_floors)} {hsr_user.total_stars}",
                "timestamp": datetime.timestamp(time_now)
            }

    # Write dictionary to json file
    with open(cache_file, "w", encoding='utf-8') as file:
        file.write(json.dumps(cache, indent=4))

    return cache


def get_cache(config, game):
    """ Generate cache if necessary """
    try:
        mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        mod_seconds = (datetime.now() - mod_time).total_seconds()
        if mod_seconds > 60*2:
            raise ValueError
    except (FileNotFoundError, ValueError):
        try:
            asyncio.run(generate_cache(config, game))
        except genshin.errors.GenshinException:
            time.sleep(5)
    with open(cache_file, encoding='utf-8') as json_file:
        return json.load(json_file)


def genshin_module(cache):
    """ Generate waybar output for Genshin """
    output = {}
    dailies = cache["Dailies completed"].split("/")
    dailies_completed = int(dailies[0]) == int(dailies[1])
    realm_currency_capped = cache['Realm currency'] >= 2000

    if not dailies_completed and not realm_currency_capped:
        output['class'] = 'red'
    if dailies_completed and realm_currency_capped:
        output['class'] = 'yellow'
    if not dailies_completed and realm_currency_capped:
        output['class'] = 'orange'

    output['text'] = f" {cache['Resin']}"

    cache.pop('timestamp')
    output['tooltip'] = (
        "<span color='#8fa1be' font_size='16pt'>"
        "Genshin Stats</span>\n") + '\n'.join(
            f'{key}: {value}' for key, value in cache.items()
    )
    return output


def hsr_module(cache):
    """ Generate waybar output for HSR """
    output = {}
    dailies = cache["Dailies completed"].split("/")
    dailies_completed = int(dailies[0]) == int(dailies[1])

    if not dailies_completed:
        output['class'] = 'red'

    output['text'] = f" {cache['Trailblaze power']}"

    cache.pop('timestamp')
    output['tooltip'] = (
        "<span color='#8fa1be' font_size='16pt'>"
        "HSR Stats</span>\n") + '\n'.join(
            f'{key}: {value}' for key, value in cache.items()
    )
    return output


def main():
    """ Main function """
    args = get_args()
    config = get_config()
    cache = asyncio.run(generate_cache(config, args.game))

    if args.game == "genshin":
        output = genshin_module(cache['Genshin'])
    elif args.game == "hsr":
        output = hsr_module(cache['HSR'])
    else:
        output = {"text": "Invalid game specified"}

    print(json.dumps(output))


if __name__ == "__main__":
    main()
