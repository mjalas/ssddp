from manager.manager import Manager

from message.message import Message, Address, ServiceList


class DescriptionManager(Manager):
    """
    Subclass of Manager. Handles all description messages connected to a node.
    """
    def __init__(self, node_name):
        self.node_name = node_name;
        self.sent_descriptions = []

    def parse_message(self, message):
        pass

    def create_message(self, address):
        pass
