from enum import Enum

# enum for sources


class Source(Enum):
    GENIUS = 'genius'
    AZLYRICS = 'azlyrics'
    GOOGLE = 'google'
    LIBLRC = 'lrclib'
    LRC = 'lrc'
    ANY = 'any'
    CACHE = 'cache'

    def __str__(self):
        return self.value
