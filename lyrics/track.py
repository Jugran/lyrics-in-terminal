#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import util


class Track:
    def __init__(self,
                 artist=None,
                 title=None,
                 align=1,
                 width=0,
                 height=0):

        self.title = title
        self.artist = artist
        self.alignment = align
        self.width = width
        self.height = height
        self.length = 0
        self.lyrics = None
        self.album = None
        self.trackid = None
        self.art_url = None

    def __str__(self):
        return self.artist + ' - ' + self.title

    @property
    def track_name(self):
        return self.artist + ' - ' + self.title

    def track_info(self, width):
        trackinfo = util.align([self.title, self.artist, self.album], width, self.alignment)
        
        offset = self.alignment%2
        padding = ' ' * offset
        trackinfo = [padding + t + ' ' * (width - len(t) - offset) for t in trackinfo]

        return trackinfo

    def update(self, artist, title, album, trackid, art_url):
        self.artist = artist
        self.title = title
        self.album = album
        self.trackid = trackid
        self.art_url = art_url
        self.get_lyrics()

    def get_lyrics(self, cache=True, source='google'):
        self.lyrics = util.get_lyrics(self.track_name, cache=cache, source=source)
        self.width = len(max(self.lyrics, key=len))
        self.length = len(self.lyrics)

    def get_text(self, wrap=False, width=0):
        if wrap:
            lyrics=util.wrap_text(self.lyrics, width)
        else:
            lyrics=self.lyrics

        self.width = len(max(lyrics, key=len))
        self.length = len(lyrics)

        lyrics = util.align(lyrics, self.width, self.alignment)

        return '\n'.join(line for line in lyrics)

    def delete_lyrics(self):
        return util.delete_lyrics(self.track_name)
