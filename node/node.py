from service.service_list import ServiceList


class Node(object):

    def __init__(self, name, address, service_list_file=None):
        self.name = name
        self.address = address
        self.service_list = ServiceList()
        if service_list_file:
            self.service_list.read_file(service_list_file)