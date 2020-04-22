# telegram-download-daemon

A Telegram Daemon (not a bot) for file downloading automation 

If you have got an Internet connected computer or NAS and you want to automate file downloading from Telegram channels, this
daemon is for you. 

Telegram bots are limited to 20Mb file size downloads. So I wrote this agent
or daemon to allow bigger downloads.

# Installation

You need Python3 (tested in 3.5).

Install Telethon module (using pip or your OS package system):
	pip install --user telethon

Install cryptg to use a C library to speed up downloads (optional)
	pip install --user cryptg

Obtain your own api id: https://core.telegram.org/api/obtaining_api_id

Edit telegram-download-daemon.py and put your own api_id and api_hash values
into the proper variables.

Change the destination folder if desired.

Use your favorite Telegram app to create a new (private)channel. 

Change the channel_id in telegram-download-daemon.py.

Run the script!








