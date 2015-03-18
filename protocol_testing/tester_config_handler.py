from protocol_testing.config_test_file import TestConfiguration
from protocol_testing.config_test_file import ConfigurationNode


class TesterConfigHandler(object):
    """
    Class for handling config files used for testing the protocol nodes.
    """

    def __init__(self, file):
        configuration = TestConfiguration.read_config_from_file(file)
        if configuration is None:
            raise FileNotFoundError
        self.test_configuration = configuration

    def get_node_names(self):
        if self.test_configuration:
            nodes = self.test_configuration.nodes
            return ConfigurationNode.get_names_from_node_list(nodes)
        return None