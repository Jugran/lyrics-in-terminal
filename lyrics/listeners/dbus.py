import re
import dbus_next
import asyncio

from dbus_next.aio import ProxyInterface, MessageBus
from dbus_next.message import Message, MessageType

from lyrics.listeners.base import PlayerBase
from lyrics.sources import Source
from lyrics.track import Track
from lyrics import Logger

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lyrics.lyrics_in_terminal import LyricsInTerminal


def parse_variant_to_dict(variant):
    """Convert a dbus-next Variant type to a Python dictionary."""
    if not isinstance(variant, dbus_next.Variant):
        Logger.warning(
            f'Provided object is not a dbus-next Variant. {variant}')
        value = variant
    else:
        value = variant.value

    if isinstance(value, dict):
        return {k: parse_variant_to_dict(v) if isinstance(v, dbus_next.Variant) else v for k, v in value.items()}
    elif isinstance(value, list):
        return [parse_variant_to_dict(v) if isinstance(v, dbus_next.Variant) else v for v in value]
    else:
        return value


class DbusListener(PlayerBase):
    def __init__(self, controller: "LyricsInTerminal", name: str, source: Source, autoswitch: bool, timeout: int):
        self.controller = controller
        self.player_name = name
        self.default_source = source

        self.autoswitch = autoswitch
        self.timeout = timeout / 1000

        self.running = False

        self.player_object: ProxyInterface = None
        self.player_properties: ProxyInterface = None
        self.session_bus: MessageBus = None

        self.object_path = '/org/mpris/MediaPlayer2'
        self.wait_task = None
    
    @property
    def track(self):
        return self.controller.track

    async def get_service_interface(self, bus_name) -> tuple[ProxyInterface, ProxyInterface]:
        ''' get player interfaces

        Parameters:
            bus_name: str

        Returns:
            player_interface: ProxyInterface
            player_properties: ProxyInterface
        '''
        try:
            introspection = await self.session_bus.introspect(bus_name, self.object_path)
            proxy_obj = self.session_bus.get_proxy_object(
                bus_name, self.object_path, introspection)
            player_interface = proxy_obj.get_interface(
                'org.mpris.MediaPlayer2.Player')
            player_properties = proxy_obj.get_interface(
                'org.freedesktop.DBus.Properties'
            )

            return player_interface, player_properties
        except dbus_next.errors.DBusError as e:
            Logger.error(
                f'Error occured while retrieving player interface: {e}')
            print("Error occured")

    async def set_active_player(self):
        ''' set playing player as active
        '''

        # Call the ListNames method to get the list of active service names
        reply = await self.session_bus.call(
            Message(destination='org.freedesktop.DBus',
                    path='/org/freedesktop/DBus',
                    interface='org.freedesktop.DBus',
                    member='ListNames'))

        if reply.message_type == MessageType.ERROR:
            Logger.error(f'Error occured while retrieving players: {
                         reply.body[0]}')
            return

        services = reply.body[0]

        for service in services:
            if not re.findall(r'org.mpris.MediaPlayer2|plasma-browser-integration', service, re.IGNORECASE):
                continue

            player_object, player_properties = await self.get_service_interface(service)
            if player_object is None:
                continue

            status = await player_object.get_playback_status()
            if status == 'Playing':
                Logger.info(f'Active player found: {service}')
                self.player_name = service.split('MediaPlayer2.')[-1]
                self.player_object = player_object
                self.player_properties = player_properties
                self.running = True
                return

    async def set_interfaces(self):
        ''' sets dbus session bus and player interface
        '''

        if not self.session_bus:
            self.session_bus = await dbus_next.aio.MessageBus().connect()

        if self.autoswitch:
            await self.set_active_player()
        else:
            player_object, player_properties = await self.get_service_interface(f'org.mpris.MediaPlayer2.{self.player_name}')

            if player_object is not None:
                self.running = True
                self.player_object = player_object
                self.player_properties = player_properties
            else:
                self.running = False
                self.player_object = None
                self.player_properties = None

    async def properties_changed(self, interface, changed, invalidated):
        ''' properties changed handler

        Parameters
        ----------
        interface : ProxyInterface
            player interface
        changed : dict
            changed properties
        invalidated : list
            invalidated properties
        '''

        Logger.info(f'properties changed: {changed}')
        metadata = changed.get('Metadata', None)

        if metadata is not None:
            metadata = parse_variant_to_dict(metadata)

        # PlaybackStatus and metadata can be absent from changed dict
        playback_status = changed.get('PlaybackStatus', None)

        if playback_status is not None:
            playback_status = parse_variant_to_dict(playback_status)
            self.running = (playback_status == 'Playing')

        if not self.running and self.wait_task is None:
            await self.clear_player_and_wait()
            return

        if metadata is None:
            Logger.info('metadata is None')
            await self.controller.update_track(playback_status, None)
            return

        track_data = self.parse_metadata(metadata)

        if track_data is None:
            Logger.info('track_data is None')
            await self.controller.update_track(playback_status, None)
            return

        await self.controller.update_track(playback_status, track_data)

    async def clear_player_and_wait(self):
        await self.stop_listner()
        self.playing = False

        if self.autoswitch:
            self.player_object = None
            self.player_properties = None

        self.wait_task = asyncio.create_task(self.main())
        await self.wait_task
        self.wait_task = None

    def parse_metadata(self, metadata) -> dict:
        ''' parses dbus changed metadata

        Parameters
        ----------
        metadata : dict
            metadata from dbus

        Returns: 
        ----------
        dict with track data
        '''
        data = {
            "title": '',
            "artist": '',
            "album": '',
            "trackid": '',
        }

        try:
            title = metadata['xesam:title']
            if title.strip() == '':
                # if Title is empty, don't update
                return None

            artist = ''
            if 'xesam:artist' in metadata:
                artist = metadata['xesam:artist']
            artist = artist[0] if isinstance(artist, list) else artist

            if re.search('chromium|plasma', self.player_name) and '-' in title:
                # in case of artist in the title
                artist, title, *_ = title.split('-')

            title = title.strip()
            artist = artist.strip()

            album = metadata.get('xesam:album')
            album = '' if album is None else album
            trackid = metadata.get('mpris:trackid')
            trackid = title if trackid is None else trackid
        except (IndexError, KeyError) as e:
            self.running = False
            return None

        if trackid.find('spotify:ad') != -1:
            self.running = False
            return None
        elif self.track.trackid != trackid or self.track.title != title:
            # update track
            data['title'] = title
            data['artist'] = artist
            data['album'] = album
            data['trackid'] = trackid
            return data

    async def check_playing(self):
        ''' checks playing status of current player
        '''

        if self.player_object:
            status = await self.player_object.get_playback_status()
            self.running = (status == 'Playing')

        return self.running

    async def set_listner(self):
        ''' sets dbus player properties changed listener
        '''
        if self.player_object is None:
            return

        self.player_properties.on_properties_changed(self.properties_changed)
        Logger.info('listener started')

    async def stop_listner(self):
        ''' stops dbus player properties changed listener
        '''
        if self.player_object is None:
            return

        self.player_properties.off_properties_changed(self.properties_changed)
        Logger.info('listener stopped')

    async def update_metadata(self):
        ''' updates metadata on request
        '''
        if self.player_object is None:
            Logger.info('Cannot init metadata, player object is None')
            return

        metadata = await self.player_object.get_metadata()
        metadata = parse_variant_to_dict(metadata)
        Logger.info(f'to dict metadata: {metadata}')
        track_data = self.parse_metadata(metadata)
        Logger.info(f'parsed metadata: {track_data}')
        if track_data is None:
            return

        await self.controller.update_track(None, track_data)

    async def wait_for_player(self):
        ''' waits for player to be running
        '''
        while not await self.check_playing():
            Logger.info('player is not running, waiting...')
            await asyncio.sleep(self.timeout)
            await self.set_interfaces()

    async def main(self):
        await self.set_interfaces()
        await self.wait_for_player()
        await self.update_metadata()
        await self.set_listner()
