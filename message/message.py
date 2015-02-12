from service.service_list import ServiceList


class Message(object):
    """

    """
    def __init__(self, node_name, address, timestamp):
        self.node_name = node_name
        self.address = address
        self.timestamp = timestamp
        self.services = ServiceList()

    def add_service(self, new_service):
        self.services.add(new_service)