from manager.manager import Manager


class DiscoveryManager(Manager):
    """
    Subclass of Manager. Handles all discovery messages connected to a node.
    """
    def handle_message(self, message):
        pass

    def send_message(self, address):
        pass