import asyncio
import logging
import multiprocessing
import string
import subprocess
from abc import ABC
from os import path

from telethon import TelegramClient, __version__, events
from telethon.tl.types import PeerChannel

import utils
from config.daemon_config import DaemonConfig
from sessionManager import getSession, saveSession
from strategies.base import BaseChannelManager
from strategies.channel_strategy_factory import ChannelStrategyFactory
from utils.event_utils import EventUtils


class Daemon(ABC):
    daemon_config: DaemonConfig = DaemonConfig()
    in_progress = {}
    queue = asyncio.Queue()
    version: string = "1.13"
    last_forwarded_channel_id: int = 0
    utils: EventUtils = EventUtils()

    def __init__(self, config: DaemonConfig):
        self.daemon_config = config
        self.peerChannel = PeerChannel(self.daemon_config.channel)
        self.client = TelegramClient(getSession(), self.daemon_config.api_id, self.daemon_config.api_hash,
                                proxy=None).start()
        self.channel_manager_factory: ChannelStrategyFactory = ChannelStrategyFactory(self.daemon_config)
        self.worker_count = multiprocessing.cpu_count()

    async def send_hello_message(self, t_client: TelegramClient, peer_channel: PeerChannel):
        entity = await t_client.get_entity(peer_channel)
        print("Telegram Download Daemon " + self.version + " using Telethon " + __version__)
        await t_client.send_message(entity,
                                    "Telegram Download Daemon " + self.version + " using Telethon " + __version__)
        await t_client.send_message(entity, "Hi! Ready for your files!")

    def init(self):
        saveSession(self.client.session)

    #@client.on(events.NewMessage())
    @events.register(events.NewMessage())
    async def handler(self, event):

        if event.to_id != self.peerChannel:
            return

        print(event)
        if event.message.fwd_from is not None:
            last_forwarded_channel_id = event.message.fwd_from.from_id.channel_id
            print(f"last_forwarded_channel_id has been set to : {last_forwarded_channel_id}")

        # print(f"Identificador del canal desde el que se hace fwd: {event.message.fwd_from.from_id.channel_id}")
        try:
            if not event.media and event.message:
                command = event.message.message
                command = command.lower()
                output = "Unknown command"

                if command == "list":
                    output = subprocess.run(["ls -l " + self.daemon_config.dest], shell=True, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT).stdout.decode('utf-8')
                elif command == "status":
                    try:
                        output = "".join(["{0}: {1}\n".format(key, value) for (key, value) in self.in_progress.items()])
                        if output:
                            output = "Active downloads:\n\n" + output
                        else:
                            output = "No active downloads"
                    except:
                        output = "Some error occured while checking the status. Retry."
                elif command == "clean":
                    output = "Cleaning " + self.daemon_config.temp + "\n"
                    output += subprocess.run(["rm " + self.daemon_config.temp + "/*." + self.daemon_config.temp_suffix],
                                             shell=True,
                                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
                else:
                    output = "Available commands: list, status, clean"

                await self.utils.log_reply(event, output)

            if event.media:
                if hasattr(event.media, 'document') or hasattr(event.media, 'photo'):
                    filename = self.utils.get_file_name(event)
                    if (path.exists(
                            "{0}/{1}.{2}".format(self.daemon_config.temp, filename,
                                                 self.daemon_config.temp_suffix)) or path.exists(
                        "{0}/{1}".format(self.daemon_config.dest,
                                         filename))) and self.daemon_config.duplicates == "ignore":
                        message = await event.reply("{0} already exists. Ignoring it.".format(filename))
                    else:
                        message = await event.reply("{0} added to queue".format(filename))
                        await self.queue.put([event, message])
                else:
                    message = await event.reply("That is not downloadable. Try to send it as a file.")

        except Exception as e:
            print('Events handler error: ', e)

    async def worker(self):
        manager: BaseChannelManager = BaseChannelManager(self.daemon_config)
        while True:
            print("Entro en el while true")
            element = await self.queue.get()
            try:
                # manager: BaseChannelManager = BaseChannelManager(client, daemon_config)
                print(f"Worker code prior to factory call:")
                print(f"Message: {element[0].message}")
                if element[0].message.fwd_from is not None:
                    print(f"FWD FROM content: {element[0].message.fwd_from}")
                    print(f"FROM_ID FROM content: {element[0].message.fwd_from.from_id}")
                    print(f"Channel id on the message: {element[0].message.fwd_from.from_id.channel_id}")
                    self.last_forwarded_channel_id = element[0].message.fwd_from.from_id.channel_id

                manager = self.channel_manager_factory.get_channel_manager(self.last_forwarded_channel_id)

                if manager is not None:
                    await manager.manage_new_message_event(self.client, self.queue, element, self.in_progress)
                    self.queue.task_done()
                else:
                    print("ERROR: manager is None, can not handle the logic properly.")
            except Exception as e:
                logging.exception("message")
                try:
                    await self.utils.log_reply(element[0],
                                               "Error: {}".format(
                                                   str(e)))  # If it failed, inform the user about it.
                except:
                    pass
                print('Queue worker error: ', e)

    async def start(self):
        tasks = []
        loop = asyncio.get_event_loop()
        for i in range(self.worker_count):
            task = loop.create_task(self.worker())
            tasks.append(task)
        await self.send_hello_message(self.client, self.peerChannel)
        await self.client.run_until_disconnected()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    def run(self):
        self.client.add_event_handler(self.handler)
        self.client.loop.run_until_complete(self.start())
