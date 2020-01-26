#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lyrics import Track

import curses
import sys

#  TITLE_HEIGHT = 1
#  PADDING =1


class Window:
    def __init__(self, stdscr, track):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.track = track 
        self.scroll_pad = curses.newpad(track.length + 2, track.width + 2)
        self.current_pos = 0
        self.pad_offset = 1

        self.set_up()

    def set_track(self, track):
        self.track = track
        # redraw screen
        self.set_up()

    def set_up(self):
        self.stdscr.clear()
        curses.curs_set(0)
        self.current_pos = 0

        self.stdscr.addstr(0, 1, self.track.title, curses.A_REVERSE | curses.A_BOLD)
        self.stdscr.addstr(1, 1, track.artist, curses.A_REVERSE)
        self.scroll_pad.addstr(self.track.get_text())

        if track.justification == 0:
            # center align
            self.pad_offset = 1 + (self.width - self.track.width) // 2
           
        self.stdscr.refresh()
        self.scroll_pad.refresh(self.current_pos, 0, 3, self.pad_offset, self.height - 2, self.width - 1)

    def main(self):
        key = ''

        while (key != ord('q') or key != ord('Q')):
            key = self.stdscr.getch()

            self.height, self.width = self.stdscr.getmaxyx()

            if track.justification == 0 and key == curses.KEY_RESIZE:
                # center align
                self.pad_offset = 1 + (self.width - self.track.width) // 2
           
            self.stdscr.erase()
            self.stdscr.addstr(0, 1, self.track.title, curses.A_REVERSE | curses.A_BOLD)
            self.stdscr.addstr(1, 1, self.track.artist, curses.A_REVERSE)
            
            if key == curses.KEY_DOWN:
                if self.current_pos <= self.track.length * 0.6:
                    self.current_pos += 1
                else:
                    self.stdscr.addstr(self.height - 1, 0, 'END', curses.A_REVERSE)
            elif key == curses.KEY_UP:
                if self.current_pos > 0:
                    if self.current_pos >= self.track.length * 0.6:
                        self.stdscr.move(self.height - 1, 0)
                        self.stdscr.clrtoeol()
                    self.current_pos -= 1
            elif key == ord('q'):
                break

            self.stdscr.refresh()
            self.scroll_pad.refresh(self.current_pos, 0, 3, self.pad_offset, self.height - 2, self.width - 1)


def main(stdscr, track):
    win = Window(stdscr, track)
    win.main()

def start():
    curses.wrapper(main)

if __name__ == '__main__':

    if len(sys.argv) >= 5:
        artist = sys.argv[1].strip()
        title = sys.argv[2].strip()

        track = Track(artist, title, 1)
        track.get_lyrics()
        print(track.track_name)
        
        curses.wrapper(main, track)

    else:
        print('No Track info provided, Exiting...')
        exit
