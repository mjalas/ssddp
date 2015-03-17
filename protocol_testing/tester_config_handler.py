import json


class TesterConfigHandler(object):
    """
    Class for handling config files used for testing the protocol nodes.
    """

    def __init__(self):
        self.node_names = []

    def handle_file(self, file):
        config_file = open(file, "r")
        config_data = config_file.read()
        data = json.load(config_data)
        if 'nodes' in data:
            nodes = data['nodes']
            for node in nodes:
                self.node_names.append(node['name'])

