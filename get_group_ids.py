import os
import sys


import time
from telethon.utils import get_display_name
from telethon.sync import TelegramClient
api_id = 1
api_hash = "x"
name = "x"
dialog_count = 600
with TelegramClient(name, api_id, api_hash) as client:
    for dialog in client.get_dialogs():
        # print(message.sender_id, ':', message.text)
        print(get_display_name(dialog.entity), dialog.entity.id)
