#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lyrics.track import Track

import dbus
import re
from mpd import MPDClient as mpd

class Player:
    def __init__(self, name, source, autoswitch, mpd_connect, **kwargs):
        self.player_name = name
        self.default_source = source

        self.autoswitch = autoswitch

        self.running = False
        self.track = Track(**kwargs)

        self.player_interface = None
        self.mpd_host = mpd_connect[0] or '127.0.0.1'
        self.mpd_port = mpd_connect[1] or 6600
        self.mpd_pass = mpd_connect[2] or ''
        self.update()

    def check_playing(self):
        ''' checks playing status of current player
        '''

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
        ''' returns name of playing media source/player
        '''

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


    def mpd_active(self):
        """ Check if mpd is active and get metadata """
        client = mpd()
        try: client.connect(self.mpd_host,self.mpd_port)
        except Exception as e:
            print(e)
        if self.mpd_pass != '':
            client.password(self.mpd_pass)
        if client.status()['state'] == 'play':
            self.player_name = "mpd"
            self.running2 = True
            currentsong = client.currentsong()
            if 'album' in currentsong: album = currentsong['album']
            else: album = ''
            title = currentsong['title']
            title2 = currentsong['title']
            artist = currentsong['artist']
            album = album
            trackid = currentsong['id']
            if self.track.title != title:
                self.track.update(artist, title, album, trackid)
                self.refresh()
                return True
        else:
            self.running2 = False        
        return False
    
    def get_bus(self):
        ''' gets dbus session bus and player interface
        '''

        try:
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
        ''' checks if player or track have changed or not
        '''

        try:
            if self.autoswitch:
                self.check_playing()
                
            if not self.running:
                self.get_bus()

            metadata = self.player_interface.Get("org.mpris.MediaPlayer2.Player", "Metadata")
            self.running = True
        except Exception as e:
            self.running = False
            self.player_interface = None
                
        
        if self.running:
            try:
                title = metadata['xesam:title']
                if title.strip() == '':
                    # if Title is empty, don't update
                    return False
                
                artist=''
                if 'xesam:artist' in metadata:
                    artist = metadata['xesam:artist']
                artist = artist[0] if isinstance(artist, list) else artist

                if re.search('chromium|plasma', self.player_name) and '-' in title:
                    # in case of artist in the title
                    artist, title, *_ = title.split('-')

                title = title.strip()
                artist = artist.strip()
                
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
                # update track
                self.track.update(artist, title, album, trackid)
                self.refresh()
                return True
                
        if not self.running:
            if self.mpd_active():
                return True
                
        return False

    def refresh(self, source=None, cache=True):
        ''' Re-fetches lyrics from procided source
            source -> source name ('google' or 'azlyrics')
            cache -> bool | wether to store cache file
        '''
        
        if source is None:
            source = self.default_source
        self.track.get_lyrics(source, cache=cache)
