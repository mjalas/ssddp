

class DescriptionMessageHandler(object):
    """
        Subclass of Manager.
        Handles the creation and parsing of description messages.
    """
    def __init__(self, node_name):
        self.node_name = node_name
        self.sent_descriptions = []

    def parse_message(self, message):
        pass

    def create_message(self, node):
        pass
