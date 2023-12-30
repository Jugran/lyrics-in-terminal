from gi.repository import GLib

import dbus
import traceback
import sys


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
