from pathlib import Path

CACHE_PATH = Path.home().joinpath('.cache', 'lyrics')

CONFIG_PATH = Path.home().joinpath('.config', 'lyrics-in-terminal', 'lyrics.cfg')

__version__ = '1.7.0'

if CONFIG_PATH.exists():
    # Update the config file with any missing keys from the defaults.
    from configparser import ConfigParser

    old_config = ConfigParser()
    old_config.read(CONFIG_PATH)

    new_config = ConfigParser()
    new_config.read('lyrics/lyrics.cfg')

    skip = True

    for section in old_config.sections():
        old_keys = {o for o in old_config[section]}
        new_keys = {n for n in new_config[section]}
        changes = new_keys ^ old_keys

        if len(changes) == 0:
            continue
        else:
            skip = False

        for option in new_keys:
            fallback = new_config[section].get(option)
            new_config[section][option] = old_config[section].get(option, fallback)

    if not skip:
        with open(CONFIG_PATH, 'w') as file:
            new_config.write(file)

else:
    # create a new config file.
    from shutil import copy
    import os

    dirname = Path(__file__).parent
    src = dirname.joinpath('lyrics.cfg')

    if not CONFIG_PATH.parent.exists():
        os.makedirs(CONFIG_PATH.parent)

    copy(src, CONFIG_PATH)
