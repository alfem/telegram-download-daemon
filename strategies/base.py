import asyncio
import os
import string
from os import path
from abc import ABC
from random import random
from typing import Dict, Callable, Any, Coroutine, Optional
from shutil import move

import telethon.tl.types
from telethon import TelegramClient, events, __version__
from telethon.tl.types import PeerChannel, DocumentAttributeFilename, DocumentAttributeVideo
from mimetypes import guess_extension

from config.daemon_config import DaemonConfig
from models.folder_container import FolderContainer
from utils.event_utils import EventUtils


class BaseChannelManager(ABC):

    def __init__(self, daemon_config: DaemonConfig):
        self.utils: EventUtils = EventUtils(daemon_config.last_update, daemon_config.update_frequency)
        self.daemon_config = daemon_config
        self.folder_name: string = ""

    def extract_folder_name(self, picture_message: string) -> string:
        """ Abstract method that children classes need to implement """
        pass

    def managed_channel(self) -> int:
        """ Abstract method that children classes need to implement """
        pass

    async def manage_new_message_event(self, client: TelegramClient, queue: asyncio.Queue,
                                       element: [], in_progress: Dict) -> telethon.tl.types.TypeMessage:
        event = element[0]
        message = element[1]
        folder_info: FolderContainer = element[2]
        try:
            filename = self.utils.get_file_name(event)
            file_name, file_extension = os.path.splitext(filename)
            tempfilename = file_name + "-" + self.utils.get_random_id(8) + file_extension

            if os.path.exists(
                    "{0}/{1}.{2}".format(self.daemon_config.temp, tempfilename, self.daemon_config.temp_suffix)) \
                    or path.exists("{0}/{1}".format(self.daemon_config.dest, filename)):
                if self.daemon_config.duplicates == "rename":
                    filename = tempfilename

            if hasattr(event.media, 'photo'):
                size = 0
                target_path: string = ""
                try:
                    # If we are processing a picture, we create the target folder to hold the image and the audio files
                    target_path = os.path.join(self.daemon_config.dest, folder_info.folder_name)
                    os.mkdir(target_path)
                except FileExistsError as e:
                    print(f"Path {target_path} already exists, no problem.")
            else:
                size = event.media.document.size

            await self.utils.log_reply(
                message,
                "Downloading file {0} ({1} bytes)".format(filename, size)
            )

            download_callback: Optional[(int, int)] = lambda received, total: self.utils.set_progress(
                filename, message, received, total, in_progress)

            await client.download_media(
                event.message,
                "{0}/{1}.{2}".format(
                    self.daemon_config.temp,
                    filename,
                    self.daemon_config.temp_suffix), progress_callback=download_callback)
            await self.utils.set_progress(filename, message, 100, 100, in_progress)
            move("{0}/{1}.{2}".format(self.daemon_config.temp, filename, self.daemon_config.temp_suffix),
                 "{0}/{1}".format(os.path.join(self.daemon_config.dest, folder_info.folder_name), filename))
            await self.utils.log_reply(message, "{0} ready".format(filename))
        except Exception as e:
            print(f"Error processing download logic", e)
            pass
        return message
