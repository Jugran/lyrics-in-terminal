#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from lyrics.config import Config
from lyrics.player import Player
from lyrics.window import Window

import sys
import curses


def ErrorHandler(func):
    """
    Decorator to log exceptions.

    Args:
        func: (callable): write your description
    """
    def wrapper(*args, **kwargs):
        """
        Wraps a wrapper around the wrapped exceptions.

        Args:
        """
        try:
            curses.wrapper(func)
        except KeyboardInterrupt:
            pass
        except curses.error as err:
            print('Please increase terminal window size!')
        except:
            print('Unexpected exception occurred.', sys.exc_info()[0])

    return wrapper


@ErrorHandler
def start(stdscr):
    """
    Starts a new game.

    Args:
        stdscr: (str): write your description
    """
    defaults = Config('OPTIONS')

    if len(sys.argv) >= 2:
        player_name = sys.argv[1].strip()
    else:
        player_name = defaults['player'].strip()

    align = defaults['alignment']

    if align == 'center':
        align = 0
    elif align == 'right':
        align = 2
    else:
        align = 1

    interval = defaults['interval']
    source = defaults['source']

    player = Player(player_name, source, align=align)
    win = Window(stdscr, player, timeout=interval)

    win.main()


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        player_name = sys.argv[1].strip()
    else:
        player_name = 'spotify'

    # curses.wrapper(main, player_name, align=1)
    start(player_name, align=1)
