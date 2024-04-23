# thnikk's waybar modules
These are my custom waybar modules. Some of these are for specific hardware or software, so they might not be useful to you.

## Modules
All modules need to be defined in your config and then added to your bar.

### Clock
This module replaces the built-in clock module. The calendar tooltip shows events defined in `~/.config/calendar-events.json`.Clicking on the bar will hide event notifications for the current day and right-clicking will unhide it.
``` json
    "custom/clock":{
        "format": "{}",
        "tooltip": true,
        "exec": "~/.local/bin/bar/clock.py",
        "on-click": "touch ~/.cache/hide-calendar-notification",
        "on-click-right": "rm ~/.cache/hide-calendar-notification",
        "return-type": "json"
    },
```

### OBS
Shows the current scene and recording status. Requires OBS to be built with websocket support (not enabled in the official arch package).

#### Dependencies
- `python-obs-websocket`
- `obs-studio-git`
``` json
    "custom/obs":{
        "format": "{}",
        "tooltip": true,
        "exec": "~/.local/bin/bar/obs.py",
        "return-type": "json",
        "interval": 1
    },
```

### UPS
The UPS module requires a vendor and product ID for your UPS. You can optionally give it an offset value with `-o` to offset the value shown on the bar.

#### Dependencies

- `python-hid`
``` json
    "custom/ups":{
        "format": "{}",
        "tooltip": true,
        "exec": "~/.local/bin/bar/ups.py 0764 0501 -o 160",
        "return-type": "json",
        "interval": 10
    },
```

### Privacy
Shows when microphones, webcams, and screensharing is used. Replaces the stock privacy module that (currently) breaks waybar and also adds webcam functionality.
``` json
    "custom/privacy":{
        "format": "{}",
        "tooltip": true,
        "exec": "~/.local/bin/bar/privacy.py",
        "return-type": "json",
        "interval": 10
    },
```

### Systemd Failed
Shows number of failed systemd services and shows failed services by category in tooltip. Also replaces built-in module to add tooltip functionality. Services can be excluded with the `-e` flag and accepts a comma-separated list.
``` json
    "custom/systemd-failed":{
        "format": "{}",
        "tooltip": true,
        "exec": "~/.local/bin/bar/systemd-failed.py -e 'reflector'",
        "return-type": "json",
        "interval": 10
    },
```

### XDrip
Interfaces with XDrip+ using the web service API to show blood sugar. Module color changes based on the sgv and turns gray if the value is stale if the module is unable to connect to the web API.
``` json
    "custom/xdrip":{
        "format": "{}",
        "tooltip": true,
        "exec": "~/.local/bin/bar/beetus.py",
        "return-type": "json",
        "interval": 5
    },
```

### Hoyo stats
Shows stats for Genshin Impact or HSR including resin, time to next 40 resin, daily completion, weekly boss progress, realm currency, and Spiral Abyss progress (and rough analogs for HSR). Resin is shown on bar and color changes based on daily completion and realm currency level. Accepts `genshin` or `hsr` used with `-g` to select a game (defaults to genshin if unset and requires the game ID to be set in the config.)

This module requires extra setup as it depends on a virtual environment:

1) Create a virtualenv with `python -m venv ~/.venv/hoyo-stats`
2) Install libraries with `~/.venv/hoyo-stats/bin/pip install requests genshin`
3) Run the script once with `~/.venv/hoyo-stats/bin/python ~/.local/bin/bar/hoyo-stats.py` to create a config file in `~/.config/hoyo-stats.ini`. Edit the config and add your [cookies](https://thesadru.github.io/genshin.py/authentication/#how-can-i-get-my-cookies) and game ID.
``` json
    "custom/genshin-stats":{
	"format": "{}",
	"tooltip": true,
	"exec": "~/.venv/hoyo-stats/bin/python ~/.local/bin/bar/hoyo-stats.py",
	"return-type": "json",
	"interval": 60
    },
```

### Weather
Shows weather using the OpenMeteo API. Accepts a zip code as location and has an optional flag `-n` to use moon icons at night.
``` json
    "custom/weather-new": {
        "format": "{}",
        "exec": "~/.local/bin/bar/weather-new.py -n 94002",
        "on-click": "~/.local/bin/bar/widgets/toggle-weather.sh",
        "return-type": "json",
        "interval": 600
    },
```

### Updates
Shows available package updates.
``` json
    "custom/updates": {
        "exec": "~/.local/bin/bar/updates.py",
        "format": "{}",
        "on-click": "kitty zsh -c 'paru; flatpak update; pkill -RTMIN+1 waybar; echo Press enter to close terminal.; read'",
        "return-type": "json",
        "signal": 1,
        "interval": 600
    },
```

### Git updates
Shows available updates to Git repo. This repo is used in the example.
``` json
    "custom/git-updates": {
        "format": "{}",
        "exec": "~/.local/bin/bar/git-updates.py ~/.local/bin/bar",
        "return-type": "json",
        "interval": 3000
    },
```

### VM
Shows running libvirt VMs and lists them in the tooltip.
``` json
    "custom/vm": {
        "format": "{}",
        "exec": "~/.local/bin/bar/vm.py",
        "return-type": "json",
        "signal": 2,
        "interval": "once"
    },
```

### Battery
Shows combined battery percentage for multiple batteries. Made for Thinkpads with 2 batteries.
``` json
    "custom/battery": {
        "format": "{}",
        "exec": "~/.local/bin/bar/battery.py BAT",
        "return-type": "json",
        "interval": 60
    },
```
