
import curses


class Widget:
    ''' Fixed Block of curses object
    '''

    def __init__(self, text, position, size):
        self.text = text
        self.position = position
        self.size = size

        self.pad = curses.newpad(size.y, size.x)

    def refresh(self):
        y = self.position.y
        x = self.position.x

        y1 = y + self.size.y
        x1 = x + self.size.x

        self.pad.refresh(y, x, y1, x1)

    def update(self, text, position):
        pass


class Bar:
    ''' Single line static bar
    '''

    def __init__(self, text, position):
        self.text = text
        self.position = position

    def refresh(self):
        pass

    def update(self, text, position):
        pass


class Menu:
    def __init__(self, options):
        self.options = options

        self.win = curses.initscr()
        self.win.box()
        self.add_text()
        self.main()

    
    def add_text(self):
        self.win.refresh()

        h, w = self.win.getmaxyx()
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
