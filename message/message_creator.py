from message.timestamp import Timestamp
from message.message import Message
from message.message_types import MessageType


class MessageCreator(object):
    """
    Convenience class for different message creation.
    """

    def __init__(self):
        pass

    @staticmethod
    def create_description_request(node_name, address):
        return Message(message_type=MessageType.description_request, node_name=node_name, address=address,
                       timestamp=Timestamp.create_timestamp())

    @staticmethod
    def create_description_response(node_name, address, services):
        return Message(message_type=MessageType.description_response, node_name=node_name, address=address,
                       timestamp=Timestamp.create_timestamp(), services=services)
