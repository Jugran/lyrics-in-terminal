#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lyrics.display.key import Key

import curses


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
        """
        Set up the initial state of the application.

        Clears the standard screen, hides the cursor, and initializes the current position to 0.

        If the player is running, updates the track, sets the title bar, and refreshes the screen and scroll pad.
        Otherwise, displays a message indicating that the player is not running.

        Parameters:
            None

        Returns:
            None
        """
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
            self.stdscr.addstr(
                0, 1, f'{self.player.player_name} is not running!')
            self.stdscr.refresh()

    def set_titlebar(self):
        """
        Set the title bar of the application window.
        Displays the track title, artist, and album.

        Parameters:
            self (object): The instance of the class.

        Return:
            None.
        """
        track_info = self.player.track.track_info(self.width - 1)
        # track_info -> ['title', 'artist', 'album'] - all algined
        self.stdscr.addstr(0, 1, track_info[0], curses.A_REVERSE)
        self.stdscr.addstr(1, 1, track_info[1],
                           curses.A_REVERSE | curses.A_BOLD | curses.A_DIM)
        self.stdscr.addstr(2, 1, track_info[2], curses.A_REVERSE)

    def set_offset(self):
        """
        Set the offset for the player track based on the alignment.

        0: center align
        1: left align
        2: right align

        Parameters:
        - None

        Return:
        - None
        """
        if self.player.track.alignment == 0:
            # center align
            self.pad_offset = (self.width - self.player.track.width) // 2
        elif self.player.track.alignment == 1:
            self.pad_offset = 2
        else:
            self.pad_offset = (self.width - self.player.track.width)

    def scroll_down(self, step=1):
        """
        Scroll down the screen by a specified number of steps.

        Args:
            step (int): The number of steps to scroll down. Defaults to 1.

        Returns:
            None
        """
        if self.current_pos < self.player.track.length - (self.height * 0.5):
            self.current_pos += step
        else:
            self.stdscr.addstr(self.height - 1, 1, 'END', curses.A_REVERSE)

    def scroll_up(self, step=1):
        """
        Scrolls the display up by a specified number of steps.

        Parameters:
            step (int): The number of steps to scroll up. Defaults to 1.

        Returns:
            None
        """
        if self.current_pos > 0:
            if self.current_pos >= self.player.track.length - \
                    (self.height * 0.5):
                self.stdscr.move(self.height - 1, 0)
                self.stdscr.clrtoeol()
            self.current_pos -= step

    def update_track(self):
        """
        Updates the track display by clearing the screen and the scroll pad.
        Wraps the track text if necessary. The offset of the scroll pad is set.

        Parameters:
            None

        Returns:
            None
        """
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
        """
        Main function that runs the display loop, listening for key inputs.

        Parameters:
            None

        Returns:
            None
        """
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
                self.stdscr.addstr(
                    0, 1, f'{self.player.player_name} player is not running.')
                self.stdscr.refresh()
