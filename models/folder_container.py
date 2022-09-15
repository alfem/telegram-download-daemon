import string
from abc import ABC

class FolderContainer(ABC):
    container_message_id: int
    container_origin_channel_id: int
    container_folder_name: string

    def __init__(self, message_id: int, origin_channel_id: int, folder_name: string):
        self.container_message_id = message_id
        self.container_origin_channel_id = origin_channel_id
        self.container_folder_name = folder_name

    @property
    def message_id(self) -> int:
        return self.container_message_id

    def set_message_id(self, value: int):
        self.container_message_id = value

    @property
    def origin_channel_id(self) -> int:
        return self.container_origin_channel_id

    def set_origin_channel_id(self, value: int):
        self.container_origin_channel_id = value

    @property
    def folder_name(self) -> string:
        return self.container_folder_name

    def set_folder_name(self, value: string):
        self.container_folder_name = value
