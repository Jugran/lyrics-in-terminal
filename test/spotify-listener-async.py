import curses
import sys
import _curses
import traceback
import asyncio
import _curses
import _asyncio
import logging

from time import sleep

import dbus_next

BUS_NAME = 'org.mpris.MediaPlayer2.spotify'
OBJECT_PATH = '/org/mpris/MediaPlayer2'
INTERFACE = 'org.freedesktop.DBus.Properties'
DISPLAY = None
PLAYER = None


# Configure the logger
logging.basicConfig(
    filename='debug.log',          # Name of the log file
    level=logging.DEBUG,         # Set the logging level
    filemode='w',
    # Log message format
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
LOGGER = logging.getLogger(__name__)


class Track:
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist
        self.trackid = ''
        self.status = '-'
        self.task = None

    async def update(self, title, artist):
        self.title = title
        self.artist = artist
        self.status = f'fetching lyrics for {self.title} ...'

        if self.task is not None:
            self.task.cancel()
        self.task = asyncio.create_task(self.fetch_lyrics())
    
    async def fetch_lyrics(self):
        await asyncio.sleep(5)
        self.status = f'lyrics fetched! for {self.title}'



def parse_variant_to_dict(variant):
    """Convert a dbus-next Variant type to a Python dictionary."""
    if not isinstance(variant, dbus_next.Variant):
        raise ValueError("Provided object is not a dbus-next Variant.")

    value = variant.value
    if isinstance(value, dict):
        return {k: parse_variant_to_dict(v) if isinstance(v, dbus_next.Variant) else v for k, v in value.items()}
    elif isinstance(value, list):
        return [parse_variant_to_dict(v) if isinstance(v, dbus_next.Variant) else v for v in value]
    else:
        return value

class DbusListener:
    def __init__(self, bus_name, object_path, interface, display, loop: asyncio.AbstractEventLoop):
        self.bus_name = bus_name
        self.object_path = object_path
        self.interface = interface
        self.display = display

        self.bus = None
        self.player_object = None
        self.loop = None

    async def properties_changed(self, interface, changed, invalidated):
        # LOGGER.info(f'properties changed: {str(changed)}')

        metadata = changed.get('Metadata', None)  # dict

        if metadata is not None:
            metadata = parse_variant_to_dict(metadata)
        # -> string = Playing | Paused

        # PlaybackStatus and metadata can be absent from changed dict
        playback_status = changed.get('PlaybackStatus', None)

        if playback_status is not None:
            playback_status = parse_variant_to_dict(playback_status)

        # if self.update is not None:
        #     self.update(metadata, playback_status)

        data = {
            "title": '',
            "artist": '',
        }

        if metadata is None:
            LOGGER.info('metadata is None')
            await self.display.update(playback_status, metadata)
            return

        try:
            title = metadata['xesam:title']
            if title.strip() == '':
                # if Title is empty, don't update
                return

            artist = metadata['xesam:artist']
            artist = artist[0] if isinstance(artist, list) else artist

            data['title'] = title
            data['artist'] = artist
        except (IndexError, KeyError) as e:
            return

        if self.display is not None:
            await self.display.update(playback_status, data)

        LOGGER.info(f'metadata sent!: {data}')

    async def start_listener(self):
        LOGGER.info('start listening')
        self.loop = asyncio.get_event_loop()

        LOGGER.info('event loop found' + str(self.loop))

        self.bus = await dbus_next.aio.MessageBus().connect()
        introspection = await self.bus.introspect(self.bus_name, self.object_path)
        try:
            proxy_obj = self.bus.get_proxy_object(
                self.bus_name, self.object_path, introspection)

            self.player_object = proxy_obj.get_interface(
                'org.mpris.MediaPlayer2.Player')

            self.interface = proxy_obj.get_interface(
                'org.freedesktop.DBus.Properties')

            self.interface.on_properties_changed(self.properties_changed)
            LOGGER.info('listener started')

        except dbus_next.errors.DBusError:
            traceback.print_exc()
            print("Error occured")
            sys.exit(1)

        # try:
        #     LOGGER.info('start loop')
        #     await self.loop.create_future()
        # except KeyboardInterrupt:
        #     print("Thread: KeyboardInterrupt")


class Player(DbusListener):
    def __init__(self, player_name, display, loop=None):
        self.player_name = player_name
        super().__init__(BUS_NAME, OBJECT_PATH, INTERFACE, display, loop)


class Display:
    def __init__(self, stdscr: "_curses._CursesWindow"):
        self.stdscr = stdscr

        # TODO: add write lock for track
        self.track = Track('', '')
        self.status = '-'

        self.height, self.width = stdscr.getmaxyx()
        self.line = self.height // 2

        # curses.use_default_colors()
        self.stdscr.clear()
        curses.curs_set(0)
        self.refresh_screen()

    async def update(self, status, metadata):
        refresh = False
        self.status = 'updating data...'

        if status is not None and self.status != status:
            self.status = status
            refresh = True

        if metadata is None:
            if refresh:
                self.refresh_screen()
            return

        title = metadata.get('title')
        artist = metadata.get('artist')

        if self.track.title != title:
            # update track
            await self.track.update(title, artist)
            refresh = True

        if refresh:
            self.refresh_screen()

        if self.status is None or self.status == 'updating data...':
            self.status = 'Updated'

    def refresh_screen(self):
        self.stdscr.erase()

        title = self.track.title
        artist = self.track.artist
        status = self.status
        track_status = self.track.status

        self.stdscr.addstr(0, 1, title, curses.A_REVERSE)
        self.stdscr.addstr(1, 1, artist, curses.A_REVERSE |
                           curses.A_BOLD | curses.A_DIM)
        self.stdscr.addstr(2, 1, status, curses.A_REVERSE)
        self.stdscr.addstr(2, self.width // 2, track_status, curses.A_REVERSE)

        text = ' <cursor line> '
        center = (self.width - len(text)) // 2
        self.stdscr.addstr(self.line, center, text, curses.A_REVERSE)
        self.stdscr.addstr(self.height - 1, 1, 'Press q to quit', curses.A_DIM)

        self.stdscr.refresh()

    async def main(self):
        # wait for key input to exit
        # self.stdscr.nodelay(True)
        self.stdscr.timeout(-1)

        while True:
            key = await asyncio.to_thread(self.stdscr.getch)

            if key == ord('q') and PLAYER is not None:
                return

            self.height, self.width = self.stdscr.getmaxyx()

            # if key == curses.ERR:
            #     await asyncio.sleep(0.1)

            if key == curses.KEY_UP:
                self.line = max(4, self.line - 1)
            elif key == curses.KEY_DOWN:
                self.line = min(self.line + 1, self.height - 2)

            self.refresh_screen()


def ErrorHandler(func):
    def wrapper(*args, **kwargs):
        try:
            curses.wrapper(func)
        except KeyboardInterrupt:
            pass
        except curses.error as err:
            print('Please increase terminal window size!')
        except:
            print('Unexpected exception occurred.', sys.exc_info())

    return wrapper


@ErrorHandler
def start(stdscr):
    global DISPLAY
    global PLAYER

    LOGGER.info("Starting up...")

    DISPLAY = Display(stdscr)
    PLAYER = Player('spotify', DISPLAY)

    async def run():
        await asyncio.gather(
            DISPLAY.main(),
            PLAYER.start_listener()
        )
        # await PLAYER.start_listener()
        # await DISPLAY.main()

    asyncio.run(run())

if __name__ == '__main__':

    try:
        start()
    except KeyboardInterrupt:
        print("Host: KeyboardInterrupt")
