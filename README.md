# thnikk's waybar modules
These are my custom waybar modules. Some of these are for specific hardware or software, so they might not be useful to you. I don't plan to make these any more universal, but feel free to submit a PR if you want to add some cool functionality. 

## Dependencies
Some modules depend on a shell program to function:

- updates.py: checkupdates, paru
- ups.py: powerpanel

## Signals
Waybar allows you to use signals to reload a module. This can help reduce unnecessary load on your system for modules that don't need to poll. A good example is the VM module, that can be updated through libvirt's qemu hook file. In this example, you'd add `pkill -RTMIN+1 waybar` to the hooks file. Other changes are required in the module config, which are:

```
"interval": "once",
"signal": 1
```

The values for RTMIN+1 and signal need to match.

## Useful libraries

If you want to make your own custom module, here are some useful libraries.

### Subprocess
You may want to use the output of a shell program instead of relying on a library. An example of this is `updates.py`, since it makes more sense to use the installed package manager. 

We can capture the output of a program like this. I'm using `uname -romi` in this example.

```
subprocess.run(["uname", "-romi"]), check=False, capture_output=True).stdout.decode('utf-8')
```

This will return a string, so you can use the output directly or continue parsing if necessary.

### Json
The json library is a versatile tool for managing data. It's a very easy way of caching API responses as well as a normal dictionary. It can be used for configuration, but unless you need more complex configuration, configparser is probably the way to go.

The most useful things to do with the json library are saving a dictionary to a json file:

```
with open("file.json) as cache:
    cache.write(json.dumps(data))
```

And loading a dictionary from a file:

```
with open("file.json") as cache:
    data = json.load(cache)
```

The other useful thing is to print a dictionary for waybar to use with json.dumps:

```
output_dictionary = {"text": "This is on the bar", "tooltip": "This is in the tooltip"}
print(json.dumps(output_dictionary))
```

### Configparser
For a config with simple key value pairs, configparser is a great choice. 

I like to create the config file if it doesn't exist:

```
# Define config location
config_file = os.path.expanduser("~/.config/module.ini")
# Check for config file and create one if it doesn't exist
if not os.path.exists(config_file):
    f = open(config_file, "a")
    f.write("[settings]\thing1 = \nthing2 = \nthing3 = ")
    f.close()
```

You then need to load the config into a variable:

```
config = configparser.ConfigParser()
config.read(config_file)
```

You can then use any of your configuration as a dictionary. In this example, since we have thing1 in the settings section, we'd use `config["settings"]["thing1"]`.


### Argparse
This one is a little niche, but I basically use it as a way to do very simple configuration without a config file. battery.py is a good example, where it's just simpler to get the search name for the battery through an argument than creating a config file.

```
parser = argparse.ArgumentParser(description="Description of module")
parser.add_argument('text', action='store', type=str, help='Description of argument')
args = parser.parse_args()
```

To use the argument, you'd just use `args.text` like you would any other variable.
