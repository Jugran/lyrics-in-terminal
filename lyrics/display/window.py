import curses
import asyncio

import _curses

from lyrics.display.input import InputManager
from lyrics.config import Config
from lyrics.track import Track
from lyrics import Logger

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lyrics.lyrics_in_terminal import LyricsInTerminal


class Window:
    def __init__(self, controller: "LyricsInTerminal", track: Track):
        self.options = Config('OPTIONS')
        self.controller = controller
        self.track = track
        self.height, self.width = controller.stdscr.getmaxyx()
        self.scroll_pad = curses.newpad(self.track.length + 2,
                                        self.track.width + 2)
        self.current_pos = 0
        self.pad_offset = 1
        self.text_padding = 5
        self.keys = controller.input_manager
        self.find_position = 0
        self.timeout = -1

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
        Logger.info('Setting up window...')
        curses.curs_set(0)
        self.current_pos = 0

        if self.controller.player.running:
            self.refresh(refresh_titlebar=True, clear=True)
        else:
            self.show_not_running()

    def set_titlebar(self):
        """
        Set the title bar of the application window.
        Displays the track title, artist, and album.

        Parameters:
            self (object): The instance of the class.

        Return:
            None.
        """
        track_info = self.track.track_info(self.width - 1)
        # track_info -> ['title', 'artist', 'album'] - all algined
        self.controller.stdscr.addstr(0, 1, track_info[0], curses.A_REVERSE)
        self.controller.stdscr.addstr(1, 1, track_info[1],
                           curses.A_REVERSE | curses.A_BOLD | curses.A_DIM)
        self.controller.stdscr.addstr(2, 1, track_info[2], curses.A_REVERSE)

    def set_statusbar(self):
        if self.options['statusbar'] != 'on':
            return

        lines = self.track.length if self.track.length > 0 else 1
        if self.current_pos < 0:
            self.current_pos = 0
        pct_progress = f' {
            round(self.current_pos * 100 / lines) + 1}% '
        self.controller.stdscr.insstr(self.height - 1, self.width -
                           len(pct_progress), pct_progress, curses.A_DIM)

    def add_notif(self, text: str):
        text = f" {text} "
        self.controller.stdscr.addstr(self.height - 1, 1, text, curses.A_REVERSE)
        self.controller.stdscr.refresh()

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
        if self.track.alignment == 0:
            # center align
            self.pad_offset = (self.width - self.track.width) // 2
        elif self.track.alignment == 1:
            self.pad_offset = 2
        else:
            self.pad_offset = (self.width - self.track.width)

    def scroll_down(self, step=1):
        """
        Scroll down the screen by a specified number of steps.

        Args:
            step (int): The number of steps to scroll down. Defaults to 1.

        Returns:
            None
        """
        if self.current_pos < self.track.length - step:
            self.current_pos += step
        else:
            self.current_pos = self.track.length - 1
            self.controller.stdscr.move(self.height - 1, 0)
            self.controller.stdscr.clrtoeol()
            self.controller.stdscr.addstr(self.height - 1, 1, 'END', curses.A_REVERSE)

    def scroll_up(self, step=1):
        """
        Scrolls the display up by a specified number of steps.

        Parameters:
            step (int): The number of steps to scroll up. Defaults to 1.

        Returns:
            None
        """
        if self.current_pos > 0:
            if self.current_pos >= self.track.length - \
                    (self.height * 0.5):
                self.controller.stdscr.move(self.height - 1, 0)
                self.controller.stdscr.clrtoeol()
            self.current_pos -= step

    def find_check_keys(self, key=None, lines_map=[]):
        if key == self.keys.binds['find-next']:
            self.controller.stdscr.addstr(self.height - 1, self.width - 3, 'n ')
            self.controller.stdscr.clrtoeol()
            # reached end of matches, loop back to start
            if self.find_position + 1 >= len(lines_map):
                self.find_position = 0
            else:
                self.find_position += 1
            return True
        elif key == self.keys.binds['find-prev']:
            self.controller.stdscr.addstr(self.height - 1, self.width - 3, 'p ')
            self.controller.stdscr.clrtoeol()
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
        self.controller.stdscr.timeout(-1)
        prompt = ':'
        self.controller.stdscr.move(self.height - 1, 0)
        self.controller.stdscr.clrtoeol()
        self.controller.stdscr.addstr(self.height - 1, self.pad_offset, prompt)
        self.set_statusbar()
        # show cursor and key presses during find
        curses.echo()
        curses.curs_set(1)

        # (y, x, input max length), case-insensitive
        find_string = self.controller.stdscr.getstr(
            self.height - 1, len(prompt) + self.pad_offset, 100)
        find_string = find_string.decode(encoding="utf-8").strip()

        # hide cursor and key presses
        curses.curs_set(0)
        curses.noecho()

        if find_string:
            # use word wrap which covers both wrap/nowrap and ensures line count is accurate
            text = self.track.get_text(
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
                    self.controller.stdscr.clear()
                    self.set_titlebar()
                    self.controller.stdscr.refresh()
                    self.scroll_pad.refresh(
                        self.current_pos, 0, 4, self.pad_offset, self.height - 2, self.width - 1)

                    # find & status bar output
                    find_string_output = f' {find_string} '
                    find_count_output = f" {
                        self.find_position + 1}/{len(lines_map)} "
                    self.controller.stdscr.addstr(
                        self.height - 1, self.pad_offset, find_string_output, curses.A_REVERSE)
                    self.controller.stdscr.insstr(
                        self.height - 1, self.pad_offset + len(find_string_output) + 1, find_count_output)
                    # multiple matches, show next/prev
                    if len(lines_map) > 1:
                        help_output = f"[{chr(
                            self.keys.binds['find-next'])}]=next, [{chr(self.keys.binds['find-prev'])}]=prev"
                        self.controller.stdscr.addstr(self.height - 1, self.pad_offset + len(
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
                        self.controller.stdscr.addch(
                            4, self.pad_offset + cpos, char, attr)

                    # after finding a match in a line, stop, wait for input
                    self.controller.stdscr.timeout(10000)
                    key = self.controller.stdscr.getch()
                    result = self.find_check_keys(key, lines_map)
                    if not result:
                        break

            else:
                output = ' not found '
                self.controller.stdscr.insstr(self.height - 1, self.pad_offset +
                                   len(prompt) + len(find_string) + 2, output, curses.A_REVERSE)
                self.set_statusbar()
                # timeout or key press
                self.controller.stdscr.timeout(5000)
                key = self.controller.stdscr.getch()
                self.find_check_keys(key, lines_map)

        # clear search line
        self.controller.stdscr.clear()
        self.controller.stdscr.timeout(self.timeout)

    def update_track(self):
        """
        Updates the track display by clearing the screen and the scroll pad.
        Wraps the track text if necessary. The offset of the scroll pad is set.

        Parameters:
            None

        Returns:
            None
        """
        Logger.info("Updating track display...")
        self.height, self.width = self.controller.stdscr.getmaxyx()
        self.scroll_pad.clear()
        self.current_pos = 0

        if self.track.width > self.width - self.text_padding:
            text = self.track.get_text(wrap=True,
                                       width=self.width - self.text_padding)
        else:
            text = self.track.get_text()

        pad_height = max(self.height, self.track.length) + 2
        pad_width = max(self.width, self.track.width) + 2

        self.scroll_pad.resize(pad_height, pad_width)
        self.scroll_pad.addstr(text)
        self.set_offset()

        self.refresh(refresh_titlebar=True, clear=True)

    def refresh_titlebar(self):
        # TODO: make titlebar separate widget
        self.set_titlebar()
        self.controller.stdscr.refresh()
        return

    def refresh(self, refresh_titlebar=True ,clear=False):
        self.height, self.width = self.controller.stdscr.getmaxyx()

        if clear:
            self.controller.stdscr.clear()
        
        if refresh_titlebar:
            self.set_titlebar()

        self.set_statusbar()
        self.controller.stdscr.refresh()
        self.scroll_pad.refresh(self.current_pos, 0, 4,
                                self.pad_offset, self.height - 2, self.width - 1)

    def show_not_running(self):
        self.controller.stdscr.clear()
        self.controller.stdscr.addstr(
            0, 1, f'{self.controller.player.player_name} player is not running.')
        self.controller.stdscr.refresh()

    # TODO: create logger annotation to log entry exit and errors
    def main(self):
        """
        Main function of window, initializes the window.

        Parameters:
            None

        Returns:
            None
        """
        curses.use_default_colors()
        self.set_up()
        Logger.info('Window Initialized')