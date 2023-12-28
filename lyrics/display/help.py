
from lyrics.config import Config
from lyrics import __version__
import curses


class HelpPage:
    def __init__(self, keybinds):
        self.keybinds = keybinds
        self.options = Config('OPTIONS')

        self.win = curses.initscr()
        self.win.box()
        self.add_text()
        self.main()

    def add_config(self, i, j, config, _keys):
        # invert keys
        for k, v in config.items():
            # set representable strings to ascii values
            if v in _keys.keys():
                v = _keys[v]
            elif k not in ['step-size', 'interval', 'mpd_port']:
                if isinstance(v, int):
                    v = chr(v)  # character values
            self.win.addstr(i, j, f'{k:18} {v}')
            # self.win.addstr(i, j, f'{k} \t {v}')
            i += 1
        return i

    def add_text(self):
        self.win.refresh()

        h, w = self.win.getmaxyx()
        self.win.addstr(2, 3, f"{'v' + __version__:>{w-5}}")
        self.win.addstr(3, 3, 'Help Page', curses.A_BOLD | curses.A_UNDERLINE)
        self.win.addstr(h - 2, 3, f"{'Press any key to exit...':>{w-5}}")

        keys = {curses.KEY_UP: '↑',
                curses.KEY_DOWN: '↓',
                curses.KEY_LEFT: '←',
                curses.KEY_RIGHT: '→',
                }
        # keybinds
        i, j = 6, 3
        self.win.addstr(i, j, 'Keybindings', curses.A_UNDERLINE)
        i += 2
        i = self.add_config(i, j, self.keybinds, keys)
        # options
        if w // 2 >= 30:
            i, j = 6, w // 2
        else:
            i += 2

        self.win.addstr(i, j, 'Default Options', curses.A_UNDERLINE)
        i += 2
        self.add_config(i, j, self.options, keys)

    def main(self):
        # wait for key input to exit
        self.win.timeout(-1)
        self.win.getch()

        self.win.timeout(self.options['interval'])
        self.win.erase()
