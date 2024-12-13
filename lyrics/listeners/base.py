from abc import ABC, abstractmethod

from lyrics.sources import Source


class PlayerBase(ABC):

    def __init__(self, name: str, source: Source, autoswitch: bool, sync_available: bool, running: bool) -> None:
        """
        Initialize the player base.

        Args:
            name (str): The name of the player.
            source (Source): The default source of the player.
            autoswitch (bool): Whether the player should autoswitch.
            sync_available (bool): Whether the player supports synced lyrics.
            running (bool): Whether the player is currently running.
        """
        self.player_name = name
        self.default_source = source
        self.autoswitch = autoswitch
        self.sync_available = sync_available
        self.running = running

    @abstractmethod
    async def check_playing(self) -> bool:
        ''' checks playing status of current player

        Returns:
            bool: playing status
        '''
        raise NotImplementedError()

    @abstractmethod
    async def set_listener(self) -> None:
        ''' set player listener
        '''
        raise NotImplementedError()

    @abstractmethod
    async def stop_listener(self) -> None:
        ''' stop player listener
        '''
        raise NotImplementedError()

    @abstractmethod
    async def update_metadata(self) -> None:
        ''' fetch player metadata on request
        '''
        raise NotImplementedError()

    # @abstractmethod
    # async def update_volume(self) -> None:
    #     ''' fetch player volume on request
    #     '''
#             raise NotImplementedError()

    @abstractmethod
    async def get_position(self) -> int:
        ''' fetch player position on request
        '''
        raise NotImplementedError()

    @abstractmethod
    async def main(self) -> None:
        ''' main function of player
        '''
        raise NotImplementedError()
