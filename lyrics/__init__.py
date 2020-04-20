from pathlib import Path

CACHE_PATH = Path.home().joinpath('.cache', 'lyrics')

CONFIG_PATH = Path.home().joinpath('.config', 'lyrics-in-terminal','lyrics.cfg')

__version__ = '1.2.0-dev'

if not CONFIG_PATH.exists():
    from shutil import copy
    import os

    dirname = Path(__file__).parent
    src = dirname.joinpath('lyrics.cfg')

    os.makedirs(CONFIG_PATH.parent)

    copy(src, CONFIG_PATH)
