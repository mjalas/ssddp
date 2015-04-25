from protocol_testing.config_test_file import TestConfiguration
from protocol_testing.config_test_file import ConfigurationNode


class ArgumentError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TesterConfigHandler(object):
    """
    Class for handling config files used for testing the protocol nodes.
    """

    def __init__(self, file=None, data=None, use_config_nodes=False):
        if not file and not data:
            raise ArgumentError("Either file or data need to be present")
        if use_config_nodes:
            if file:
                self.config_nodes = TestConfiguration.read_config_from_file_v2(file)
            if self.config_nodes is None:
                raise FileNotFoundError
            elif data:
                self.config_nodes = TestConfiguration.read_config_from_data_v2(data)
            self.test_configuration = None
        else:
            if file:
                self.test_configuration = TestConfiguration.read_config_from_file(file)
                if self.test_configuration is None:
                    raise FileNotFoundError
            elif data:
                self.test_configuration = TestConfiguration.read_config_from_data(data)
            self.config_nodes = None

    def get_node_names(self):
        if self.test_configuration:
            nodes = self.test_configuration.nodes
            return ConfigurationNode.get_names_from_node_list(nodes)
        return None

    def get_services_for_nodes(self):
        if self.test_configuration:
            nodes = self.test_configuration.nodes
            services = {}
            for node in nodes:
                if node.services:
                    services[node.name] = node.services
            return services
        return None

