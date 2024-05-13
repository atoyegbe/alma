
import abc


class StreamData(abc.ABC):
    @abc.abstractmethod
    async def __init__(self):
        pass

    @abc.abstractmethod
    async def get_user_playlist(self):
        pass

    @abc.abstractmethod
    async def get_followed_artists(self):
        pass

    @abc.abstractmethod
    async def get_top_artists(self):
        pass

    @abc.abstractmethod
    async def get_top_tracks(self):
        pass
