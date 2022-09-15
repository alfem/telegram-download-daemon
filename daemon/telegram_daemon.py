import asyncio
import logging
import multiprocessing
import string
import subprocess
from abc import ABC
from os import path
from typing import List

from telethon import TelegramClient, __version__, events
from telethon.tl.types import PeerChannel

import utils
from config.daemon_config import DaemonConfig
from daemon.FolderInformationNotFoundException import FolderInformationNotFoundException
from sessionManager import getSession, saveSession
from strategies.base import BaseChannelManager
from strategies.channel_strategy_factory import ChannelStrategyFactory
from utils.event_utils import EventUtils
from models.folder_container import FolderContainer


class Daemon(ABC):
    daemon_config: DaemonConfig = DaemonConfig()
    in_progress = {}
    queue = asyncio.Queue()
    folder_list: list[FolderContainer] = []
    version: string = "1.13"
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

    @events.register(events.NewMessage())
    async def handler(self, event):
        folder_container: FolderContainer = None
        if event.to_id != self.peerChannel:
            return

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
                    if event.message.fwd_from is not None:
                        manager: BaseChannelManager = self.channel_manager_factory.get_channel_manager(
                            event.message.fwd_from.from_id.channel_id)
                        temporal_folder_name = manager.extract_folder_name(event.message.message)
                        folder_container = FolderContainer(event.message.id,
                                                           event.message.fwd_from.from_id.channel_id,
                                                           temporal_folder_name)
                        self.folder_list.append(folder_container)

                    if (path.exists(
                            "{0}/{1}.{2}".format(self.daemon_config.temp, filename,
                                                 self.daemon_config.temp_suffix)) or path.exists(
                        "{0}/{1}".format(self.daemon_config.dest,
                                         filename))) and self.daemon_config.duplicates == "ignore":
                        message = await event.reply("{0} already exists. Ignoring it.".format(filename))
                    else:
                        message = await event.reply("{0} added to queue".format(filename))

                        if folder_container is None:
                            folder_container = self.get_right_folder_info(event.message.id)

                        print(
                            f"METO EN LA COLA: evento: {event} mensaje: {message} folder_container: {folder_container}")

                        await self.queue.put([event, message, folder_container])
                else:
                    message = await event.reply("That is not downloadable. Try to send it as a file.")

        except Exception as e:
            logging.exception("message")
            print('Events handler error: ', e)

    def get_right_folder_info(self, message_id: int) -> FolderContainer:
        """ Gets closest message id to the one provided from the list, which contains right folder information to
        use. """
        target_folder_container: FolderContainer = None
        for info in reversed(self.folder_list):
            if info.message_id < message_id:
                target_folder_container = info
                break
        if target_folder_container is None:
            raise FolderInformationNotFoundException()

        return target_folder_container

    async def worker(self):
        manager: BaseChannelManager = BaseChannelManager(self.daemon_config)
        while True:
            print("Entro en el while true")
            # If the queue has no messages left to be processed then clear the list to avoid huge memory consumption.
            if self.queue.empty():
                self.folder_list.clear()
                
            element = await self.queue.get()
            folder_info: FolderContainer = element[2]
            try:
                manager = self.channel_manager_factory.get_channel_manager(folder_info.origin_channel_id)

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
        self.init()
        self.client.add_event_handler(self.handler)
        self.client.loop.run_until_complete(self.start())
