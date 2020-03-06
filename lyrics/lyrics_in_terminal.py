#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from player import Player

import curses
import sys


class Window:
	def __init__(self, stdscr, player, timeout=1500):
		self.stdscr = stdscr
		self.height, self.width = stdscr.getmaxyx()
		self.player = player
		self.scroll_pad = curses.newpad(self.player.track.length + 2,\
			self.player.track.width + 2)

		self.current_pos = 0
		self.pad_offset = 1
		self.text_padding = 5
		self.autoscroll = False

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
			self.scroll_pad.refresh(self.current_pos, 0, 4, \
				self.pad_offset, self.height - 2, self.width - 1)
		else:
			 self.stdscr.addstr(0, 1, f'{self.player.player_name} \
			 	is not running!')
			 self.stdscr.refresh()

	def set_titlebar(self):
		track_info = self.player.track.track_info(self.width - 1)
		# track_info -> ['title', 'artist', 'album'] - all algined
		self.stdscr.addstr(0, 1, track_info[0], curses.A_REVERSE)
		self.stdscr.addstr(1, 1, track_info[1], \
			curses.A_REVERSE | curses.A_BOLD | curses.A_DIM)
		self.stdscr.addstr(2, 1, track_info[2], curses.A_REVERSE)
		
	def set_offset(self):
		if self.player.track.alignment == 0:
				# center align
			self.pad_offset = (self.width - self.player.track.width) // 2
		elif self.player.track.alignment == 1:
			self.pad_offset = 2
		else:
			self.pad_offset = (self.width - self.player.track.width) - 2
	
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
			text = self.player.track.get_text(wrap=True, \
				width=self.width - self.text_padding)
		else:
			text = self.player.track.get_text()

		pad_height = max(self.height, self.player.track.length) + 2
		pad_width = max(self.width, self.player.track.width) + 2

		self.scroll_pad.resize(pad_height, pad_width)
		self.scroll_pad.addstr(text)
		self.set_offset()

	def input_key(self, key):
		if key == curses.KEY_RESIZE:
			self.update_track()
		elif key == curses.KEY_DOWN:
			self.scroll_down()
		elif key == curses.KEY_RIGHT:
			self.scroll_down(5)
			self.stdscr.erase()
		elif key == curses.KEY_UP:
			self.scroll_up()
		elif key == curses.KEY_LEFT:
			self.scroll_up(5)
			self.stdscr.erase()

		elif key == ord('r'):
			self.player.refresh('az')
			self.current_pos = 0
			self.update_track()
		elif key == ord('R'):
			self.player.refresh('google')
			self.current_pos = 0
			self.update_track()
			
		# keys to change alignment
		# j = left | k = center | l = right
		elif key == ord('j'):
			self.player.track.alignment=1
			self.update_track()
		elif key == ord('k'):
			self.player.track.alignment=0
			self.update_track()
		elif key == ord('l'):
			self.player.track.alignment=2
			self.update_track()

		elif key == ord('d'):
			if self.player.track.delete_lyrics():
				self.stdscr.addstr(self.height - 1, self.width - 10, \
				 ' Deleted ', curses.A_REVERSE)

	def main(self):
		key = ''

		while key != ord('q') and key != ord('Q'):
			key = self.stdscr.getch()

			self.height, self.width = self.stdscr.getmaxyx()

			if key == -1:
				if self.player.update():
					self.current_pos = 0
					self.update_track()
				elif self.autoscroll:
					# auto scroll
					pass
					
			if self.player.running:
				self.input_key(key)

				self.set_titlebar()
				self.stdscr.refresh()
				self.scroll_pad.refresh(self.current_pos, 0, 4, \
					self.pad_offset, self.height - 2, self.width - 1)
			else:
				self.stdscr.clear()
				self.stdscr.addstr(0, 1, f'{self.player.player_name} \
					is not running!')
				self.stdscr.refresh()


def main(stdscr, player_name, **kwargs):
	player = Player(player_name, **kwargs)

	win = Window(stdscr, player, timeout=1500)
	#curses.cbreak()
	# win.stdscr.timeout(1500)

	win.main()


def start(player_name=None):
	if player_name is None:
		if len(sys.argv) >= 2:
			player_name=sys.argv[1].strip()
		else:
			player_name='spotify'
	else:
		player_name = player_name.strip()

	curses.wrapper(main, player_name, align=1)


if __name__ == '__main__':
	if len(sys.argv) >= 2:
		player_name=sys.argv[1].strip()
	else:
		player_name='spotify'

	curses.wrapper(main, player_name, align=1)