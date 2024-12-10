import os
import asyncio
from typing import List, Tuple

from lyrics import Logger, utils, CACHE_PATH
from lyrics.sources import Source
from lyrics.sources.genius import GeniusSource
from lyrics.sources.azlyrics import AZLyricsSource
from lyrics.sources.google import GoogleSource
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from lyrics.lyrics_in_terminal import LyricsInTerminal


class Status(Enum):
    IDLE = 0
    LOADING = 1
    LOADED = 2
    ERROR = 3


class Track:
    def __init__(self,
                 controller: "LyricsInTerminal|None" = None,
                 artist='',
                 title='',
                 align=1,
                 width=0,
                 default_source=Source.GOOGLE
                 ):

        self.controller = controller
        self.title = title
        self.artist = artist
        self.alignment = align
        self.width = width
        self.length = 0
        self.lyrics = []
        self.source = default_source
        self.album = ''
        self.trackid = None
        self.sources = [Source.GOOGLE, Source.AZLYRICS, Source.GENIUS]
        self.status = Status.IDLE
        self.task = None

    @property
    def window(self):
        return self.controller.window

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
        trackinfo = utils.align(
            [self.title, self.artist, self.album], width, self.alignment)

        offset = self.alignment % 2
        padding = ' ' * offset
        trackinfo = [padding + t + ' ' *
                     (width - len(t) - offset) for t in trackinfo]

        return trackinfo

    def update(self, artist, title, album, trackid):
        ''' update currently playing track info, (change track)
        '''
        Logger.debug(f'Updating track: {artist} - {title}')
        self.artist = artist
        self.title = title
        self.album = album
        self.trackid = trackid

    async def update_lyrics(self, cycle_source=False, cache=True):
        ''' updates lyrics from source
        '''
        if self.task is not None:
            self.task.cancel()

        self.task = asyncio.create_task(
            self._update_lyrics(cycle_source, cache))

        await self.task

    async def _update_lyrics(self, cycle_source=False, cache=True):
        ''' loads lyrics from source
        '''
        self.status = Status.LOADING

        if cycle_source:
            self.next_source()
            source = self.source
            cache = False
        else:
            source = Source.ANY

        lyrics, source = await self.fetch_lyrics(source, cache=cache)
        self.set_lyrics(lyrics, source)
        self.status = Status.LOADED

        if self.window is None:
            return

        Logger.debug('Refreshing screen...')
        self.window.update_track()

        if len(lyrics) > 2:
            self.window.add_notif(f'Source: {self.source}')

    async def fetch_lyrics(self, source: Source, cache: bool = True) -> Tuple[List[str] | None, Source | None]:
        ''' returns tuple of list of strings with lines of lyrics and found source
            also reads/write to cache file | if cache=True

            source -> source to fetch lyrics from ('google', 'azlyrics', 'genius', 'any')
            cache -> bool | whether to check lyrics from cache or not.
        '''
        filepath = utils.get_filename(self.track_name)

        if not os.path.isdir(CACHE_PATH):
            os.makedirs(CACHE_PATH)

        lyrics_lines = None
        # If cache enabled, then return cached lyrics
        if os.path.isfile(filepath) and cache:
            # cache lyrics exist
            with open(filepath) as file:
                lyrics_lines = file.read().splitlines()

            lyrics_lines = lyrics_lines if len(lyrics_lines) > 0 else None
            return lyrics_lines, Source.CACHE

        google = GoogleSource(self.track_name)
        search_html = await google.extract_html()

        found_source = None

        # cycle though each source if lyrics not found if source is not 'any'
        # else get source from specified source
        if source == Source.GOOGLE or source == Source.ANY:
            lyrics_lines = google.parse_lyrics(search_html)
            found_source = Source.GOOGLE if lyrics_lines is not None else None

        if source == Source.AZLYRICS or (source == Source.ANY and found_source is None):
            azlyrics = AZLyricsSource()
            lyrics_lines = await azlyrics.get_lyrics(search_html)
            found_source = Source.AZLYRICS if lyrics_lines is not None else None

        if source == Source.GENIUS or (source == Source.ANY and found_source is None):
            genius = GeniusSource()
            lyrics_lines = await genius.get_lyrics(search_html)
            found_source = Source.GENIUS if lyrics_lines is not None else None

        if lyrics_lines is None or len(lyrics_lines) < 2:
            Logger.debug(f'Lyrics not found - {source}, {self.track_name}')
            return None, source

        Logger.debug(f'Lyrics found - {found_source}, {self.track_name}')
        return lyrics_lines, found_source

    def set_lyrics(self, lyrics: List[str] | None, source: Source, save=True):
        ''' set lyrics and source for track

            lyrics -> list of strings
            source -> source to fetch lyrics from ('google', 'azlyrics', 'genius', 'any')
            save -> bool | whether to save lyrics to cache
        '''
        if source is not None and source != Source.ANY:
            self.source = source

        if lyrics is None:
            lyrics = ['Lyrics not found in ' + str(source) + ' :(']
            save = False

        self.lyrics = lyrics

        Logger.debug(f'Lyrics set - {self.lyrics}, {self.source}')
        self.width = len(max(self.lyrics, key=len))
        self.length = len(self.lyrics)

        if save:
            filepath = utils.get_filename(self.track_name)
            with open(filepath, 'w') as file:
                text = '\n'.join(self.lyrics)
                file.write(text)

    def next_source(self):
        ''' cycle to next source
        '''
        if self.source is None or self.source == Source.CACHE:
            self.source = self.sources[-1]

        curr_source = self.sources.index(self.source)
        next_source = (curr_source + 1) % len(self.sources)
        self.source = self.sources[next_source]
        Logger.info(f'Next source: {self.source}')

    def get_text(self, wrap=False, width=0):
        ''' returns lyrics text seperated by '\\n'
        '''
        if wrap:
            lyrics = utils.wrap_text(self.lyrics, width)
        else:
            lyrics = self.lyrics

        if len(lyrics) == 0:
            lyrics = ['Lyrics not found in ' + str(self.source) + ' :(']

        self.width = len(max(lyrics, key=len))
        self.length = len(lyrics)

        lyrics = utils.align(lyrics, self.width, self.alignment)

        return '\n'.join(line for line in lyrics)

    def edit_lyrics(self):
        ''' open lyrics file in text editor present in CONFIG path
        '''
        utils.edit_lyrics(self.track_name)

    def delete_lyrics(self):
        ''' delete lyrics file
        '''
        return utils.delete_lyrics(self.track_name)
