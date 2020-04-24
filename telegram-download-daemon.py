#!/usr/bin/env python3
# Telegram Download Daemon
# Author: Alfonso E.M. <alfonso@el-magnifico.org>
# You need to install telethon (and cryptg to speed up downloads)


from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel
import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s]%(name)s:%(message)s',level=logging.WARNING)

# Edit these lines:
api_id = NNNNNN
api_hash = "XXXXXXXXXXXXXXXXXXXXXXXXXX"
downloadFolder="/tmp"
channel_id= NNNNNNNNN
proxy = None  
# End of interesting parameters 

session = "DownloadDaemon"

client = TelegramClient(session, api_id, api_hash, proxy=proxy).start()

@client.on(events.NewMessage())
async def handler(event):
    
    async def log_respond(respond):
        print(respond)
        await event.respond(respond)

    if event.to_id != PeerChannel(channel_id):
        return
    
    print(event)
    
    if event.media:
       filename=event.media.document.attributes[0].file_name
       log_respond(f"Downloading file {filename} ({event.media.document.size} bytes)")

       await client.download_media(event.message, downloadFolder)
       log_respond(f"{filename} ready")


with client:
    client.run_until_disconnected()



