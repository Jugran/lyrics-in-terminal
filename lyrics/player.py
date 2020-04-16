#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .track import Track

import dbus


class Player:
    def __init__(self, name, source, **kwargs):
        self.player_name = name
        self.default_source = source

        self.running = False
        self.metadata = None
        self.track = Track(**kwargs)

        self.session_bus = None
        self.player_bus = None
        self.player_interface = None

        self.update()

    def get_bus(self):
        try:
            self.session_bus = dbus.SessionBus()
            self.player_bus = self.session_bus.get_object(f'org.mpris.MediaPlayer2.{self.player_name}', '/org/mpris/MediaPlayer2')
            self.player_interface = dbus.Interface(self.player_bus, 'org.freedesktop.DBus.Properties')
            self.running = True
        except dbus.exceptions.DBusException:
            self.running = False

    def update(self):
        try:
            if not self.running:
                self.get_bus()

            self.metadata = self.player_interface.Get("org.mpris.MediaPlayer2.Player", "Metadata")
            self.running = True
        except Exception as e:
            self.running = False

        if self.running:
            try:
                title = self.metadata['xesam:title']
                artist = self.metadata['xesam:artist'][0]
                album = self.metadata['xesam:album']
                # arturl = self.metadata['mpris:artUrl']
                trackid = self.metadata['mpris:trackid']
            except (IndexError, KeyError) as e:
                self.running = False
                return False

            if trackid.find('spotify:ad') != -1:
                self.running = False
            elif self.track.trackid != trackid or self.track.title != title:
                #update
                self.track.update(artist, title, album, trackid)
                self.refresh(self.default_source)
                return True

        return False

    def refresh(self, source, cache=True):
        self.track.get_lyrics(source, cache=cache)

    def next(self):
        pass

    def prev(self):
        pass

    def play_toggle(self):
        pass