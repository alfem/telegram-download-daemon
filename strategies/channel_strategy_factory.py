from abc import ABC

# Factory class that returns singleton instances of channel managers depending on the channel id passed
# as the input argument.
from config.daemon_config import DaemonConfig
from strategies.base import BaseChannelManager
from strategies.exception.ChannelStrategyNotFoundException import ChannelStrategyNotFoundException
from strategies.fresh_electronic_music_channel import FreshElectronicMusicChannelStrategy
from strategies.prometeo_releases_music import PrometeoReleasesMusicChannelStrategy
from strategies.rave_music_releases_channel import RaveMusicReleasesChannelStrategy


class ChannelStrategyFactory(ABC):
    def __init__(self, daemon_config: DaemonConfig):
        self.fresh_electronic_music_manager: FreshElectronicMusicChannelStrategy = \
            FreshElectronicMusicChannelStrategy(daemon_config)
        self.rave_music_releases_manager: RaveMusicReleasesChannelStrategy = \
            RaveMusicReleasesChannelStrategy(daemon_config)
        self.prometeo_releases_music_manager : PrometeoReleasesMusicChannelStrategy = PrometeoReleasesMusicChannelStrategy(daemon_config)

    def get_channel_manager(self, channel_id: int) -> BaseChannelManager:
        target_strategy: BaseChannelManager
        print(f"Input channel id to the factory: {channel_id}")
        if channel_id in self.fresh_electronic_music_manager.managed_channel:
            print(f"Manager detected as FEM channel manager.")
            target_strategy = self.fresh_electronic_music_manager
        elif channel_id in self.rave_music_releases_manager.managed_channel:
            print(f"Manager detected as RMR channel manager.")
            target_strategy = self.rave_music_releases_manager
        elif channel_id in self.prometeo_releases_music_manager.managed_channel():
            print(f"Manager detected as PRM channel manager.")
            target_strategy = self.prometeo_releases_music_manager
        else:
            print(f"Provided channel id not managed by any existing manager.")
            raise ChannelStrategyNotFoundException()

        return target_strategy
