from abc import ABC, abstractmethod


class PlayerBase(ABC):

    @abstractmethod
    async def check_playing(self) -> bool:
        ''' checks playing status of current player

        Returns:
            bool: playing status
        '''
        raise NotImplementedError()

    @abstractmethod
    async def set_listner(self) -> None:
        ''' set player listener
        '''
        raise NotImplementedError()

    @abstractmethod
    async def stop_listner(self) -> None:
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
    async def main(self) -> None:
        ''' main function of player
        '''
        raise NotImplementedError()