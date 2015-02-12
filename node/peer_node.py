from node.node_address import Address
from service.service_list import ServiceList

class PeerNode(object):
    """

    """
    def __init__(self, name, address, timestamp):
        self.name = name
        self.address = address
        self.timestamp = timestamp
        self.service_list = ServiceList()