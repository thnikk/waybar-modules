# thnikk's waybar modules
These are my custom waybar modules. Some of these are for specific hardware or software, so they might not be useful to you.

## Dependencies
Some modules depend on a shell program to function:

- updates.py: checkupdates, paru, flatpak (will only show updates if program is installed)
- ups.py: PowerPanel

## Signals
Waybar allows you to use signals to reload a module. This can help reduce unnecessary load on your system for modules that don't need to poll. A good example is the VM module, that can be updated through libvirt's qemu hook file. In this example, you'd add `pkill -RTMIN+1 waybar` to the hooks file. Other changes are required in the module config, which are:

```
"interval": "once",
"signal": 1
```

The values for RTMIN+1 and signal need to match.

## Common library

I've made a common library to reduce redundant code and make new modules easier to write.

### Printing debug info

You can print debug info with print_debug(), which will print to stderr in the same format as waybar. You can either run waybar in a terminal or redirect the output to a log file with `waybar > ~/.cache/waybar.log 2>&1`.

### Using cache

I made a cache class to simplify caching. You can use it like this:

```
import requests
from common import Cache

cache = Cache('/path/to/cache.json')

data = cache.load()
response = requests.get('https://wttr.in/?format=j1', timeout=3).json()

if data != response:
    cache.save(response)
```
