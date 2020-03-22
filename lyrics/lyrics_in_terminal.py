#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from .config import Config
from .player import Player
from .window import Window

import sys


def main(stdscr, player_name, **kwargs):
	player = Player(player_name, **kwargs)
	win = Window(stdscr, player, timeout=1500)

	win.main()

def start():
	defaults=Config('OPTIONS')
	if len(sys.argv) >= 2:
		player_name=sys.argv[1].strip()
	else:
		player_name=defaults['player']

	align = defaults['alignment']

	if align == 'center':
		align = 0
	elif align == 'right':
		align = 2
	else:
		align = 1

	curses.wrapper(main, player_name, align=align)


if __name__ == '__main__':
	if len(sys.argv) >= 2:
		player_name=sys.argv[1].strip()
	else:
		player_name='spotify'

	curses.wrapper(main, player_name, align=1)