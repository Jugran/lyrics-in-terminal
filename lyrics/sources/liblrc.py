from typing import List, Tuple

from lyrics import Logger
from lyrics import utils
from lyrics.sources.base import SourceBase


class LibLRCSource(SourceBase):

    def __init__(self) -> None:
        super().__init__()
        self.url = "https://lrclib.net/api/get"

    def extract_html(self, html):
        return super().extract_html(html)

    def parse_lyrics(self, html):
        return super().parse_lyrics(html)

    def extract_lyrics(self, response: dict) -> Tuple[List[str] | None, List[str] | None, bool]:
        """
        Extracts synced lyrics from lrclib.net
        Returns:
            Tuple of (synced lyrics list, lyrics list, is_instrumental)
        """
        if response is None:
            Logger.error("LibLRC response is None")
            return (None, None, False)


        if response.get("statusCode") == 404:
            Logger.error(response.get("message"))
            return (None, None, False)

        if response.get("instrumental", False):
            return (None, None, True)

        lyrics = response.get("plainLyrics", None)
        synced_lyrics = response.get("syncedLyrics", None)

        if synced_lyrics is not None:
            return (synced_lyrics.split('\n'), lyrics, False)

        if lyrics is not None:
            lyrics = lyrics.split('\n')

        return (synced_lyrics, lyrics, False)

    async def fetch_lyrics(self, artist_name, track_name) -> dict | None:
        ''' returns liblrc response
        '''
        try:
            query_params = {"artist_name": artist_name,
                            "track_name": track_name}
            return await self.fetch_json(self.url, query_params)
        except Exception as e:
            Logger.error(f"Failed to fetch LibLRC lyrics: {e}")
            return None

    async def get_lyrics(self, track_name: str) -> Tuple[List[str] | None, List[str]]:
        ''' returns list of strings
        Returns:
            Tuple of (lyrics list, lyrics timings)
        '''
        artist_name, track_name = track_name.split(" - ", 1)
        response = await self.fetch_lyrics(artist_name, track_name)
        synced_lyrics, lyrics, is_instrumental = self.extract_lyrics(response)

        if is_instrumental:
            intrumental_text = "Instrumental Track \n Sit back and relax."
            return ([intrumental_text], None)

        if synced_lyrics is not None:
            return utils.format_synced_lyrics(synced_lyrics)

        return (lyrics, None)
