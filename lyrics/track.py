#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lyrics import util


class Track:
    def __init__(self,
                 artist='',
                 title='',
                 align=1,
                 width=0):

        self.title = title
        self.artist = artist
        self.alignment = align
        self.width = width
        self.length = 0
        self.lyrics = []
        self.timestamps = []  # List of timestamps corresponding to lyrics lines
        self.source = None
        self.album = None
        self.trackid = None
        self.sources = ['lrc', 'lrclib', 'google', 'azlyrics', 'genius']

    def __str__(self):
        ''' trackname in format "{artist} - {title}"
        '''
        return self.artist + ' - ' + self.title

    @property
    def track_name(self):
        ''' returns trackname in format "{artist} - {title}"
        '''
        return self.artist + ' - ' + self.title

    def reset_width(self):
        ''' reset track width (when track/lyrics is changed)
        '''
        self.width = len(max(self.lyrics, key=len))

    def track_info(self, width):
        ''' returns properly formated (3 lined, title, artist, album) track info for 
            title 
        '''
        trackinfo = util.align([self.title, self.artist, self.album], width, self.alignment)
        
        offset = self.alignment%2
        padding = ' ' * offset
        trackinfo = [padding + t + ' ' * (width - len(t) - offset) for t in trackinfo]

        return trackinfo

    def update(self, artist, title, album, trackid):
        ''' update currently playing track info, (change track)
        '''
        self.artist = artist
        self.title = title
        self.album = album
        self.trackid = trackid
        # self.art_url = art_url
        # self.get_lyrics()

    def get_lyrics(self, source, cycle_source=False, cache=True):
        ''' fetch lyrics off the internet
        '''
        if self.source is None or self.source == 'cache':
            self.source = source or self.sources[0]

        if cycle_source:
            curr_source = self.sources.index(self.source)
            next_source = (curr_source + 1) % len(self.sources)
            source = self.sources[next_source]
            cache = False
        else:
            source = 'any'

        result = util.get_lyrics(self.track_name, source, cache=cache)
        if len(result) == 3:  # New format with timestamps
            self.lyrics, self.timestamps, self.source = result
        else:  # Old format compatibility
            self.lyrics, self.source = result
            self.timestamps = None
            
        self.width = len(max(self.lyrics, key=len)) if self.lyrics else 0
        self.length = len(self.lyrics)

    def set_lyrics_with_timestamps(self, lyrics_list, timestamps_list):
        """Set lyrics and their corresponding timestamps.
        
        Args:
            lyrics_list: List of lyrics lines
            timestamps_list: List of timestamps (in seconds) for each line
        """
        self.lyrics = lyrics_list
        self.timestamps = timestamps_list
        self.length = len(self.lyrics)
        if self.lyrics:
            self.reset_width()

    def refresh_lyrics(self, source='any', cache=True, cycle_source=False):
        ''' refresh lyrics from source
        '''
        if cycle_source and self.source in self.sources:
            i = self.sources.index(self.source) + 1
            source = self.sources[i % len(self.sources)]

        result = util.get_lyrics(self.track_name, source, cache=cache)
        if len(result) == 3:  # New format with timestamps
            self.lyrics, self.timestamps, self.source = result
        else:  # Old format compatibility
            self.lyrics, self.source = result
            self.timestamps = None
            
        self.width = len(max(self.lyrics, key=len)) if self.lyrics else 0
        self.length = len(self.lyrics)

    def get_text(self, wrap=False, width=0):
        ''' returns lyrics text seperated by '\\n'
        '''
        if not self.lyrics:
            return ''
            
        if wrap:
            lyrics=util.wrap_text(self.lyrics, width)
        else:
            lyrics=self.lyrics

        self.width = len(max(lyrics, key=len))
        self.length = len(lyrics)

        lyrics = util.align(lyrics, self.width, self.alignment)

        return '\n'.join(line for line in lyrics)
    
    def edit_lyrics(self):
        ''' open lyrics file in text editor present in CONFIG path
        '''
        util.edit_lyrics(self.track_name)


    def delete_lyrics(self):
        ''' delete lyrics file
        '''
        return util.delete_lyrics(self.track_name)
