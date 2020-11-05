#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lyrics import util


class Track:
    def __init__(self,
                 artist=None,
                 title=None,
                 align=1,
                 width=0):
        """
        Initialize the artist object.

        Args:
            self: (todo): write your description
            artist: (todo): write your description
            title: (str): write your description
            align: (bool): write your description
            width: (int): write your description
        """

        self.title = title
        self.artist = artist
        self.alignment = align
        self.width = width
        self.length = 0
        self.lyrics = None
        self.album = None
        self.trackid = None

    def __str__(self):
        """
        The string representation of artist

        Args:
            self: (todo): write your description
        """
        return self.artist + ' - ' + self.title

    @property
    def track_name(self):
        """
        The artist name

        Args:
            self: (todo): write your description
        """
        return self.artist + ' - ' + self.title

    def reset_width(self):
        """
        Reset the width.

        Args:
            self: (todo): write your description
        """
        self.width = len(max(self.lyrics, key=len))

    def track_info(self, width):
        """
        Return information about the trackinfo.

        Args:
            self: (todo): write your description
            width: (int): write your description
        """
        trackinfo = util.align([self.title, self.artist, self.album], width, self.alignment)
        
        offset = self.alignment%2
        padding = ' ' * offset
        trackinfo = [padding + t + ' ' * (width - len(t) - offset) for t in trackinfo]

        return trackinfo

    def update(self, artist, title, album, trackid):
        """
        Updates a song

        Args:
            self: (todo): write your description
            artist: (todo): write your description
            title: (str): write your description
            album: (array): write your description
            trackid: (str): write your description
        """
        self.artist = artist
        self.title = title
        self.album = album
        self.trackid = trackid
        # self.art_url = art_url
        # self.get_lyrics()

    def get_lyrics(self, source, cache=True):
        """
        Returns the number of the number of tracks for the same length.

        Args:
            self: (todo): write your description
            source: (str): write your description
            cache: (todo): write your description
        """
        self.lyrics = util.get_lyrics(self.track_name, source, cache=cache)
        self.width = len(max(self.lyrics, key=len))
        self.length = len(self.lyrics)

    def get_text(self, wrap=False, width=0):
        """
        Return a string representation of the table.

        Args:
            self: (todo): write your description
            wrap: (todo): write your description
            width: (int): write your description
        """
        if wrap:
            lyrics=util.wrap_text(self.lyrics, width)
        else:
            lyrics=self.lyrics

        self.width = len(max(lyrics, key=len))
        self.length = len(lyrics)

        lyrics = util.align(lyrics, self.width, self.alignment)

        return '\n'.join(line for line in lyrics)
    
    def edit_lyrics(self):
        """
        Edit track_name

        Args:
            self: (todo): write your description
        """
        util.edit_lyrics(self.track_name)


    def delete_lyrics(self):
        """
        Deletes the track_name.

        Args:
            self: (todo): write your description
        """
        return util.delete_lyrics(self.track_name)
