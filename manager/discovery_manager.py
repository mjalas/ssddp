from manager.manager import Manager


class DiscoveryManager(Manager):
    """
    Subclass of Manager. Handles all discovery messages connected to a node.
    """
    def parse_message(self, message):
        pass

    def create_message(self, address):
        pass