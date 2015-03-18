import json


class TestConfiguration(object):
    """
    A class representing a json config file used for testing the protocol.
    """

    def __init__(self, nodes=None):
        if nodes:
            self.nodes = nodes
        else:
            self.nodes = []

    @staticmethod
    def create_config_file(test_configuration, filename="test_example.json"):
        if not isinstance(test_configuration, TestConfiguration):
            return None
        data = {
            "nodes": [

            ]
        }
        for node in test_configuration.nodes:
            structure_to_append = {
                "name": node.name
            }
            data["nodes"].append(structure_to_append)
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

    @staticmethod
    def read_config_from_file(filename):
        try:
            fd = open(filename, 'r')
            data = fd.read()
            return TestConfiguration.json_to_object(data)
        except FileNotFoundError as e:
            print(e.args)
            return None

    @staticmethod
    def json_to_object(json_file):
        data = json.loads(json_file)
        if 'nodes' in data:
            test_conf = TestConfiguration()
            for node in data["nodes"]:
                if 'name' in data["nodes"]:
                    conf_node = ConfigurationNode(node['name'])
                    test_conf.nodes.append(conf_node)
            return test_conf
        return None


class ConfigurationNode(object):
    """
    A class to represent a configuration node
    """
    def __init__(self, name):
        self.name = name

    @staticmethod
    def get_names_from_node_list(nodes):
        node_names = []
        for node in nodes:
            if not isinstance(node, ConfigurationNode):
                continue
            node_names.append(node.name)
        return node_names