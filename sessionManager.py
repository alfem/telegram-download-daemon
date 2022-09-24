import string
from abc import ABC
from os import path
from pathlib import Path

from telethon.sessions import StringSession

from config.daemon_config import DaemonConfig


class TelegramSessionManager(ABC):

    def __init__(self, daemon_config: DaemonConfig):
        self.daemon_config = daemon_config
        self.sessionName = "DownloadDaemon"
        self.string_session_filename = "{0}.session".format(self.sessionName)

    def _get_string_session_if_exists(self):
        session_file_path = path.join(self.daemon_config.session_path,
                                      self.string_session_filename)
        if path.isfile(session_file_path):
            with open(session_file_path, mode='r') as file:
                session = file.read()
                print("Session loaded from {0}".format(session_file_path))
                return session
        return None

    def get_session(self):
        session_file_path: path = path.join(self.daemon_config.session_path,
                                            self.string_session_filename)
        if not path.exists(session_file_path) or not path.isfile(session_file_path):
            return path.join(self.daemon_config.session_path, self.sessionName)
        else:
            return StringSession(self._get_string_session_if_exists())

    def save_session(self, session):
        if self.daemon_config.session_path is not None:
            session_file_path = path.join(self.daemon_config.session_path,
                                          self.string_session_filename)
            with open(session_file_path, mode='w') as file:
                file.write(StringSession.save(session))
            print("Session saved in {0}".format(session_file_path))
