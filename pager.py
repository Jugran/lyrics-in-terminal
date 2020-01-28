#!/usr/bin/env python
# -*- coding: utf-8 -*-

from player import Player

import curses
import sys

#TODO: text wrap for long lines 
# DEUTSCHLAND, somewhere i belong - good test cases

class Window:
    def __init__(self, stdscr, player):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.player = player
        self.scroll_pad = curses.newpad(self.player.track.length + 2, self.player.track.width + 2)
        self.current_pos = 0
        self.pad_offset = 1

        self.set_up()

    def set_up(self):
        self.stdscr.clear()
        curses.curs_set(0)
        self.current_pos = 0

        if self.player.running:
            self.stdscr.addstr(0, 1, self.player.track.title, curses.A_REVERSE | curses.A_BOLD)
            self.stdscr.addstr(1, 1, self.player.track.artist, curses.A_REVERSE)

            self.scroll_pad.addstr(self.player.track.get_text())

            if self.player.track.justification == 0:
                # center align
                self.pad_offset = (self.width - self.player.track.width) // 2
            elif self.player.track.justification != 1:
                self.pad_offset = (self.width - self.player.track.width) - 2

            self.stdscr.refresh()
            self.scroll_pad.refresh(self.current_pos, 0, 3, self.pad_offset, self.height - 2, self.width - 1)
        else:
             self.stdscr.addstr(0, 1, f'{self.player.player_name} is not running!')
             self.stdscr.refresh()

    def main(self):
        key = ''

        while key != ord('q') and key != ord('Q'):
            key = self.stdscr.getch()

            self.height, self.width = self.stdscr.getmaxyx()

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
                    if self.player.track.justification == 0:
                        # center align
                        self.pad_offset = (self.width - self.player.track.width) // 2
                    elif self.player.track.justification != 1:
                        self.pad_offset = (self.width - self.player.track.width) - 2

                #  self.stdscr.erase()
                self.stdscr.addstr(0, 1, self.player.track.title, curses.A_REVERSE | curses.A_BOLD)
                self.stdscr.addstr(1, 1, self.player.track.artist, curses.A_REVERSE)

                if key == curses.KEY_DOWN:
                    if self.current_pos <= self.player.track.length * 0.6:
                        self.current_pos += 1
                    else:
                        self.stdscr.addstr(self.height - 1, 0, 'END', curses.A_REVERSE)
                elif key == curses.KEY_UP:
                    if self.current_pos > 0:
                        if self.current_pos >= self.player.track.length * 0.6:
                            self.stdscr.move(self.height - 1, 0)
                            self.stdscr.clrtoeol()
                        self.current_pos -= 1

                self.stdscr.refresh()
                self.scroll_pad.refresh(self.current_pos, 0, 3, self.pad_offset, self.height - 2, self.width - 1)
            else:
                self.stdscr.clear()
                self.stdscr.addstr(0, 1, f'{self.player.player_name} is not running!')
                self.stdscr.refresh()


def main(stdscr, player_name, **kwargs):
    player = Player(player_name, **kwargs)

    win = Window(stdscr, player)
    #curses.cbreak()
    win.stdscr.timeout(500)
    win.main()


def start(player_name, **kwargs):
    curses.wrapper(main, player_name, **kwargs)


if __name__ == '__main__':

    if len(sys.argv) > 1:
        player_name = sys.argv[1].strip()
    else:
        player_name = 'spotify'

    start(player_name, justify=0)
