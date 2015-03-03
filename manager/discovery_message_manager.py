from manager.manager import MessageManager


class DiscoveryMessageManager(MessageManager):
    """
        Subclass of Manager.
        Handles parsing and creating discovery messages connected to a node.
    """
    def parse_message(self, message):
        pass

    def create_message(self, address):
        pass