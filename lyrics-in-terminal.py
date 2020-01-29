#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from player import Player

import curses
import sys

#   TODO: text wrap for long lines 
#   DEUTSCHLAND, somewhere i belong - good test cases

class Window:
    def __init__(self, stdscr, player, timeout=1500):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.player = player
        self.scroll_pad = curses.newpad(self.player.track.length + 2, self.player.track.width + 2)
        self.current_pos = 0
        self.pad_offset = 1

        curses.use_default_colors()
        self.stdscr.timeout(timeout)
        
        self.set_up()

    def set_up(self):
        self.stdscr.clear()
        curses.curs_set(0)
        self.current_pos = 0

        if self.player.running:
            self.set_titlebar()
            self.scroll_pad.addstr(self.player.track.get_text())
            self.set_offset()

            self.stdscr.refresh()
            self.scroll_pad.refresh(self.current_pos, 0, 4, self.pad_offset, self.height - 2, self.width - 1)
        else:
             self.stdscr.addstr(0, 1, f'{self.player.player_name} is not running!')
             self.stdscr.refresh()

    def set_titlebar(self):

        self.stdscr.addstr(0, 1, self.player.track.title.center(self.width - 1), curses.A_REVERSE)
        self.stdscr.addstr(1, 1, self.player.track.artist.center(self.width - 1), curses.A_REVERSE | curses.A_BOLD | curses.A_DIM)
        self.stdscr.addstr(2, 1, self.player.track.album.center(self.width - 1), curses.A_REVERSE | curses.A_ITALIC)
        

    def set_offset(self):
        if self.player.track.justification == 0:
                # center align
            self.pad_offset = (self.width - self.player.track.width) // 2
        elif self.player.track.justification != 1:
            self.pad_offset = (self.width - self.player.track.width) - 2

    def scroll_up(self, step=1):
        if self.current_pos <= self.player.track.length * 0.8:
            self.current_pos += step
        else:
            self.stdscr.addstr(self.height - 1, 1, 'END', curses.A_REVERSE)

    def scroll_down(self, step=1):
        if self.current_pos > 0:
            if self.current_pos >= self.player.track.length * 0.8:
                self.stdscr.move(self.height - 1, 0)
                self.stdscr.clrtoeol()
            self.current_pos -= step

    def main(self):
        key = ''

        while key != ord('q') and key != ord('Q'):
            key = self.stdscr.getch()

            self.height, self.width = self.stdscr.getmaxyx()

            if key == -1:
                if self.player.update():
                    self.stdscr.clear()
                    self.scroll_pad.clear()
                    self.scroll_pad.resize(self.player.track.length + 2, self.player.track.width + 2)
                    self.scroll_pad.addstr(self.player.track.get_text())
                    self.current_pos = 0
                    key = curses.KEY_RESIZE

            if self.player.running:
                if key == curses.KEY_RESIZE:
                    self.stdscr.clear()
                    self.set_offset()

                if key == curses.KEY_DOWN:
                    self.scroll_up()
                elif key == curses.KEY_RIGHT:
                    self.scroll_up(5)
                    self.stdscr.erase()
                elif key == curses.KEY_UP:
                    self.scroll_down()
                elif key == curses.KEY_LEFT:
                    self.scroll_down(5)
                    self.stdscr.erase()

                # keys to change alignment
                # j = left | k = center | l = right

                self.set_titlebar()
                self.stdscr.refresh()
                self.scroll_pad.refresh(self.current_pos, 0, 4, self.pad_offset, self.height - 2, self.width - 1)
            else:
                self.stdscr.clear()
                self.stdscr.addstr(0, 1, f'{self.player.player_name} is not running!')
                self.stdscr.refresh()


def main(stdscr, player_name, **kwargs):
    player = Player(player_name, **kwargs)

    win = Window(stdscr, player, timeout=2000)
    #curses.cbreak()
    # win.stdscr.timeout(1500)

    win.main()


def start(player_name, **kwargs):
    curses.wrapper(main, player_name, **kwargs)


if __name__ == '__main__':

    if len(sys.argv) > 1:
        player_name = sys.argv[1].strip()
    else:
        player_name = 'spotify'

    start(player_name, justify=0)
