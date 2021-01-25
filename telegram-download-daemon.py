#!/usr/bin/env python3
# Telegram Download Daemon
# Author: Alfonso E.M. <alfonso@el-magnifico.org>
# You need to install telethon (and cryptg to speed up downloads)

from os import getenv, rename
import subprocess
import math

from sessionManager import getSession, saveSession

from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, DocumentAttributeFilename, DocumentAttributeVideo
import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s]%(name)s:%(message)s',
                    level=logging.WARNING)

import multiprocessing
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
worker_count = multiprocessing.cpu_count()

# Edit these lines:
proxy = None


# End of interesting parameters
async def sendHelloMessage(client, peerChannel):
    entity = await client.get_entity(peerChannel)
    print("Hi! Ready for your files!")
    await client.send_message(entity, "Hi! Ready for your files!")
    

async def log_reply(event : events.ChatAction.Event, reply):
    print(reply)
    await event.reply(reply)

def getFilename(event: events.NewMessage.Event):
    for attribute in event.media.document.attributes:
        if isinstance(attribute, DocumentAttributeFilename): return attribute.file_name
        if isinstance(attribute, DocumentAttributeVideo): 
            try: return event.message.document.attributes[1].file_name #sometimes there is the filename
            except: return "DocumentAttributeVideo"
       


in_progress={}

def set_progress(filename, received, total):
    if received >= total:
        try: in_progress.pop(filename)
        except: pass
        return
    percentage = math.trunc(received / total * 10000) / 100

    in_progress[filename] = f"{percentage} % ({received} / {total})"

with TelegramClient(getSession(), api_id, api_hash,
                    proxy=proxy).start() as client:

    saveSession(client.session)

    queue = asyncio.Queue()
    que_fname = asyncio.Queue()
    peerChannel = PeerChannel(channel_id)
    config_rename = False

    @client.on(events.NewMessage())
    async def handler(event):

        if event.to_id != peerChannel:
            return

        print(event)
        global config_rename
        if not event.media and event.message:
            command = event.message.message
            command = command.lower()
            command = command.split(' ',1) #splitting for future command params


            if command[0] == "/start":
                que_fname.put_nowait(command[1])
                

            if command[0] == "/list":
                output = subprocess.run(["ls", "-l", downloadFolder], capture_output=True).stdout
                output = output.decode('utf-8')
                await log_reply(event, output)

            if command[0] == "/status":
                try:
                    output = "".join([ f"{key}: {value}\n" for (key, value) in in_progress.items()])
                    if output: output = "Active downloads:\n\n" + output
                    else: output = "No active downloads"
                except:
                    output = "Some error occured while checking the status. Retry."
                await log_reply(event, output)
            
            if command[0] == "/config":
                output = "Wrong prarameter:\n type \'/config help\' "
                if len(command) > 1:
                    params = command[1].split(' ')
                    if(params[0] == "help"):
                        output = "HELP\n type /help rename [ON/OFF]"
                    if len(params)>1:
                        if(params[0] == "rename"):
                            if params[1] == "on":
                                config_rename = True
                                output = "Manual renaming files : ON"
                            if params[1] == "off":    
                                config_rename = False
                                output = "Manual renaming files : OFF"
                        else:
                            output = "Wrong prarameter:\n type \'/config help\' "
                else:
                    output = "Wrong prarameter:\n type \'/config help\' "
                #output = "Wrong prarameter:\n type \'/config help\' "
                await log_reply(event, output)

        if event.media:
            entity = await client.get_entity(peerChannel)
            videoname = getFilename(event)
            if config_rename == True | (videoname == 'DocumentAttributeVideo'):
                await client.send_message(entity, "Enter /start [Filename] to start your download")
            else:
                que_fname.put_nowait(videoname)
            queue.put_nowait(event)


    

    async def worker():
        while True:
            event = await queue.get()
            filename=await que_fname.get() # waiting for the filename
            que_fname.task_done()

            await log_reply(
                event,
                f"Downloading file {filename} ({event.media.document.size} bytes)"
            )

            download_callback = lambda received, total: set_progress(filename, received, total)

            await client.download_media(event.message, f"{downloadFolder}/{filename}.partial", progress_callback = download_callback)
            set_progress(filename, 1, 1)
            rename(f"{downloadFolder}/{filename}.partial", f"{downloadFolder}/{filename}")
            await log_reply(event, f"{filename} ready")

            queue.task_done()

    async def start():
        tasks = []
        loop = asyncio.get_event_loop()
        for i in range(worker_count):
            task = loop.create_task(worker())
            tasks.append(task)
        await sendHelloMessage(client, peerChannel)
        await client.run_until_disconnected()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    client.loop.run_until_complete(start())
