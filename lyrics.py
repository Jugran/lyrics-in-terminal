#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import util


class Track:
    def __init__(self, artist, title, justify=1, width=0, height=0, hard_format=False):
        self.title = title
        self.artist = artist
        self.justification = justify
        self.lyrics = None 
        self.hard_format = hard_format
        self.width = width
        self.height = height
        self.length = 0

    def __str__(self):
        return self.artist + ' - ' + self.title

    @property
    def track_name(self):
        return self.artist + ' - ' + self.title

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
            #  lyrics = [''] * (padding - 3) + lyrics
        
        if self.justification == 1:
            return lyrics
        elif self.justification == 0:
            return [line.center(self.width) for line in lyrics]
        else:
            return [line.rjust(self.width) for line in lyrics]

    def get_text(self):
        return '\n'.join(line for line in self.lyrics)


if __name__ == '__main__':

    if len(sys.argv) >= 5:
        artist = sys.argv[1].strip()
        title = sys.argv[2].strip()
        width = int(sys.argv[-2])
        height = int(sys.argv[-1])

        track = Track(artist, title, 0, width, height, True)
        track.get_lyrics()
        topline = str(track.track_name).center(width) + '\n' + (round(width * 0.8) * '-').center(width - 1)

        print(topline, track.get_text())

    else:
        print('No Track info provided, Exiting...')
        exit

