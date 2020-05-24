#!/usr/bin/env python3
# Telegram Download Daemon
# Author: Alfonso E.M. <alfonso@el-magnifico.org>
# You need to install telethon (and cryptg to speed up downloads)

from os import getenv

from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel
import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s]%(name)s:%(message)s',level=logging.WARNING)

import argparse

TELEGRAM_DEAMON_API_ID = getenv("TELEGRAM_DEAMON_API_ID")
TELEGRAM_DEAMON_API_HASH = getenv("TELEGRAM_DEAMON_API_HASH")
TELEGRAM_DEAMON_CHANNEL = getenv("TELEGRAM_DEAMON_CHANNEL")

parser = argparse.ArgumentParser(description="Script to download files from Telegram Channel.")
parser.add_argument("--api-id", required=TELEGRAM_DEAMON_API_ID == None, type=int, default=TELEGRAM_DEAMON_API_ID, help='api_id from https://core.telegram.org/api/obtaining_api_id (default is TELEGRAM_DEAMON_API_ID env var)')
parser.add_argument("--api-hash", required=TELEGRAM_DEAMON_API_HASH == None, type=str, default=TELEGRAM_DEAMON_API_HASH, help='api_hash from https://core.telegram.org/api/obtaining_api_id (default is TELEGRAM_DEAMON_API_HASH env var)')
parser.add_argument("--dest", type=str, default=getenv("TELEGRAM_DEAMON_DEST", "/telegram-downloads"), help='Destenation path for downloading files (default is /telegram-downloads).')
parser.add_argument("--channel", required=TELEGRAM_DEAMON_CHANNEL == None, type=int, default=TELEGRAM_DEAMON_CHANNEL, help='Channel id to download from it (default is TELEGRAM_DEAMON_CHANNEL env var')
args = parser.parse_args()

api_id = args.api_id
api_hash = args.api_hash
channel_id = args.channel
downloadFolder = args.dest

# Edit these lines:
proxy = None
# End of interesting parameters 

session = "DownloadDaemon"

client = TelegramClient(session, api_id, api_hash, proxy=proxy).start()

@client.on(events.NewMessage())
async def handler(event):
    
    async def log_reply(reply):
        print(reply)
        await event.reply(reply)

    if event.to_id != PeerChannel(channel_id):
        return
    
    print(event)
    
    if event.media:
       filename=event.media.document.attributes[0].file_name
       log_reply(f"Downloading file {filename} ({event.media.document.size} bytes)")

       await client.download_media(event.message, downloadFolder)
       log_reply(f"{filename} ready")


with client:
    client.run_until_disconnected()



