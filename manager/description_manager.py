from manager.manager import Manager

from message.message import Message, Address, ServiceList


class DescriptionManager(Manager):
    """
    Subclass of Manager. Handles all description messages connected to a node.
    """
    def __init__(self, node_name):
        self.node_name = node_name;
        self.sent_descriptions = []

    def handle_message(self, message):
        if isinstance(message, Message):
            pass

    def send_message(self, address):
        if isinstance(address, Address):
            message = Message(self.node_name)
