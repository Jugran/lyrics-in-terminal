#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lyrics.track import Track

import dbus
import re


class Player:
    def __init__(self, name, source, autoswitch, **kwargs):
        self.player_name = name
        self.default_source = source

        self.autoswitch = autoswitch

        self.running = False
        self.track = Track(**kwargs)

        self.player_interface = None

        self.update()

    def check_playing(self):
        if self.player_interface:
            status = self.player_interface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
            self.running = (status == 'Playing')

    # def get_players(self):
    #     players = []
    #     for service in dbus.SessionBus().list_names():
    #         if re.findall(r'org.mpris.MediaPlayer2|plasma-browser-integration', service, re.IGNORECASE):
    #         obj = bus.get_object(service, '/org/mpris/MediaPlayer2')
    #         interface = dbus.Interface(obj, 'org.freedesktop.DBus.Properties')
    #         status = str(interface.Get(
    #             'org.mpris.MediaPlayer2.Player', 'PlaybackStatus'))
    #         players.append((str(service), status))
    #     return players

    def get_active_player(self):
        session_bus = dbus.SessionBus()
        for service in session_bus.list_names():
            if re.findall(r'org.mpris.MediaPlayer2|plasma-browser-integration', service, re.IGNORECASE):
                obj = session_bus.get_object(service, '/org/mpris/MediaPlayer2')
                interface = dbus.Interface(obj, 'org.freedesktop.DBus.Properties')
                status = interface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
                if status == 'Playing':
                    self.player_name = service.split('MediaPlayer2.')[-1]
                    self.player_interface = interface
                    self.running = True
                    return


    def get_bus(self):
        try:
            # session_bus = dbus.SessionBus()
            # dirname = Path(__file__).parent
            # self.player_name = subprocess.check_output(dirname.joinpath('detect-media.sh')).decode('utf-8')
            # player_bus = session_bus.get_object(self.player_name, '/org/mpris/MediaPlayer2')
            # self.player_interface = dbus.Interface(player_bus, 'org.freedesktop.DBus.Properties')
            if self.autoswitch:
                self.get_active_player()
            else:
                session_bus = dbus.SessionBus()
                player_bus = session_bus.get_object(f'org.mpris.MediaPlayer2.{self.player_name}', '/org/mpris/MediaPlayer2')
                self.player_interface = dbus.Interface(player_bus, 'org.freedesktop.DBus.Properties')
                self.running = True

        except dbus.exceptions.DBusException:
            self.running = False
            self.player_interface = None

    def update(self):
        try:
            if self.autoswitch:
                self.check_playing()
                
            if not self.running:
                self.get_bus()
            # check if current player that was being tracking is playing or not
            # if not the get playing media player
            # if not found fallback to default media player

            metadata = self.player_interface.Get("org.mpris.MediaPlayer2.Player", "Metadata")
            self.running = True
        except Exception as e:
            self.running = False
            self.player_interface = None

        if self.running:
            try:
                title = metadata['xesam:title']
                # title = re.sub(r'(\[.*\])', '', title).strip()

                artist = metadata['xesam:artist']
                artist = artist[0] if isinstance(artist, list) else artist
                
                album = metadata.get('xesam:album')
                album = '' if album is None else album
                # arturl = metadata['mpris:artUrl']
                trackid = metadata.get('mpris:trackid')
                trackid = title if trackid is None else trackid
            except (IndexError, KeyError) as e:
                self.running = False
                return False

            if trackid.find('spotify:ad') != -1:
                self.running = False
            elif self.track.trackid != trackid or self.track.title != title:
                #update
                self.track.update(artist, title, album, trackid)
                self.refresh()
                return True

        return False

    def refresh(self, source=None, cache=True):
        if source is None:
            source = self.default_source
        self.track.get_lyrics(source, cache=cache)
