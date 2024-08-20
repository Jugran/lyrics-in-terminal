from pathlib import Path

CACHE_PATH = Path.home().joinpath('.cache', 'lyrics')

CONFIG_PATH = Path.home().joinpath('.config', 'lyrics-in-terminal', 'lyrics.cfg')

__version__ = '1.6.0'

if not CONFIG_PATH.exists():
    from shutil import copy
    import os

    dirname = Path(__file__).parent
    src = dirname.joinpath('lyrics.cfg')

    if not CONFIG_PATH.parent.exists():
        os.makedirs(CONFIG_PATH.parent)

    copy(src, CONFIG_PATH)
