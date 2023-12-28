import curses
import sys

from time import sleep
from threading import Thread
import dbus.mainloop.glib
import dbus
from gi.repository import GLib
import traceback
import sys

BUS_NAME = 'org.mpris.MediaPlayer2.spotify'
OBJECT_PATH = '/org/mpris/MediaPlayer2'
INTERFACE = 'org.freedesktop.DBus.Properties'
DISPLAY = None
PLAYER = None


class Track:
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist
        self.trackid = ''

    def update(self, title, artist):
        self.title = title
        self.artist = artist



class DbusListener:
    def __init__(self, bus_name, object_path, interface, display):
        self.bus_name = bus_name
        self.object_path = object_path
        self.interface = interface
        self.display = display

        self.bus = None
        self.player_object = None
        self.loop = None

    def properties_changed(self, interface, changed, invalidated):

        metadata = changed.get('Metadata')  # dict
        # -> string = Playing | Paused

        # PlaybackStatus and metadata can be absent from changed dict
        playback_status = changed.get('PlaybackStatus')

        # if self.update is not None:
        #     self.update(metadata, playback_status)

        if self.display is not None:
            self.display.update(playback_status, metadata)
    
    def quit_listener(self):
        if self.loop is not None:
            self.loop.quit()

    def start_listener(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        self.bus = dbus.SessionBus()
        try:
            self.player_object = self.bus.get_object(
                self.bus_name, self.object_path)

            self.player_object.connect_to_signal(
                "PropertiesChanged", self.properties_changed, dbus_interface=self.interface)

        except dbus.DBusException:
            traceback.print_exc()
            print("Error occured")
            sys.exit(1)

        self.loop = GLib.MainLoop()

        try:
            self.loop.run()
        except KeyboardInterrupt:
            print("Thread: KeyboardInterrupt")
            self.loop.quit()


class Player(DbusListener):
    def __init__(self, player_name, display):
        self.player_name = player_name
        super().__init__(BUS_NAME, OBJECT_PATH, INTERFACE, display)


class Display:
    def __init__(self, stdscr):
        self.stdscr = stdscr


        # TODO: add write lock for track
        self.track = Track('', '')
        self.status = '-'

        self.height, self.width = stdscr.getmaxyx()

        # curses.use_default_colors()
        self.stdscr.clear()
        curses.curs_set(0)
        self.refresh_screen()

    def update(self, status, metadata):
        refresh = False

        if status is not None and self.status != status:
            self.status = status
            refresh = True

        if metadata is None:
            if refresh:
                self.refresh_screen()
            return
        try:
            title = metadata['xesam:title']
            if title.strip() == '':
                # if Title is empty, don't update
                return

            artist = metadata['xesam:artist']
            artist = artist[0] if isinstance(artist, list) else artist

        except (IndexError, KeyError) as e:
            return

        if self.track.title != title:
            # update track
            self.track.update(title, artist)
            refresh = True

        if refresh:
            self.refresh_screen()

    def refresh_screen(self):
        self.stdscr.erase()

        title = self.track.title
        artist = self.track.artist
        status = self.status

        self.stdscr.addstr(0, 1, title, curses.A_REVERSE)
        self.stdscr.addstr(1, 1, artist, curses.A_REVERSE |
                           curses.A_BOLD | curses.A_DIM)
        self.stdscr.addstr(2, 1, status, curses.A_REVERSE)

        self.stdscr.refresh()

    def main(self):
        # wait for key input to exit
        self.stdscr.timeout(-1)

        while True:
            key = self.stdscr.getch()

            if key == ord('q') and PLAYER is not None:
                PLAYER.quit_listener()
                return

            self.stdscr.erase()



def ErrorHandler(func):
    def wrapper(*args, **kwargs):
        try:
            curses.wrapper(func)
        except KeyboardInterrupt:
            pass
        except curses.error as err:
            print('Please increase terminal window size!')
        except:
            print('Unexpected exception occurred.', sys.exc_info())

    return wrapper


@ErrorHandler
def start(stdscr):
    global DISPLAY

    DISPLAY = Display(stdscr)
    DISPLAY.main()


if __name__ == '__main__':

    try:
        display_thread = Thread(target=start)
        display_thread.start()

        sleep(2)
        PLAYER = Player('spotify', DISPLAY)
        main_thread = Thread(target=PLAYER.start_listener)

        main_thread.start()

        display_thread.join()
        main_thread.join()

    except KeyboardInterrupt:
        print("Host: KeyboardInterrupt")
        PLAYER.quit_listener()
