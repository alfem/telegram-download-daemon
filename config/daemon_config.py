from abc import ABC
from os import getenv
from pathlib import Path

from pydantic import BaseModel


class DaemonConfig(BaseModel):
    telegram_daemon_api_id: int = getenv("TELEGRAM_DAEMON_API_ID")
    telegram_daemon_api_hash: str = getenv("TELEGRAM_DAEMON_API_HASH")
    telegram_daemon_channel: int = getenv("TELEGRAM_DAEMON_CHANNEL")
    telegram_daemon_session_path: Path = getenv("TELEGRAM_DAEMON_SESSION_PATH")
    telegram_daemon_dest: str = getenv("TELEGRAM_DAEMON_DEST", "/telegram-downloads")
    telegram_daemon_temp: str = getenv("TELEGRAM_DAEMON_TEMP", "")
    telegram_daemon_duplicates: str = getenv("TELEGRAM_DAEMON_DUPLICATES", "rename")
    telegram_daemon_temp_suffix: str = "tdd"
    telegram_daemon_update_frequency: int = 10
    telegram_daemon_last_update: float = 0

    @property
    def api_id(self) -> int:
        return self.telegram_daemon_api_id

    def set_api_id(self, value: int):
        self.telegram_daemon_api_id = value

    @property
    def api_hash(self) -> str:
        return self.telegram_daemon_api_hash

    def set_api_hash(self, value: str):
        self.telegram_daemon_api_hash = value

    @property
    def channel(self) -> int:
        return self.telegram_daemon_channel

    def set_channel(self, value: int):
        self.telegram_daemon_channel = value

    @property
    def session_path(self) -> Path:
        return self.telegram_daemon_session_path

    def set_session_path(self, value: Path):
        self.telegram_daemon_session_path = value

    @property
    def dest(self) -> str:
        return self.telegram_daemon_dest

    def set_dest(self, value: str):
        self.telegram_daemon_dest = value

    @property
    def temp(self) -> str:
        value_to_return: str
        if not self.telegram_daemon_temp:
            value_to_return = self.telegram_daemon_dest
        else:
            value_to_return = self.telegram_daemon_temp
        return value_to_return

    def set_temp(self, value: str):
        self.telegram_daemon_temp = value

    @property
    def duplicates(self) -> str:
        return self.telegram_daemon_duplicates

    def set_duplicates(self, value: str):
        self.telegram_daemon_duplicates = value

    @property
    def temp_suffix(self) -> str:
        return self.telegram_daemon_temp_suffix

    def set_temp_suffix(self, value: str):
        self.telegram_daemon_temp_suffix = value

    @property
    def update_frequency(self) -> int:
        return self.telegram_daemon_update_frequency

    def set_update_frequency(self, value: int):
        self.telegram_daemon_update_frequency = value

    @property
    def last_update(self) -> float:
        return self.telegram_daemon_last_update

    def set_last_update(self, value: float):
        self.telegram_daemon_last_update = value
