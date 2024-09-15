import logging

from pathlib import Path

__version__ = '1.8.0-dev'

CACHE_PATH = Path.home().joinpath('.cache', 'lyrics_dev')
CONFIG_PATH = Path.home().joinpath('.config', 'lyrics-in-terminal', 'lyrics.cfg')
# LOG_PATH = '/var/log/lyrics_in_terminal/debug.log'
LOG_PATH = 'debug.log'

if not CONFIG_PATH.exists():
    from shutil import copy
    import os

    dirname = Path(__file__).parent
    src = dirname.joinpath('lyrics.cfg')

    if not CONFIG_PATH.parent.exists():
        os.makedirs(CONFIG_PATH.parent)

    copy(src, CONFIG_PATH)



# Configure the logger
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
Logger = logging.getLogger(__name__)