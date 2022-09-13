import string

from config.daemon_config import DaemonConfig
from strategies.base import BaseChannelManager
from sanitize_filename import sanitize


class RaveMusicReleasesChannelStrategy(BaseChannelManager):

    def __init__(self, daemon_config: DaemonConfig):
        super().__init__(daemon_config)
        self._managed_channel = 1387836304

    def extract_folder_name(self, picture_message: string) -> string:
        print(f"Input message received: {picture_message}")
        print("Splitted output:")
        print(picture_message.splitlines())
        print(f"Resolved folder name: ", picture_message.splitlines()[0])
        line1: string = picture_message.splitlines()[0]
        hashtags: list = []
        index: int = 0

        if line1 is not None:
            hashtags = [i for i in line1.split() if i.startswith("#")]

        if len(line1.split()) == len(hashtags):
            index = 2

        return sanitize(picture_message.splitlines()[index])

    @property
    def managed_channel(self) -> int:
        return self._managed_channel
