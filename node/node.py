from service.service_list import ServiceList


class Node(object):

    def __init__(self, name, services=None):
        self.name = name
        if services is None:
            self.service_list = ServiceList()
        else:
            self.service_list = services

