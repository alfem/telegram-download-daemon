#!/usr/bin/env python3
# Telegram Download Daemon
# Author: Alfonso E.M. <alfonso@el-magnifico.org>
# You need to install telethon (and cryptg to speed up downloads)

import argparse
import asyncio
import logging
import math
import multiprocessing
import os.path
import subprocess
import time
from os import getenv, path
from shutil import move

from telethon import TelegramClient, events, __version__
from telethon.tl.types import PeerChannel

from config.daemon_config import DaemonConfig
from daemon.telegram_daemon import Daemon
from sessionManager import getSession, saveSession
from strategies.base import BaseChannelManager
from strategies.channel_strategy_factory import ChannelStrategyFactory
from utils.event_utils import EventUtils

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s]%(name)s:%(message)s',
                    level=logging.WARNING)

TDD_VERSION = "1.13"

TELEGRAM_DAEMON_API_ID = getenv("TELEGRAM_DAEMON_API_ID")
TELEGRAM_DAEMON_API_HASH = getenv("TELEGRAM_DAEMON_API_HASH")
TELEGRAM_DAEMON_CHANNEL = getenv("TELEGRAM_DAEMON_CHANNEL")

TELEGRAM_DAEMON_SESSION_PATH = getenv("TELEGRAM_DAEMON_SESSION_PATH")

TELEGRAM_DAEMON_DEST = getenv("TELEGRAM_DAEMON_DEST", "/telegram-downloads")
TELEGRAM_DAEMON_TEMP = getenv("TELEGRAM_DAEMON_TEMP", "")
TELEGRAM_DAEMON_DUPLICATES = getenv("TELEGRAM_DAEMON_DUPLICATES", "rename")

TELEGRAM_DAEMON_TEMP_SUFFIX = "tdd"

parser = argparse.ArgumentParser(
    description="Script to download files from a Telegram Channel.")
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
parser.add_argument(
    "--duplicates",
    choices=["ignore", "rename", "overwrite"],
    type=str,
    default=TELEGRAM_DAEMON_DUPLICATES,
    help=
    '"ignore"=do not download duplicated files, "rename"=add a random suffix, "overwrite"=redownload and overwrite.'
)
args = parser.parse_args()

api_id = args.api_id
api_hash = args.api_hash
channel_id = args.channel
downloadFolder = args.dest
tempFolder = args.temp
duplicates = args.duplicates
worker_count = multiprocessing.cpu_count()
updateFrequency = 10
lastUpdate = 0
# multiprocessing.Value('f', 0)

if not tempFolder:
    tempFolder = downloadFolder

# Edit these lines:
proxy = None

utils: EventUtils = EventUtils()
daemon_config: DaemonConfig = DaemonConfig()
daemon_config.set_api_id(api_id)
daemon_config.set_api_hash(api_hash)
daemon_config.set_channel(channel_id)
daemon_config.set_dest(downloadFolder)
daemon_config.set_temp(tempFolder)
daemon_config.set_duplicates(duplicates)
daemon_config.set_update_frequency(updateFrequency)
daemon_config.set_last_update(lastUpdate)

channel_manager_factory: ChannelStrategyFactory = ChannelStrategyFactory(daemon_config)
#manager: BaseChannelManager = BaseChannelManager(daemon_config)



# End of interesting parameters

#async def send_hello_message(t_client: TelegramClient, peer_channel: PeerChannel):
#    entity = await t_client.get_entity(peer_channel)
#    print("Telegram Download Daemon " + TDD_VERSION + " using Telethon " + __version__)
#    await t_client.send_message(entity, "Telegram Download Daemon " + TDD_VERSION + " using Telethon " + __version__)
#    await t_client.send_message(entity, "Hi! Ready for your files!")


#in_progress = {}

#with TelegramClient(getSession(), api_id, api_hash,
#                    proxy=proxy).start() as client:
#    saveSession(client.session)

#   queue = asyncio.Queue()
#    peerChannel = PeerChannel(channel_id)
#    last_forwarded_channel_id: int = 0

#    @client.on(events.NewMessage())
#    async def handler(event):

#        if event.to_id != peerChannel:
#            return

#        print(event)
#        if event.message.fwd_from is not None:
#            last_forwarded_channel_id = event.message.fwd_from.from_id.channel_id
#            print(f"last_forwarded_channel_id has been set to : {last_forwarded_channel_id}")

        # print(f"Identificador del canal desde el que se hace fwd: {event.message.fwd_from.from_id.channel_id}")
#       try:
#            if not event.media and event.message:
#                command = event.message.message
#                command = command.lower()
#                output = "Unknown command"

#               if command == "list":
#                    output = subprocess.run(["ls -l " + downloadFolder], shell=True, stdout=subprocess.PIPE,
#                                            stderr=subprocess.STDOUT).stdout.decode('utf-8')
#                elif command == "status":
#                    try:
#                        output = "".join(["{0}: {1}\n".format(key, value) for (key, value) in in_progress.items()])
#                        if output:
#                            output = "Active downloads:\n\n" + output
#                        else:
#                            output = "No active downloads"
#                    except:
#                        output = "Some error occured while checking the status. Retry."
#                elif command == "clean":
#                    output = "Cleaning " + tempFolder + "\n"
#                    output += subprocess.run(["rm " + tempFolder + "/*." + TELEGRAM_DAEMON_TEMP_SUFFIX], shell=True,
#                                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
#                else:
#                    output = "Available commands: list, status, clean"
#
#                await utils.log_reply(event, output)

#            if event.media:
#                if hasattr(event.media, 'document') or hasattr(event.media, 'photo'):
#                    filename = utils.get_file_name(event)
#                    if (path.exists(
#                            "{0}/{1}.{2}".format(tempFolder, filename, TELEGRAM_DAEMON_TEMP_SUFFIX)) or path.exists(
#                        "{0}/{1}".format(downloadFolder, filename))) and duplicates == "ignore":
#                        message = await event.reply("{0} already exists. Ignoring it.".format(filename))
#                    else:
#                        message = await event.reply("{0} added to queue".format(filename))
#                        await queue.put([event, message])
#                else:
#                    message = await event.reply("That is not downloadable. Try to send it as a file.")
#
#        except Exception as e:
#            print('Events handler error: ', e)


#   async def worker():
#        manager: BaseChannelManager = BaseChannelManager(daemon_config)
#        while True:
#            print("Entro en el while true")
#            element = await queue.get()
#            try:
#                #manager: BaseChannelManager = BaseChannelManager(client, daemon_config)
#                print(f"Worker code prior to factory call:")
#                print(f"Message: {element[0].message}")
#                if element[0].message.fwd_from is not None:
#                    print(f"FWD FROM content: {element[0].message.fwd_from}")
#                    print(f"FROM_ID FROM content: {element[0].message.fwd_from.from_id}")
#                    print(f"Channel id on the message: {element[0].message.fwd_from.from_id.channel_id}")
#                    last_forwarded_channel_id = element[0].message.fwd_from.from_id.channel_id

#                manager = channel_manager_factory.get_channel_manager(last_forwarded_channel_id)

#                if manager is not None:
#                    await manager.manage_new_message_event(client, queue, element, in_progress)
#                    queue.task_done()
#                else:
#                    print("ERROR: manager is None, can not handle the logic properly.")
#            except Exception as e:
#                logging.exception("message")
#                try:
#                    await utils.log_reply(element[0],
#                                          "Error: {}".format(str(e)))  # If it failed, inform the user about it.
#                except:
#                    pass
#                print('Queue worker error: ', e)


#   async def start():
#        tasks = []
#        loop = asyncio.get_event_loop()
#        for i in range(worker_count):
#            task = loop.create_task(worker())
#            tasks.append(task)
#        await send_hello_message(client, peerChannel)
#        await client.run_until_disconnected()
#        for task in tasks:
#            task.cancel()
#        await asyncio.gather(*tasks, return_exceptions=True)


#    client.loop.run_until_complete(start())

telegram_daemon: Daemon = Daemon(daemon_config)
telegram_daemon.run()

