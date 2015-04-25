import json
from service.service_list import ServiceList
from node.node import Node
from service.service_list import ServiceList
from service.service import Service


class TestConfiguration(object):
    """
    A class representing a json config file used for testing the protocol.
    """

    def __init__(self, nodes=None):
        if nodes:
            self.nodes = nodes
        else:
            self.nodes = []
        self.services = None

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
            with open(filename) as data_file:
                data = json.load(data_file)

            return TestConfiguration.json_to_object(data)
        except FileNotFoundError as e:
            print(e.args)
            return None

    @staticmethod
    def read_config_from_file_v2(filename):
        try:
            with open(filename) as data_file:
                data = json.load(data_file)

            return TestConfiguration.json_to_nodes(data)
        except FileNotFoundError as e:
            print(e.args)
            return None

    @staticmethod
    def read_config_from_data(data):
        data = json.loads(data)
        return TestConfiguration.json_to_object(data)

    @staticmethod
    def read_config_from_data_v2(data):
        data = json.loads(data)
        return TestConfiguration.json_to_nodes(data)

    @staticmethod
    def json_to_object(data):
        if 'nodes' in data:
            test_conf = TestConfiguration()
            for node in data["nodes"]:
                if 'name' in node:

                    if 'services' in node:
                        print("services: " + str(node['services']))
                        services = ServiceList()
                        # service_data = json.loads(node['services'])
                        #services.from_dict(str(node['services']))
                        #conf_node = ConfigurationNode(node['name'], services)
                        conf_node = ConfigurationNode(node['name'])
                    else:
                        conf_node = ConfigurationNode(node['name'])
                    test_conf.nodes.append(conf_node)
            return test_conf
        return None

    @staticmethod
    def get_services_for_node(node_data, services):
        for service_data in node_data['services']:
            found_count = 0
            service_name = ''
            service_type = ''
            service_description = ''
            if 'name' in service_data:
                service_name = service_data['name']
                found_count += 1
            if 'service_type' in service_data:
                service_type = service_data['service_type']
                found_count += 1
            if 'description' in service_data:
                service_description = service_data['description']
                found_count += 1
            if found_count == 3:
                service = Service(name=service_name, service_type=service_type,
                                  description=service_description)
                services.append(service)

    @staticmethod
    def json_to_nodes(data):
        if 'nodes' in data:
            nodes = []
            for node_data in data['nodes']:
                if 'name' in node_data:
                    node_name = node_data['name']
                    services = ServiceList()
                    if 'services' in node_data:
                        TestConfiguration.get_services_for_node(node_data, services)
                    if node_name and not services.is_empty():
                        node = ConfigurationNode(name=node_name, services=services)
                    else:
                        node = ConfigurationNode(name=node_name)
                    nodes.append(node)
            return nodes
        return None


class ConfigurationNode(object):
    """
    A class to represent a configuration node
    """

    def __init__(self, name, services=None):
        self.name = name
        self.services = services

    @staticmethod
    def get_names_from_node_list(nodes):
        node_names = {}
        for i, node in enumerate(nodes):
            if not isinstance(node, ConfigurationNode):
                continue
            node_names[i + 1] = node.name
        return node_names