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
| `TELEGRAM_DAEMON_API_ID`   | `--api-id`              | api_id from https://core.telegram.org/api/obtaining_api_id   |                     |
| `TELEGRAM_DAEMON_API_HASH` | `--api-hash`            | api_hash from https://core.telegram.org/api/obtaining_api_id |                     |
| `TELEGRAM_DAEMON_DEST`     | `--dest`                | Destination path for downloading files                       | `/telegram-downloads` |
| `TELEGRAM_DAEMON_CHANNEL`  | `--channel`             | Channel id to download from it                               |                     |

You can define them as Environment Variables, or put them as a command line arguments, for example:

    python telegram-download-daemon.py --api-id <your-id> --api-hash <your-hash> --channel <channel-number>


Finally, resend any file link to the channel to start the downloading. This daemon can manage many downloads simultaneously.

You can also 'talk' to this daemon using your Telegram client:

* Say "/list" and get a list of available files in the destination path.
* Say "/status" to the daemon yo check the current status.
* Say "/config help" to see config parameters.



# Docker

`docker pull alfem/telegram-download-daemon`

When we use the [`TelegramClient`](https://docs.telethon.dev/en/latest/quick-references/client-reference.html#telegramclient) method, it requires us to interact with the `Console` to give it our phone number and confirm with a security code.

To do this, when using *Docker*, you need to **interactively** run the container for the first time.

When you use `docker-compose`, the `.session` file, where the login is stored is kept in *Volume* outside the container. Therefore, when using docker-compose you are required to:

```bash
$ docker-compose run --rm telegram-download-daemon
# Interact with the console to authenticate yourself.
# See the message "Signed in successfully as {youe name}"
# Close the container
$ docker-compose up -d
```

See the `sessions` volume in the [docker-compose.yml](docker-compose.yml) file.
