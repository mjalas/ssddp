from enum import Enum


class MessageType(Enum):
    discovery_request = 1
    discovery_response = 2
    description_request = 3
    description_response = 4
