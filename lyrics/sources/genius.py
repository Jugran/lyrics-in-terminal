import re

from typing import List

from lyrics.sources.base import SourceBase


class GeniusSource(SourceBase):

    def __init__(self) -> None:
        super().__init__()
        self.track_name = None

    async def extract_html(self, html: str) -> str | None:
        ''' finds genius website link and
            returns html text from genius

            if genius link not found returns None
        '''
        regex = re.compile(r'(http[s]?://genius.com/(?!albums)(?:.*?))&amp')
        gns_url = regex.search(html)

        if gns_url is None:
            return None

        gns_url = gns_url.group(1)
        gns_html = await self.get_html(gns_url, header={})

        if gns_html is None:
            return None
        return gns_html

    async def parse_lyrics(self, html: str | None) -> List[str] | None:
        ''' parses lyrics from genius html
            returns list if strings of lyrics or None if lyrics not found
        '''
        if html is None:
            return None

        gns_regex = re.compile(
            '<div data-lyrics-container="true" (?:.*?)(>.*?<)/div>', re.S)
        ly = gns_regex.findall(html)

        if ly is None:
            # Genius lyrics not found
            return None

        lyrics_lines = ''
        for ly_section in ly:
            ly_section = ly_section.replace('&#x27;', "'")
            line_regex = re.compile(r'>([^<]+?)<', re.S)
            lines = line_regex.findall(ly_section)
            lyrics_lines += "\n".join(lines)

        lyrics_lines = re.sub(r'\n{2,}', '\n', lyrics_lines)
        lyrics_lines = lyrics_lines.replace('\n[', '\n\n[')

        lyrics_lines = lyrics_lines.split('\n')

        return lyrics_lines

    async def get_lyrics(self, html: str) -> List[str]:
        ''' returns list of strings
        '''
        html = await self.extract_html(html)
        return await self.parse_lyrics(html)
