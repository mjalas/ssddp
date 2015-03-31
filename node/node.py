from service.service_list import ServiceList
from json import JSONEncoder


class Node(object):

    def __init__(self, name, address, service_list_file=None, service_json_list=None):
        self.name = name
        self.address = address
        self.service_list = ServiceList()
        if service_json_list:
            self.service_list.from_dict(service_json_list)
        elif service_list_file:
            self.service_list.from_file(service_list_file)


class NodeEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Node):
            d = {'name': o.name, 'address': o.address}
            services = []
            for service in o.service_list:
                services.append(service)
            d['services'] = services
            return d
        else:
            raise TypeError("Given argument is not of type Node!")

