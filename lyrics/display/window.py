#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lyrics.display.key import Key
from lyrics.config import Config

import curses


class Window:
    def __init__(self, stdscr, player, timeout):
        self.options = Config('OPTIONS')
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.player = player
        self.scroll_pad = curses.newpad(self.player.track.length + 2,
                                        self.player.track.width + 2)
        self.current_pos = 0
        self.pad_offset = 1
        self.text_padding = 5
        self.keys = Key()
        self.find_position = 0
        self.timeout = timeout

        curses.use_default_colors()
        self.stdscr.timeout(self.timeout)
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

    def set_statusbar(self):
        if self.options['statusbar'] != 'on':
            return

        lines = self.player.track.length
        if self.current_pos < 0:
            self.current_pos = 0
        pct_progress = f' {
            round(self.current_pos * 100 / lines) + 1}% '
        self.stdscr.insstr(self.height - 1, self.width -
                           len(pct_progress), pct_progress, curses.A_DIM)

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
        if self.current_pos < self.player.track.length - step:
            self.current_pos += step
        else:
            self.current_pos = self.player.track.length - 1
            self.stdscr.move(self.height - 1, 0)
            self.stdscr.clrtoeol()
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

    def find_check_keys(self, key=None, lines_map=[]):
        if key == self.keys.binds['find-next']:
            self.stdscr.addstr(self.height - 1, self.width - 3, 'n ')
            self.stdscr.clrtoeol()
            # reached end of matches, loop back to start
            if self.find_position + 1 >= len(lines_map):
                self.find_position = 0
            else:
                self.find_position += 1
            return True
        elif key == self.keys.binds['find-prev']:
            self.stdscr.addstr(self.height - 1, self.width - 3, 'p ')
            self.stdscr.clrtoeol()
            if self.find_position - 1 < 0:
                self.find_position = len(lines_map) - 1
            else:
                self.find_position -= 1
            return True
        # other keys for more accessibility
        elif key == self.keys.binds['down']:
            self.scroll_down()
        elif key == self.keys.binds['up']:
            self.scroll_up()
        elif key == self.keys.binds['step-down']:
            self.scroll_down(self.keys.binds['step-size'])
        elif key == self.keys.binds['step-up']:
            self.scroll_up(self.keys.binds['step-size'])
        elif key == self.keys.binds['find']:
            self.find()
        return False

    def find(self):
        # wait for input
        self.stdscr.timeout(-1)
        prompt = ':'
        self.stdscr.move(self.height - 1, 0)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(self.height - 1, self.pad_offset, prompt)
        self.set_statusbar()
        # show cursor and key presses during find
        curses.echo()
        curses.curs_set(1)

        # (y, x, input max length), case-insensitive
        find_string = self.stdscr.getstr(
            self.height - 1, len(prompt) + self.pad_offset, 100)
        find_string = find_string.decode(encoding="utf-8").strip()

        # hide cursor and key presses
        curses.curs_set(0)
        curses.noecho()

        if find_string:
            # use word wrap which covers both wrap/nowrap and ensures line count is accurate
            text = self.player.track.get_text(
                wrap=True, width=self.width - self.text_padding)
            lines = text.split('\n')

            # [0,9,10,14] list of lines that contain a match
            lines_map = []
            for line_num, line in enumerate(lines):
                # case-insensitive match
                if find_string.lower() in line.lower():
                    lines_map.append(line_num)

            if len(lines_map) > 0:

                # continue search from current position
                for line in lines_map:
                    # >= causes us to stay on the current line for a new search
                    if line >= self.current_pos:
                        self.find_position = lines_map.index(line)
                        break
                # otherwise loop back to the start
                else:
                    self.find_position = 0

                while True:
                    # update current position based on where we are at in the find
                    self.current_pos = lines_map[self.find_position]

                    # duplicated from main() to manually refresh on find
                    self.stdscr.clear()
                    self.set_titlebar()
                    self.stdscr.refresh()
                    self.scroll_pad.refresh(
                        self.current_pos, 0, 4, self.pad_offset, self.height - 2, self.width - 1)

                    # find & status bar output
                    find_string_output = f' {find_string} '
                    find_count_output = f" {
                        self.find_position + 1}/{len(lines_map)} "
                    self.stdscr.addstr(
                        self.height - 1, self.pad_offset, find_string_output, curses.A_REVERSE)
                    self.stdscr.insstr(
                        self.height - 1, self.pad_offset + len(find_string_output) + 1, find_count_output)
                    # multiple matches, show next/prev
                    if len(lines_map) > 1:
                        help_output = f"[{chr(
                            self.keys.binds['find-next'])}]=next, [{chr(self.keys.binds['find-prev'])}]=prev"
                        self.stdscr.addstr(self.height - 1, self.pad_offset + len(
                            find_string_output) + len(find_count_output) + 2, help_output)
                    self.set_statusbar()

                    # highlight found text
                    line_text = lines[self.current_pos]
                    # case-insensitive, [4, 5, 21]
                    found_index_list = [i for i in range(
                        len(line_text)) if line_text.lower().startswith(find_string.lower(), i)]
                    # loop over each character in the line, highlight found strings
                    highlight_end = -1
                    for cpos, char in enumerate(line_text):
                        attr = curses.A_NORMAL
                        # start of found string
                        if cpos in found_index_list:
                            highlight_end = cpos + len(find_string)
                            attr = curses.A_REVERSE
                        # inside string
                        elif highlight_end > cpos:
                            attr = curses.A_REVERSE
                        self.stdscr.addch(
                            4, self.pad_offset + cpos, char, attr)

                    # after finding a match in a line, stop, wait for input
                    self.stdscr.timeout(10000)
                    key = self.stdscr.getch()
                    result = self.find_check_keys(key, lines_map)
                    if not result:
                        break

            else:
                output = ' not found '
                self.stdscr.insstr(self.height - 1, self.pad_offset +
                                   len(prompt) + len(find_string) + 2, output, curses.A_REVERSE)
                self.set_statusbar()
                # timeout or key press
                self.stdscr.timeout(5000)
                key = self.stdscr.getch()
                self.find_check_keys(key, lines_map)

        # clear search line
        self.stdscr.clear()
        self.stdscr.timeout(self.timeout)

    def update_track(self, show_source=False):
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

        if show_source:
            self.stdscr.addstr(self.height - 1, 1,
                    f" Source: {self.player.track.source}", curses.A_REVERSE)

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
                self.set_statusbar()
                self.stdscr.refresh()
                self.scroll_pad.refresh(self.current_pos, 0, 4,
                                        self.pad_offset, self.height - 2, self.width - 1)
            else:
                self.stdscr.clear()
                self.stdscr.addstr(
                    0, 1, f'{self.player.player_name} player is not running.')
                self.stdscr.refresh()
