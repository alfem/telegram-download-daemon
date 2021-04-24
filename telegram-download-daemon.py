#!/usr/bin/env python3
# Telegram Download Daemon
# Author: Alfonso E.M. <alfonso@el-magnifico.org>
# You need to install telethon (and cryptg to speed up downloads)

import os
import shutil
import subprocess
import math
import time

from sessionManager import getSession, saveSession

from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, DocumentAttributeFilename, DocumentAttributeVideo
import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s]%(name)s:%(message)s',
                    level=logging.WARNING)

import multiprocessing
import argparse
import asyncio


TDD_VERSION="1.4"

TELEGRAM_DAEMON_API_ID = os.getenv("TELEGRAM_DAEMON_API_ID")
TELEGRAM_DAEMON_API_HASH = os.getenv("TELEGRAM_DAEMON_API_HASH")
TELEGRAM_DAEMON_CHANNEL = os.getenv("TELEGRAM_DAEMON_CHANNEL")

TELEGRAM_DAEMON_SESSION_PATH = os.getenv("TELEGRAM_DAEMON_SESSION_PATH")

TELEGRAM_DAEMON_DEST=os.getenv("TELEGRAM_DAEMON_DEST", "/telegram-downloads")
TELEGRAM_DAEMON_TEMP=os.getenv("TELEGRAM_DAEMON_TEMP", "")

TELEGRAM_DAEMON_TEMP_SUFFIX="tdd"

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
    default=TELEGRAM_DAEMON_DEST,
    help=
    'Destination path for downloaded files (default is /telegram-downloads).')
parser.add_argument(
    "--temp",
    type=str,
    default=TELEGRAM_DAEMON_TEMP,
    help=
    'Destination path for temporary files (default is using the same downloaded files directory).')
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
tempFolder = args.temp
worker_count = multiprocessing.cpu_count()
updateFrequency = 10
lastUpdate = 0
#multiprocessing.Value('f', 0)

if not tempFolder:
    tempFolder = downloadFolder

# Edit these lines:
proxy = None

# End of interesting parameters

async def sendHelloMessage(client, peerChannel):
    entity = await client.get_entity(peerChannel)
    print("Telegram Download Daemon "+TDD_VERSION)
    await client.send_message(entity, "Telegram Download Daemon "+TDD_VERSION)
    await client.send_message(entity, "Hi! Ready for your files!")
 

async def log_reply(message, reply):
    print(reply)
    await message.edit(reply)
 
def getFilename(event: events.NewMessage.Event):
    mediaFileName = "unknown"
    for attribute in event.media.document.attributes:
        if isinstance(attribute, DocumentAttributeFilename): return attribute.file_name
        if isinstance(attribute, DocumentAttributeVideo): mediaFileName = event.original_update.message.message
    return mediaFileName


in_progress={}

async def set_progress(filename, message, received, total):
    global lastUpdate
    global updateFrequency

    if received >= total:
        try: in_progress.pop(filename)
        except: pass
        return
    percentage = math.trunc(received / total * 10000) / 100;

    progress_message= "{0} % ({1} / {2})".format(percentage, received, total)
    in_progress[filename] = progress_message

    currentTime=time.time()
    if (currentTime - lastUpdate) > updateFrequency:
        await log_reply(message, progress_message)
        lastUpdate=currentTime


with TelegramClient(getSession(), api_id, api_hash,
                    proxy=proxy).start() as client:

    saveSession(client.session)

    queue = asyncio.Queue()
    peerChannel = PeerChannel(channel_id)

    @client.on(events.NewMessage())
    async def handler(event):

        if event.to_id != peerChannel:
            return

        print(event)
        
        try:

            if not event.media and event.message:
                command = event.message.message
                command = command.lower()
                output = "Unknown command"

                if command == "list":
                    output = subprocess.run(["ls -l "+downloadFolder], shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.decode('utf-8')
                elif command == "status":
                    try:
                        output = "".join([ "{0}: {1}\n".format(key,value) for (key, value) in in_progress.items()])
                        if output: 
                            output = "Active downloads:\n\n" + output
                        else: 
                            output = "No active downloads"
                    except:
                        output = "Some error occured while checking the status. Retry."
                elif command == "clean":
                    output = "Cleaning "+tempFolder+"\n"
                    output+=subprocess.run(["rm "+tempFolder+"/*."+TELEGRAM_DAEMON_TEMP_SUFFIX], shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout
                else:
                    output = "Available commands: list, status, clean"

                await log_reply(event, output)

            if event.media:
                filename=getFilename(event)
                message=await event.reply("{0} added to queue".format(filename))
                await queue.put([event, message])
        except Exception as e:
                print('Events handler error: ', e)

    async def worker():
        global downloadFolder
        while True:
            try:
                element = await queue.get()
                event=element[0]
                message=element[1]

                filename=getFilename(event)

                await log_reply(
                    message,
                    "Downloading file {0} ({1} bytes)".format(filename,event.media.document.size)
                )

                download_callback = lambda received, total: set_progress(filename, message, received, total)

                await client.download_media(event.message, "{0}/{1}.{2}".format(tempFolder,filename,TELEGRAM_DAEMON_TEMP_SUFFIX), progress_callback = download_callback)
                set_progress(filename, message, 100, 100)
                _downloadFolder = downloadFolder
                if event.message.message:
                    try:
                        _dir = os.path.splitext(filename)[0]
                    except:
                        _dir = filename
                    _downloadFolder = os.path.join(downloadFolder, _dir)
                    if not os.path.exists(_downloadFolder):
                        os.makedirs(_downloadFolder)
                    with open(os.path.join(_downloadFolder, "message.txt"), "w") as f:
                        f.write(f'{event.message.message}\n')
                try:
                    move_from = os.path.join(tempFolder, "{}.{}".format(filename,TELEGRAM_DAEMON_TEMP_SUFFIX))
                    move_to = os.path.join(_downloadFolder, filename)
                    if os.path.exists(move_from):
                        shutil.move(move_from, move_to)
                    else:
                        set_progress(filename, f"error: tmpfile for '{filename}' doesn't exist!", 0, 0)
                except Exception as exc:
                    set_progress(filename, f"shutil error: {str(exc)}", 0, 0)
                    print('shutil error: ', exc)

                await log_reply(message, "{0} ready".format(filename))

                queue.task_done()
            except Exception as e:
                set_progress(filename, f"Queue worker error: {str(e)}", 0, 0)
                print('Queue worker error: ', e)

 
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
