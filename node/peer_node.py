from node.node_address import Address
from service.service_list import ServiceList
from message.message import Message


class PeerNode(object):
    """

    """
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
        node = PeerNode(message.node_name, message.address, message.timestamp, message.services)
        return node