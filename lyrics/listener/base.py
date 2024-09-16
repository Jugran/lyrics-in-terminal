#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class PlayerBase(ABC):

    @abstractmethod
    async def check_playing(self) -> bool:
        ''' checks playing status of current player

        Returns:
            bool: playing status
        '''
        pass

    @abstractmethod
    async def set_listner(self) -> None:
        ''' set player listener
        '''
        pass

    @abstractmethod
    async def stop_listner(self) -> None:
        ''' stop player listener
        '''
        pass

    @abstractmethod
    async def update_metadata(self) -> None:
        ''' fetch player metadata on request
        '''
        pass

    # @abstractmethod
    # async def update_volume(self) -> None:
    #     ''' fetch player volume on request
    #     '''
    #     pass

    @abstractmethod
    async def main(self) -> None:
        ''' main function of player
        '''
        pass
