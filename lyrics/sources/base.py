import aiohttp

from typing import List
from abc import ABC, abstractmethod


class SourceBase(ABC):
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch'
    }

    async def get_html(self, url: str, header: dict = HEADER) -> str:
        ''' returns html text from given url
        '''
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=header) as resp:
                resp.raise_for_status()
                return await resp.text()

    async def fetch_json(self, url: str, params: dict) -> dict:
        ''' returns json response
        '''
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                # Ensure that the response status is OK
                response.raise_for_status()
                # Parse the JSON response
                return await response.json()

    @abstractmethod
    async def extract_html(self, html: str) -> str | None:
        ''' extracts relavant html from google search html
        '''
        raise NotImplementedError()

    @abstractmethod
    def parse_lyrics(self, html: str | None) -> List[str] | None:
        ''' parses lyrics from html
        '''
        raise NotImplementedError()

    @abstractmethod
    async def get_lyrics(self) -> List[str] | None:
        ''' returns list of strings
        '''
        raise NotImplementedError()
