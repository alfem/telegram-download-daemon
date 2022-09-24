#!/usr/bin/env python3
# Telegram Download Daemon
# Author: Alfonso E.M. <alfonso@el-magnifico.org>
# You need to install telethon (and cryptg to speed up downloads)

import argparse
import logging
import multiprocessing
from os import getenv

from config.daemon_config import DaemonConfig
from daemon.telegram_daemon import Daemon

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
    required=TELEGRAM_DAEMON_API_ID is None,
    type=int,
    default=TELEGRAM_DAEMON_API_ID,
    help=
    'api_id from https://core.telegram.org/api/obtaining_api_id (default is TELEGRAM_DAEMON_API_ID env var)'
)
parser.add_argument(
    "--api-hash",
    required=TELEGRAM_DAEMON_API_HASH is None,
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
    required=TELEGRAM_DAEMON_CHANNEL is None,
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
parser.add_argument(
    "--session-path",
    required=TELEGRAM_DAEMON_SESSION_PATH is None,
    type=str,
    default=TELEGRAM_DAEMON_SESSION_PATH,
    help=
    "Path to folder location where telegram session will be create or is already placed (DownloadDaemon.session file)."
)

args = parser.parse_args()

api_id = args.api_id
api_hash = args.api_hash
channel_id = args.channel
downloadFolder = args.dest
tempFolder = args.temp
duplicates = args.duplicates
session_path = args.session_path
worker_count = multiprocessing.cpu_count()
updateFrequency = 10
lastUpdate = 0
# multiprocessing.Value('f', 0)

if not tempFolder:
    tempFolder = downloadFolder

# Edit these lines:
proxy = None

daemon_config: DaemonConfig = DaemonConfig()
daemon_config.set_api_id(api_id)
daemon_config.set_api_hash(api_hash)
daemon_config.set_channel(channel_id)
daemon_config.set_dest(downloadFolder)
daemon_config.set_temp(tempFolder)
daemon_config.set_duplicates(duplicates)
daemon_config.set_update_frequency(updateFrequency)
daemon_config.set_last_update(lastUpdate)
daemon_config.set_session_path(session_path)

telegram_daemon: Daemon = Daemon(daemon_config)
telegram_daemon.run()

