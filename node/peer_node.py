from node.node_address import Address
from service.service_list import ServiceList
from message.message import Message


class PeerNode(object):
    """

    """
    message_type_error_string = "Message not of type Message."

    def __init__(self, name, address, timestamp, services=None):
        self.name = name
        self.address = address
        self.timestamp = timestamp
        if services is None:
            self.service_list = ServiceList()
        else:
            self.service_list = services

    @staticmethod
    def create_node_from_message(message):
        if not isinstance(message, Message):
            raise ValueError(PeerNode.message_type_error_string)
        node = PeerNode(message.node_name, message.address, message.timestamp, message.services)
        return node

    def update_node(self, message):
        if not isinstance(message, Message):
            raise ValueError(PeerNode.message_type_error_string)
        if self.name is not message.node_name:
            self.name = message.node_name
        if self.address is not message.address:
            self.address = message.address
        if self.timestamp < message.timestamp:
            self.timestamp = message.timestamp
        if self.service_list is not message.services:
            self.service_list = message.services