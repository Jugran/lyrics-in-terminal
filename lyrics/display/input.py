import asyncio
import curses


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

    @property
    def stdscr(self):
        return self.controller.stdscr

    @property
    def window(self):
        return self.controller.window

    @property
    def player(self):
        return self.controller.player

    @property
    def track(self):
        return self.controller.track

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
            self.window.update_track()
        elif key == self.binds['down']:
            self.window.scroll_down()
            self.window.refresh()
        elif key == self.binds['step-down']:
            self.window.scroll_down(self.binds['step-size'])
            self.stdscr.erase()
            self.window.refresh()
        elif key == self.binds['up']:
            self.window.scroll_up()
            self.window.refresh()
        elif key == self.binds['step-up']:
            self.window.scroll_up(self.binds['step-size'])
            self.stdscr.erase()
            self.window.refresh()

        elif key == self.binds['cycle-source']:
            self.window.add_notif('Switching source...')
            await self.track.update_lyrics(cycle_source=True, cache=False)
            if self.track.timestamps and self.player.sync_available:
                Logger.info("Synced Lyrics available")
                # start sync mode
            else:
                pass
                # reset sync mode
                # self.window.last_highlight = -1
                # self.stdscr.timeout(self.window.timeout)

        # keys to change alignment
        elif key == self.binds['left']:
            self.controller.track.alignment = 1
            self.controller.track.reset_width()
            self.window.update_track()
        elif key == self.binds['center']:
            self.controller.track.alignment = 0
            self.controller.track.reset_width()
            self.window.update_track()
        elif key == self.binds['right']:
            self.window.track.alignment = 2
            self.controller.track.reset_width()
            self.window.update_track()

        elif key == self.binds['delete']:
            if self.controller.track.delete_lyrics():
                self.window.add_notif('Deleted')
        elif key == self.binds['help']:
            self.stdscr.erase()
            HelpPage(self.binds)
            self.controller.reinitialize_screen()
        elif key == self.binds['edit']:
            curses.endwin()
            self.controller.track.edit_lyrics()
            self.controller.reinitialize_screen()
            await self.controller.track.update_lyrics(cache=True)
            self.window.update_track()

        elif key == self.binds['find']:
            self.window.find()

        # autoswitch toggle
        elif key == self.binds['autoswitchtoggle']:
            self.player.autoswitch = not self.player.autoswitch
            self.stdscr.addstr(self.window.height - 1, 1,
                               f" Autoswitch: {'on' if self.player.autoswitch else 'off'} ", curses.A_REVERSE)

    async def main(self):
        if self.player.running:
            self.stdscr.timeout(-1)
        else:
            self.stdscr.timeout(200)

        await self.loop()

    async def loop(self):
        Logger.info('Start Input loop...')
        key = ''
        self.stdscr.timeout(-1)

        while key != self.binds['quit']:
            key = await asyncio.to_thread(self.stdscr.getch)
            if key != curses.ERR:
                Logger.debug(f'Key pressed: {key}')
                await self.input(key)

        Logger.info('End Input loop...')
        self.controller.quit()
