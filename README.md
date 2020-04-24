# telegram-download-daemon

A Telegram Daemon (not a bot) for file downloading automation 

If you have got an Internet connected computer or NAS and you want to automate file downloading from Telegram channels, this
daemon is for you. 

Telegram bots are limited to 20Mb file size downloads. So I wrote this agent
or daemon to allow bigger downloads (limited to 1.5GB by Telegram APIs).

# Installation

You need Python3 (tested in 3.5).

Install dependencies by running this command:

    pip install -r requirements.txt

(If you don't want to install `cryptg` and its dependencies, you just need to install `telethon`)


Obtain your own api id: https://core.telegram.org/api/obtaining_api_id

# Usage

You need to configure these values:

| Environment Variable     | Command Line argument | Description                                                  | Default Value       |
|--------------------------|:-----------------------:|--------------------------------------------------------------|---------------------|
| `TELEGRAM_DEAMON_API_ID`   | `--api-id`              | api_id from https://core.telegram.org/api/obtaining_api_id   |                     |
| `TELEGRAM_DEAMON_API_HASH` | `--api-hash`            | api_hash from https://core.telegram.org/api/obtaining_api_id |                     |
| `TELEGRAM_DEAMON_CHANNEL`  | `--dest`                | Destenation path for downloading files                       | `/telegram-downloads` |
| `TELEGRAM_DEAMON_DEST`     | `--channel`             | Channel id to download from it                               |                     |

You can define the as Environment Variables, or put them as a commend line arguments, for example:

    python telegram-download-deamon.py --api-ip <your-id> --api-hash <your-hash> --channel <channel-number>
