from message.timestamp import Timestamp
from service.service_list import ServiceList
from json import JSONEncoder
import json


class Node(object):

    def __init__(self, name, address, service_list_file=None, service_json_list=None, services=None):
        self.name = name
        self.address = address
        self.service_list = ServiceList()
        self.logfile = None
        self.creation_time = Timestamp.create_timestamp()
        if service_json_list:
            self.service_list.from_dict(service_json_list)
        elif service_list_file:
            self.service_list.from_file(service_list_file)
        elif services:
            self.service_list = services

    def initialize_logfile(self, logfile):
        self.logfile = logfile
        logfile.log("Node initialized ({0})".format(self.creation_time))


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

