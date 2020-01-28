#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import util

JUSTIFICATION = 0


def justify(text, width, justification=1):
    if justification == 1:
        return text
    elif justification == 0:
        return [line.center(width) for line in text]
    else:
        return [line.rjust(width) for line in text]


class Track:
    def __init__(self,
                 artist=None,
                 title=None,
                 justify=1,
                 width=0,
                 height=0,
                 hard_format=False):

        self.title = title
        self.artist = artist
        self.justification = justify
        self.hard_format = hard_format
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

    def update(self, artist, title, album, trackid, art_url):
        self.artist = artist
        self.title = title
        self.album = album
        self.trackid = trackid
        self.art_url = art_url
        self.get_lyrics()

    def get_lyrics(self):
        lyrics = util.get_lyrics(self.track_name)

        if not self.hard_format:
            self.width = len(max(lyrics, key=len))

        self.length = len(lyrics)
        self.lyrics = self.format_lyrics(lyrics)

    def format_lyrics(self, lyrics):
        # center lyrics vertically
        if self.length < self.height and self.hard_format:
            space = (self.height - self.length) // 2
            padding = [''] * (space - 2)
            lyrics = padding + lyrics + padding

        return justify(lyrics, self.width, self.justification)

    def get_text(self):
        return '\n'.join(line for line in self.lyrics)


if __name__ == '__main__':

    if len(sys.argv) >= 5:
        artist = sys.argv[1].strip()
        title = sys.argv[2].strip()
        width = int(sys.argv[-2])
        height = int(sys.argv[-1])

        track = Track(artist, title, JUSTIFICATION, width, height, True)
        track.get_lyrics()

        topline = [track.track_name, round(width * 0.8) * '-']
        topline = '\n'.join(justify(topline, width, JUSTIFICATION))
        print(topline, '\n' + track.get_text())

    else:
        print('No Track info provided, Exiting...')
        exit
