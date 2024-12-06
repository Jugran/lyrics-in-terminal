import asyncio
import curses
import _curses

from lyrics.config import Config
from lyrics.display.help import HelpPage
from lyrics import Logger

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lyrics.lyrics_in_terminal import LyricsInTerminal


class InputManager:
    def __init__(self,  controller: "LyricsInTerminal" = None):
        self.binds = Config('BINDINGS')
        self.controller = controller

    async def input(self, key):
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
            self.controller.window.update_track()
        elif key == self.binds['down']:
            self.controller.window.scroll_down()
            self.controller.window.refresh()
        elif key == self.binds['step-down']:
            self.controller.window.scroll_down(self.binds['step-size'])
            self.controller.stdscr.erase()
            self.controller.window.refresh()
        elif key == self.binds['up']:
            self.controller.window.scroll_up()
            self.controller.window.refresh()
        elif key == self.binds['step-up']:
            self.controller.window.scroll_up(self.binds['step-size'])
            self.controller.stdscr.erase()
            self.controller.window.refresh()


        elif key == self.binds['cycle-source']:
            self.controller.window.add_notif('Switching source...')
            await self.controller.track.update_lyrics(cycle_source=True, cache=False)

        # keys to change alignment
        elif key == self.binds['left']:
            self.controller.track.alignment = 1
            self.controller.track.reset_width()
            self.controller.window.update_track()
        elif key == self.binds['center']:
            self.controller.track.alignment = 0
            self.controller.track.reset_width()
            self.controller.window.update_track()
        elif key == self.binds['right']:
            self.controller.window.track.alignment = 2
            self.controller.track.reset_width()
            self.controller.window.update_track()

        elif key == self.binds['delete']:
            if self.controller.track.delete_lyrics():
                self.controller.window.add_notif('Deleted')
        elif key == self.binds['help']:
            self.controller.stdscr.erase()
            HelpPage(self.binds)
            self.controller.reinitialize_screen()
        elif key == self.binds['edit']:
            curses.endwin()
            self.controller.track.edit_lyrics()
            self.controller.reinitialize_screen()
            await self.controller.track.update_lyrics(cache=True)
            self.controller.window.update_track()

        elif key == self.binds['find']:
            self.controller.window.find()

        # autoswitch toggle
        elif key == self.binds['autoswitchtoggle']:
            self.controller.player.autoswitch = not self.controller.player.autoswitch
            self.controller.stdscr.addstr(self.controller.window.height - 1, 1,
                                          f" Autoswitch: {'on' if self.controller.player.autoswitch else 'off'} ", curses.A_REVERSE)

    async def main(self):
        if self.controller.player.running:
            self.controller.stdscr.timeout(-1)
        else:
            self.controller.stdscr.timeout(200)

        await self.loop()

    async def loop(self):
        Logger.info('Start Input loop...')
        key = ''
        self.controller.stdscr.timeout(-1)

        while key != self.binds['quit']:
            key = await asyncio.to_thread(self.controller.stdscr.getch)
            if key != curses.ERR:
                Logger.debug(f'Key pressed: {key}')
                await self.input(key)


        Logger.info('End Input loop...')
        self.controller.quit()

