from message.message import Message
from node.node import Node
from service.service_list import ServiceList


class PeerNode(object):
    """

    """
    message_type_error_string = "Message not of type Message."

    def __init__(self, node, timestamp,):
        self.node = node
        self.timestamp = timestamp

    @staticmethod
    def create_node_from_message(message):
        if not isinstance(message, Message):
            raise ValueError(PeerNode.message_type_error_string)
        node = Node(message.node_name, message.address, None, message.services)
        peer_node = PeerNode(node, message.timestamp)
        return peer_node

    def update_node(self, message):
        if not isinstance(message, Message):
            raise ValueError(PeerNode.message_type_error_string)
        if self.node.name is not message.node_name:
            self.node.name = message.node_name
        if self.node.address is not message.address:
            self.node.address = message.address
        if self.timestamp < message.timestamp:
            self.timestamp = message.timestamp
        if self.node.service_list is not message.services:
            self.node.service_list = ServiceList()
            self.node.service_list.from_dict(message.services)