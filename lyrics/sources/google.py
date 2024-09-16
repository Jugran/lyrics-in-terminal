import re

from typing import List
from urllib.parse import quote

from lyrics.sources.base import SourceBase


class GoogleSource(SourceBase):
    URL = 'https://www.google.com/search?q='
    CLASS_NAME = r'\w{5,7} \w{4,5} \w{5,7}'  # dependent on User-Agent

    def __init__(self) -> None:
        super().__init__()
        self.track_name = None
        self.html = None

    def query(self):
        '''encodes search query
        '''
        self.track_name = re.sub(
            r'(\[.*\].*)|(\(.*\).*)', '', self.track_name).strip()
        return quote(self.track_name + ' lyrics')

    async def extract_html(self, html: str | None = None) -> str | None:
        ''' extracts google search html
        '''
        if self.track_name is None:
            return None
        q = self.query()
        url = self.URL + q
        self.html = await self.get_html(url)
        return self.html

    async def parse_lyrics(self, html: str | None) -> List[str] | None:
        ''' parses google result html
            returns list of strings or None if no lyrics found
        '''
        if html is None:
            return None

        html_regex = re.compile(
            r'<div class="{}">([^>]*?)</div>'.format(self.CLASS_NAME), re.S)

        text_list = html_regex.findall(html)

        if len(text_list) < 2:
            # No google result found!
            return None

        lyrics_lines = []
        for l in text_list[1:]:
            # lyrics must be multiline,
            # ignore the artist info below lyrics
            if l.count('\n') > 2:
                lyrics_lines += l.split('\n')
        if len(lyrics_lines) < 5:
            # too short match for lyrics
            return None

        return lyrics_lines

    async def get_lyrics(self, track_name) -> List[str]:
        ''' returns list of strings
        '''
        self.track_name = track_name
        html = await self.extract_html()
        return await self.parse_lyrics(html)
