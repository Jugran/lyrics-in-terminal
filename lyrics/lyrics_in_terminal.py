#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from lyrics.config import Config
from lyrics.listener.player import Player
from lyrics.display.window import Window
import traceback

import sys
import curses


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
    defaults = Config('OPTIONS')

    if len(sys.argv) >= 2:
        player_name = sys.argv[1].strip()
        autoswitch = False

    else:
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

    player = Player(player_name, source, autoswitch, mpd_connect, align=align)
    win = Window(stdscr, player, timeout=interval)

    win.main()


def main():
    if len(sys.argv) >= 2:
        if sys.argv[1] == '-t':
            try:
                artist = sys.argv[2].strip()
                title = sys.argv[3].strip()
            except IndexError:
                print(
                    'Please provide track info in format "-t {artist} {title}".')
                exit(1)

            from lyrics.track import Track

            track = Track(artist=artist, title=title)
            track.get_lyrics('google')

            print(track.track_name)
            print('-' * track.width, '\n')
            print(track.get_text())

            exit(0)

    init_pager()


if __name__ == "__main__":
    main()
