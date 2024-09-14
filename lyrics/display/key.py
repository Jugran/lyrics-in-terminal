from lyrics.config import Config
from lyrics.display.help import HelpPage
import curses


class Key:
    def __init__(self):
        self.binds = Config('BINDINGS')

    def input(self, window, key):
        """
        Process the input from the user interface and perform corresponding actions.

        Args:
            window (Window): The user interface window object.
            key (int): The key code representing the user's input.

        Returns:
            None

        Raises:
            None
        """
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
            window.player.refresh(source='azlyrics', cache=False)
            window.current_pos = 0
            window.update_track()
        elif key == self.binds['google']:
            window.player.refresh(source='google', cache=False)
            window.current_pos = 0
            window.update_track()

        elif key == self.binds['cycle-source']:
            window.player.refresh(cycle_source=True, cache=False)
            window.current_pos = 0
            window.update_track(True)

        # keys to change alignment
        elif key == self.binds['left']:
            window.player.track.alignment = 1
            window.player.track.reset_width()
            window.update_track()
        elif key == self.binds['center']:
            window.player.track.alignment = 0
            window.player.track.reset_width()
            window.update_track()
        elif key == self.binds['right']:
            window.player.track.alignment = 2
            window.player.track.reset_width()
            window.update_track()

        elif key == self.binds['delete']:
            if window.player.track.delete_lyrics():
                window.stdscr.addstr(window.height - 1, 1,
                                     ' Deleted ', curses.A_REVERSE)
        elif key == self.binds['help']:
            window.stdscr.erase()
            HelpPage(self.binds)
            window.height, window.width = window.stdscr.getmaxyx()
        elif key == self.binds['edit']:
            curses.endwin()
            window.player.track.edit_lyrics()
            window.stdscr = curses.initscr()
            window.current_pos = 0
            window.player.refresh(cache=True)
            window.update_track()

        elif key == self.binds['find']:
            window.find()

        # autoswitch toggle
        elif key == self.binds['autoswitchtoggle']:
            window.player.autoswitch = not window.player.autoswitch
            window.stdscr.addstr(window.height - 1, 1,
                                 f" Autoswitch: {'on' if window.player.autoswitch else 'off'} ", curses.A_REVERSE)
