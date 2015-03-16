from service.service_list import ServiceList


class Node(object):

    def __init__(self, name, address, services=None):
        self.name = name
        self.address = address
        if services is None:
            self.service_list = ServiceList()
        else:
            self.service_list = services

