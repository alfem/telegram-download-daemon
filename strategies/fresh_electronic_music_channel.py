import string

from config.daemon_config import DaemonConfig
from strategies.base import BaseChannelManager
from sanitize_filename import sanitize


class FreshElectronicMusicChannelStrategy(BaseChannelManager):

    def __init__(self, daemon_config: DaemonConfig):
        super().__init__(daemon_config)
        self._managed_channel: int = 1290586824

    def extract_folder_name(self, picture_message: string) -> string:
        print(f"Input message received: {picture_message}")
        print("Splitted output:")
        print(picture_message.splitlines())
        print(f"Resolved folder name: ", picture_message.splitlines()[2])
        return sanitize(picture_message.splitlines()[2])

    @property
    def managed_channel(self) -> int:
        return self._managed_channel

