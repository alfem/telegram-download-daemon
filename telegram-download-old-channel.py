#!/usr/bin/env python3

import os
import shutil
import subprocess
import math
import time
import random, string
import time

from sessionManager import getSession, saveSession

from telethon import TelegramClient, events, sync
from telethon.tl.types import PeerChannel, DocumentAttributeFilename, DocumentAttributeVideo
from telethon.errors import FloodWaitError
import decorator, traceback
from functools import wraps

import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s]%(name)s:%(message)s',
                    level=logging.WARNING)

import multiprocessing
import argparse
import asyncio


def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "func: '{}' > exc: {}, Retrying in {} seconds...".format(str(f.__name__), str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry



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

@retry(FloodWaitError, tries=3, delay=1000)
def download_media_avoid_lock(client, message, file_dest):
    try:
        client.download_media(message, file_dest)
    except FloodWaitError as e:
        print('Flood waited for ', e.seconds)
        raise ValueError("See traceback: \n\n{}".format(''.join(traceback.format_stack())))
    except Exception as exc:
        # raise ValueError("See traceback: \n\n{}".format(''.join(traceback.format_stack())))
        pass
    else:
        pass

with TelegramClient(getSession(), api_id, api_hash,
                    proxy=proxy).start() as client:

    saveSession(client.session)
    client.flood_sleep_threshold = 10  # auto-sleep 10 sec
    queue = asyncio.Queue()
    peerChannel = PeerChannel(channel_id)
    client.start()
    trigger = False
    for message in client.iter_messages(peerChannel):
        # global downloadFolder
        try:
            if message.media:
                # filename=getFilename(event)
                filename_attr = next(filter(lambda x: isinstance(x, DocumentAttributeFilename),
                                        message.media.document.attributes), None)
                filename = filename_attr.file_name if filename_attr else ''
                try:
                    # message=element[1]

                    # filename=getFilename(event)
                    filename_attr = next(filter(lambda x: isinstance(x, DocumentAttributeFilename),
                                        message.media.document.attributes), None)
                    filename = filename_attr.file_name if filename_attr else ''
                    if not filename:
                        print(f"id: {message.sender_id},\n {message}")
                        continue
                    # await log_reply(
                    #     message,
                    #     "Downloading file {0} ({1} bytes)".format(filename, message.media.document.size)
                    # )
                    # print(f"try to download id: {message.id}, {filename}\n")
                    # if message.id == 2055:
                    #     trigger = True
                    # if not trigger:
                    #     print("skip...")
                    #     continue
                    print(f"downloading id: {message.id}, {filename}...\n")

                    # download_callback = lambda received, total: set_progress(filename, message, received, total)
                    move_from = os.path.join(tempFolder, "{}.{}".format(filename,TELEGRAM_DAEMON_TEMP_SUFFIX))
                    os.chdir(tempFolder)
                    # client.download_media(message, move_from)
                    
                    # await client.download_media(event.message, "{0}/{1}.{2}".format(tempFolder,filename,TELEGRAM_DAEMON_TEMP_SUFFIX), progress_callback = download_callback)
                    _downloadFolder = downloadFolder
                    if message.message:
                        try:
                            _dir = os.path.splitext(filename)[0]
                        except:
                            _dir = filename
                        if not os.path.exists(os.path.join(downloadFolder, _dir)):
                            _downloadFolder = os.path.join(downloadFolder, _dir)
                            os.makedirs(_downloadFolder)
                        else:
                            _dir += ''.join(random.choice(string.ascii_letters) for x in range(6))
                            _downloadFolder = os.path.join(downloadFolder, _dir)
                            os.makedirs(_downloadFolder)
                        with open(os.path.join(_downloadFolder, "message.txt"), "w") as f:
                            f.write(f'{message.message}\n')
                    if not os.path.exists(os.path.join(_downloadFolder, filename)):
                        download_media_avoid_lock(client, message, move_from)
                    else:
                        print(f"skip... '{filename}' from msg: {message.id}")
                        continue
                    try:
                        if os.path.exists(move_from):
                            if os.path.exists(os.path.join(_downloadFolder, filename)):
                                _filename = ''.join(random.choice(string.ascii_letters) for x in range(6)) + filename
                                move_to = os.path.join(_downloadFolder, _filename)
                            else:
                                move_to = os.path.join(_downloadFolder, filename)
                                shutil.move(move_from, move_to)
                        else:
                            print(f"error: tmpfile '{move_from}' for '{filename}' doesn't exist!")
                    except Exception as exc:
                        print('shutil error: ', exc)
                except Exception as e:
                    print('Queue worker error: ', e)
                # time.sleep(10)
        except Exception as e:
            print('Queue worker error: ', e)


    # client.loop.run_until_complete(start())
