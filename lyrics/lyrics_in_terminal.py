#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import curses
import traceback
import sys

import _curses

from lyrics.listener.base import PlayerBase
from lyrics.listener.dbus import DbusListener
from lyrics.display.window import Window
from lyrics.config import Config
from lyrics.track import Track
from lyrics import Logger


class LyricsInTerminal:
    def __init__(self, stdscr: "_curses._CursesWindow|None" = None, stdout_mode=False):
        self.stdscr = stdscr
        self.player: PlayerBase = None
        self.window: Window = None
        self.track: Track = None

        if stdout_mode:
            return

        self.init()

    def init(self):
        ''' Initialize the lyrics app.
        '''
        Logger.info('Initializing lyrics app...')
        defaults = Config('OPTIONS')

        player_name = defaults['player'].strip()
        autoswitch = defaults.getboolean('autoswitch')

        align = defaults['alignment']

        if align == 'center':
            align = 0
        elif align == 'right':
            align = 2
        else:
            align = 1

        interval = defaults['interval']
        source = defaults['source']
        mpd_connect = [defaults['mpd_host'],
                       defaults['mpd_port'], defaults['mpd_pass']]

        self.track = Track(align=align)

        # TODO: add os platform check here
        self.player = DbusListener(controller=self, name=player_name,
                             source=source, autoswitch=autoswitch,
                             track=self.track)
        self.window = Window(controller=self, stdscr=self.stdscr,
                             timeout=interval, track=self.track)

    async def start(self):
        Logger.info('Starting lyrics pager...')
        
        await asyncio.gather(
            self.window.main(),
            self.player.main(),
            )

    def stdout_lyrics(self):
        Logger.info('STDOUT lyrics mode...')
        try:
            artist = sys.argv[2].strip()
            title = sys.argv[3].strip()
        except IndexError:
            print(
                'Please provide track info in format "-t {artist} {title}".')
            exit(1)

        track = Track(artist=artist, title=title)
        track.get_lyrics(source='any')

        print(track.track_name)
        print('-' * track.width, '\n')
        print(track.get_text())

        Logger.info('Lyrics printed. Exiting...')
        exit(0)

    async def update_track(self, playback_status=None, metadata=None):
        Logger.info(f'Updating track...{playback_status} {metadata}')
        if playback_status is not None:
            pass

        if metadata is not None:
            self.track.update(**metadata)
            self.track.get_lyrics(source='any')

            # TODO: combine update and refresh
            self.window.update_track()
            self.window.refresh_screen()


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
    asyncio.run(lyrics.start())


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == '-t':
        lyrics = LyricsInTerminal(stdout_mode=True)
        lyrics.stdout_lyrics()
    else:
        init_pager()


if __name__ == "__main__":
    main()
