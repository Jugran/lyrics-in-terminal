import re

from typing import List

from lyrics.sources.base import SourceBase


class AZLyricsSource(SourceBase):

    def __init__(self) -> None:
        super().__init__()
        self.track_name = None

    async def extract_html(self, html: str) -> str | None:
        ''' finds azlyrics website link and
            returns html text from azlyrics

            if azlyrics link not found returns None
        '''
        regex = re.compile(r'(http[s]?://www.azlyrics.com/lyrics(?:.*?))&amp')
        az_url = regex.search(html)

        if az_url is None:
            return None

        header = {'User-Agent': 'Mozilla/5.0 Firefox/70.0'}
        az_url = az_url.group(1)
        az_html = await self.get_html(az_url, header)

        return az_html

    def parse_lyrics(self, html: str | None) -> List[str] | None:
        ''' parses lyrics from azlyrics html
            returns list if strings of lyrics

            if lyrics not found returns error string
        '''
        if html is None:
            return None

        az_regex = re.compile(
            r'<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->(.*)<!-- MxM banner -->', re.S)

        ly = az_regex.search(html)
        if ly is None:
            # Az lyrics not found
            return None

        # remove stray html tags
        ly = re.sub(r'<[/]?\w*?>', '', ly.group(1)).strip()

        # replace html entities
        rep = {'&quot;': '\"', '&amp;': '&', '\r': ''}
        replace_patten = '|'.join(rep.keys())
        ly = re.sub(replace_patten, lambda match: rep[match.group(0)], ly)
        lyrics_lines = ly.split('\n')

        return lyrics_lines

    async def get_lyrics(self, html: str) -> List[str] | None:
        ''' returns list of strings
        '''
        html = await self.extract_html(html)
        # NOTE: this parsing can be offloaded to a different thread
        return self.parse_lyrics(html)
