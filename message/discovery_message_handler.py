from manager.message_handler import MessageHandler
from message.message import Message
from message.message_types import MessageType
from message.timestamp import Timestamp


class DiscoveryMessageHandler(MessageHandler):
    """
        Subclass of Manager.
        Handles parsing and creating discovery messages connected to a node.
    """
    def parse_message(self, message):
        pass

    def create_message(self, node):

        message_type = MessageType.discovery_response
        timestamp = Timestamp.create_timestamp()

        message = Message(message_type, node.name, node.address, timestamp, node.service_list)

        return message