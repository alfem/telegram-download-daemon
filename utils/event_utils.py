import math
import random
import string
import time
from abc import ABC
from mimetypes import guess_extension
from typing import Dict, Any

from telethon import events
from telethon.tl.types import DocumentAttributeFilename, DocumentAttributeVideo
import logging


class EventUtils(ABC):
    last_update: float = 0
    update_frequency: int = 10

    def __init__(self, last_update: float = 0, update_frequency: int = 10):
        self.last_update = last_update
        self.update_frequency = update_frequency
        self.target_download_folder = ""

    async def log_reply(self, message, reply):
        print(reply)
        await message.edit(reply)

    def get_random_id(self, length: int):
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for x in range(length))

    def get_file_name(self, event: events.NewMessage.Event):
        media_file_name: str = "unknown"

        if hasattr(event.media, 'photo'):
            media_file_name = str(event.media.photo.id) + ".jpeg"
        elif hasattr(event.media, 'document'):
            for attribute in event.media.document.attributes:
                if isinstance(attribute, DocumentAttributeFilename):
                    media_file_name = attribute.file_name
                    break
                if isinstance(attribute, DocumentAttributeVideo):
                    if event.original_update.message.message != '':
                        media_file_name = event.original_update.message.message
                    else:
                        media_file_name = str(event.message.media.document.id)
                    media_file_name += guess_extension(event.message.media.document.mime_type)

        media_file_name = "".join(c for c in media_file_name if c.isalnum() or c in "()._- ")

        return media_file_name

    async def set_progress(self, filename: str, message, received: int, total: int, in_progress: Dict) -> None:

        if received >= total:
            try:
                in_progress.pop(filename)
            except KeyError as key_error:
                print(f"Key does not exist in the queu because it was already processed, all fine.", key_error)
                pass
            except Exception as e:
                print(f"Error processing progress", e)
                logging.exception("message")
                pass
            return
        percentage = math.trunc(received / total * 10000) / 100

        progress_message = "{0} % ({1} / {2})".format(percentage, received, total)
        in_progress[filename] = progress_message

        current_time = time.time()
        if (current_time - self.last_update) > self.update_frequency:
            await self.log_reply(message, progress_message)
            self.last_update = current_time
