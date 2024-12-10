#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import curses
import traceback
import sys

import _curses
from lyrics.display.input import InputManager

from lyrics.listeners.base import PlayerBase
from lyrics.listeners.dbus import DbusListener
from lyrics.display.window import Window
from lyrics.config import Config
from lyrics.track import Track
from lyrics.sources import Source
from lyrics import Logger


class LyricsInTerminal:
    def __init__(self, stdscr: "_curses._CursesWindow" = None, stdout_mode=False):
        self.stdscr = stdscr
        self.player: PlayerBase | None = None
        self.window: Window | None = None
        self.track: Track | None = None
        self.input_manager: InputManager | None = None
        self.tasks = None
        self.timeout = -1

        if stdout_mode:
            return

        self.init()

    def init(self):
        ''' Initialize the lyrics app.
        '''
        Logger.info('Initializing lyrics app...')
        defaults = Config('OPTIONS')

        player_name = defaults['player'].strip()
        autoswitch = defaults.getboolean('autoswitch', False)

        align = defaults['alignment']

        if align == 'center':
            align = 0
        elif align == 'right':
            align = 2
        else:
            align = 1

        self.timeout = int(defaults['interval'])
        mpd_connect = [defaults['mpd_host'],
                       defaults['mpd_port'], defaults['mpd_pass']]

        source = defaults['source']
        source = Source(source)

        self.input_manager = InputManager(controller=self)

        self.track = Track(self, align=align, default_source=source)

        # TODO: add os platform check here
        self.player = DbusListener(controller=self, name=player_name,
                                   source=source, autoswitch=autoswitch,
                                   timeout=self.timeout)
        self.window = Window(controller=self)

    async def start(self):
        Logger.info('Starting lyrics pager...')

        self.window.main()
        self.tasks = asyncio.gather(
            self.player.main(),
            self.input_manager.main()
        )

        await self.tasks

    async def stdout_lyrics(self):
        Logger.info('STDOUT lyrics mode...')
        try:
            artist = sys.argv[2].strip()
            title = sys.argv[3].strip()
        except IndexError:
            print(
                'Please provide track info in format "-t {artist} {title}".')
            exit(1)

        track = Track(None, artist=artist, title=title)
        await track._update_lyrics()

        print(track.track_name)
        print('-' * track.width, '\n')
        print(track.get_text())

        Logger.info('Lyrics printed. Exiting...')
        exit(0)

    def quit(self):
        Logger.info('Quitting...')

        if self.tasks is not None:
            self.tasks.cancel()

    def reinitialize_screen(self):
        Logger.info('Reinitializing screen...')
        self.stdscr = curses.initscr()
        self.window.main()

    async def update_track(self, playback_status=None, metadata=None):
        Logger.info(f'Updating track...{playback_status} {metadata}')
        if playback_status is not None:
            pass

        if metadata is not None:
            self.track.update(**metadata)
            self.window.refresh_titlebar()
            await self.track.update_lyrics()


def ErrorHandler(func):
    def wrapper(*args, **kwargs):
        try:
            curses.wrapper(func)
        except KeyboardInterrupt:
            pass
        except curses.error as err:
            print('Please increase terminal window size!')
        except Exception as err:
            print('Unexpected exception occurred.')
            traceback.print_exc()

    return wrapper


@ErrorHandler
def init_pager(stdscr=None):
    lyrics = LyricsInTerminal(stdscr)
    try:
        asyncio.run(lyrics.start())
    except asyncio.CancelledError:
        exit(1)


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == '-t':
        lyrics = LyricsInTerminal(stdout_mode=True)
        asyncio.run(lyrics.stdout_lyrics())
    else:
        init_pager()


if __name__ == "__main__":
    main()
