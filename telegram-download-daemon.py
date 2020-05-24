#!/usr/bin/env python3
# Telegram Download Daemon
# Author: Alfonso E.M. <alfonso@el-magnifico.org>
# You need to install telethon (and cryptg to speed up downloads)

from os import getenv

from sessionManager import getSession, saveSession

from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, DocumentAttributeFilename
import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s]%(name)s:%(message)s',
                    level=logging.WARNING)

import argparse
import asyncio

TELEGRAM_DAEMON_API_ID = getenv("TELEGRAM_DAEMON_API_ID")
TELEGRAM_DAEMON_API_HASH = getenv("TELEGRAM_DAEMON_API_HASH")
TELEGRAM_DAEMON_CHANNEL = getenv("TELEGRAM_DAEMON_CHANNEL")

TELEGRAM_DAEMON_SESSION_PATH = getenv("TELEGRAM_DAEMON_SESSION_PATH")

parser = argparse.ArgumentParser(
    description="Script to download files from Telegram Channel.")
parser.add_argument(
    "--api-id",
    required=TELEGRAM_DAEMON_API_ID == None,
    type=int,
    default=TELEGRAM_DAEMON_API_ID,
    help=
    'api_id from https://core.telegram.org/api/obtaining_api_id (default is TELEGRAM_DAEMON_API_ID env var)'
)
parser.add_argument(
    "--api-hash",
    required=TELEGRAM_DAEMON_API_HASH == None,
    type=str,
    default=TELEGRAM_DAEMON_API_HASH,
    help=
    'api_hash from https://core.telegram.org/api/obtaining_api_id (default is TELEGRAM_DAEMON_API_HASH env var)'
)
parser.add_argument(
    "--dest",
    type=str,
    default=getenv("TELEGRAM_DAEMON_DEST", "/telegram-downloads"),
    help=
    'Destenation path for downloading files (default is /telegram-downloads).')
parser.add_argument(
    "--channel",
    required=TELEGRAM_DAEMON_CHANNEL == None,
    type=int,
    default=TELEGRAM_DAEMON_CHANNEL,
    help=
    'Channel id to download from it (default is TELEGRAM_DAEMON_CHANNEL env var'
)
args = parser.parse_args()

api_id = args.api_id
api_hash = args.api_hash
channel_id = args.channel
downloadFolder = args.dest

# Edit these lines:
proxy = None


# End of interesting parameters
async def sendHelloMessage(client, peerChannel):
    entity = await client.get_entity(peerChannel)
    print("Hi! Ready for you files!")
    await client.send_message(entity, "Hi! Ready for you files!")
 

async def log_reply(event : events.ChatAction.Event, reply):
    print(reply)
    await event.reply(reply)

def getFilename(event: events.NewMessage.Event):
    return next(x for x in event.media.document.attributes if isinstance(x, DocumentAttributeFilename)).file_name


with TelegramClient(getSession(), api_id, api_hash,
                    proxy=proxy).start() as client:

    saveSession(client.session)

    peerChannel = PeerChannel(channel_id)

    @client.on(events.NewMessage())
    async def handler(event):

        if event.to_id != peerChannel:
            return

        print(event)

        if event.media:
            filename=getFilename(event)
            await log_reply(
                event,
                f"Downloading file {filename} ({event.media.document.size} bytes)"
            )

            await client.download_media(event.message, downloadFolder)
            await log_reply(event, f"{filename} ready")
    
    async def start():
        await sendHelloMessage(client, peerChannel)
        await client.run_until_disconnected()

    client.loop.run_until_complete(start())
