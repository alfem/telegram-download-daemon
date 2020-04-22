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
    if event.to_id != PeerChannel(channel_id):
        return
    print(event)
    if event.media:
       filename=event.media.document.attributes[0].file_name
       answer="Downloading file %s (%i bytes)" % (filename,event.media.document.size)
       print(answer)
       await event.respond(answer)

       await client.download_media(event.message,downloadFolder)
       await event.respond(filename+" ready")


with client:
    client.run_until_disconnected()



