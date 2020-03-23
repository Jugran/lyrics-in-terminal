#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from .config import Config
from .player import Player
from .window import Window

import sys
import curses


def main(stdscr):
	defaults=Config('OPTIONS')

	if len(sys.argv) >= 2:
		player_name=sys.argv[1].strip()
	else:
		player_name=defaults['player'].strip()

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

def start():
	curses.wrapper(main)


if __name__ == '__main__':
	if len(sys.argv) >= 2:
		player_name=sys.argv[1].strip()
	else:
		player_name='spotify'

	curses.wrapper(main, player_name, align=1)