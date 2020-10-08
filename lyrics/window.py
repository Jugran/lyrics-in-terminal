#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lyrics.player import Player
from lyrics.config import Config

import curses


class Key:
	def __init__(self):
		self.binds = Config('BINDINGS')

	def input(self, window, key):
		if key == curses.KEY_RESIZE:
			window.update_track()
		elif key == self.binds['down']:
			window.scroll_down()
		elif key == self.binds['step-down']:
			window.scroll_down(self.binds['step-size'])
			window.stdscr.erase()
		elif key == self.binds['up']:
			window.scroll_up()
		elif key == self.binds['step-up']:
			window.scroll_up(self.binds['step-size'])
			window.stdscr.erase()

		elif key == self.binds['azlyrics']:
			window.player.refresh('azlyrics', cache=False)
			window.current_pos = 0
			window.update_track()
		elif key == self.binds['google']:
			window.player.refresh('google',cache=False)
			window.current_pos = 0
			window.update_track()
			
		# keys to change alignment
		elif key == self.binds['left']:
			window.player.track.alignment=1
			window.player.track.reset_width()
			window.update_track()
		elif key == self.binds['center']:
			window.player.track.alignment=0
			window.player.track.reset_width()
			window.update_track()
		elif key == self.binds['right']:
			window.player.track.alignment=2
			window.player.track.reset_width()
			window.update_track()

		elif key == self.binds['delete']:
			if window.player.track.delete_lyrics():
				window.stdscr.addstr(window.height - 1, window.width - 10,
							' Deleted ', curses.A_REVERSE)
		elif key == self.binds['help']:
			window.stdscr.erase()
			HelpPage(self.binds)
			window.height, window.width = window.stdscr.getmaxyx()
		elif key == ord('e'):
			curses.endwin()
			window.player.track.edit_lyrics()
			window.stdscr = curses.initscr()
			window.current_pos = 0
			window.player.refresh('google',cache=True)
			window.update_track()

class HelpPage:
	def __init__(self, keybinds):
		self.keybinds = keybinds
		self.options = Config('OPTIONS')

		self.win = curses.initscr()
		self.win.box()
		self.add_text()
		self.main()

	def add_config(self, i, j, config, _keys):
		# invert keys
		for k, v in config.items():
			# set representable strings to ascii values
			if v in _keys.keys():
				v = _keys[v]
			elif k != 'step-size' and k != 'interval':
				if isinstance(v, int):
					v = chr(v) # character values
			self.win.addstr(i, j, f'{k:15} {v}')
			# self.win.addstr(i, j, f'{k} \t {v}')
			i += 1
		return i

	def add_text(self):
		self.win.refresh()

		h, w = self.win.getmaxyx()
		self.win.addstr(3, 3, 'Help Page', curses.A_BOLD | curses.A_UNDERLINE)
		self.win.addstr(h - 2, 3, f"{'Press any key to exit...':>{w-5}}")

		keys = {  curses.KEY_UP : '↑',
			curses.KEY_DOWN : '↓',
			curses.KEY_LEFT: '←',
			curses.KEY_RIGHT: '→',
		}
		# keybinds
		i, j = 6, 3
		self.win.addstr(i, j, 'Keybindings', curses.A_UNDERLINE)
		i += 2
		i = self.add_config(i, j, self.keybinds, keys)
		# options
		if w // 2 >= 30:
			i, j = 6, w // 2 
		else:
			i += 2

		self.win.addstr(i, j, 'Default Options', curses.A_UNDERLINE)
		i+= 2
		self.add_config(i, j, self.options, keys)

	def main(self):
		# wait for key input to exit
		self.win.timeout(-1)
		self.win.getch()

		self.win.timeout(self.options['interval'])
		self.win.erase()


class Window:
	def __init__(self, stdscr, player, timeout):
		self.stdscr = stdscr
		self.height, self.width = stdscr.getmaxyx()
		self.player = player
		self.scroll_pad = curses.newpad(self.player.track.length + 2,
					self.player.track.width + 2)
		self.current_pos = 0
		self.pad_offset = 1
		self.text_padding = 5
		self.keys = Key()

		curses.use_default_colors()
		self.stdscr.timeout(timeout)
		self.set_up()

	def set_up(self):
		self.stdscr.clear()
		curses.curs_set(0)
		self.current_pos = 0

		if self.player.running:
			self.update_track()
			self.set_titlebar()
			self.stdscr.refresh()
			self.scroll_pad.refresh(self.current_pos, 0, 4, 
					self.pad_offset, self.height - 2, self.width - 1)
		else:
			 self.stdscr.addstr(0, 1, f'{self.player.player_name} is not running!')
			 self.stdscr.refresh()

	def set_titlebar(self):
		track_info = self.player.track.track_info(self.width - 1)
		# track_info -> ['title', 'artist', 'album'] - all algined
		self.stdscr.addstr(0, 1, track_info[0], curses.A_REVERSE)
		self.stdscr.addstr(1, 1, track_info[1], 
					curses.A_REVERSE | curses.A_BOLD | curses.A_DIM)
		self.stdscr.addstr(2, 1, track_info[2], curses.A_REVERSE)
		
	def set_offset(self):
		if self.player.track.alignment == 0:
				# center align
			self.pad_offset = (self.width - self.player.track.width) // 2
		elif self.player.track.alignment == 1:
			self.pad_offset = 2
		else:
			self.pad_offset = (self.width - self.player.track.width)
	
	def scroll_down(self, step=1):
		if self.current_pos < self.player.track.length - (self.height * 0.5):
			self.current_pos += step
		else:
			self.stdscr.addstr(self.height - 1, 1, 'END', curses.A_REVERSE)

	def scroll_up(self, step=1):
		if self.current_pos > 0:
			if self.current_pos >= self.player.track.length - \
				(self.height * 0.5):
				self.stdscr.move(self.height - 1, 0)
				self.stdscr.clrtoeol()
			self.current_pos -= step

	def update_track(self):
		self.stdscr.clear()
		self.scroll_pad.clear()

		if self.player.track.width > self.width - self.text_padding:
			text = self.player.track.get_text(wrap=True, 
						width=self.width - self.text_padding)
		else:
			text = self.player.track.get_text()

		pad_height = max(self.height, self.player.track.length) + 2
		pad_width = max(self.width, self.player.track.width) + 2

		self.scroll_pad.resize(pad_height, pad_width)
		self.scroll_pad.addstr(text)
		self.set_offset()	
		
	def main(self):
		key = ''

		while key != self.keys.binds['quit']:
			key = self.stdscr.getch()

			self.height, self.width = self.stdscr.getmaxyx()

			if key == -1:
				if self.player.update():
					self.current_pos = 0
					self.update_track()
					
			if self.player.running:
				self.keys.input(self, key)

				self.set_titlebar()
				self.stdscr.refresh()
				self.scroll_pad.refresh(self.current_pos, 0, 4, 
							self.pad_offset, self.height - 2, self.width - 1)
			else:
				self.stdscr.clear()
				self.stdscr.addstr(0, 1, f'{self.player.player_name} is not running!')
				self.stdscr.refresh()