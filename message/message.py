import json

from service.service_list import ServiceList
from node.node_address import Address


class Message(object):
    """

    """

    def __init__(self, message_type, node_name, address, timestamp, services=None, protocol='ssddp'):
        self.message_type = message_type
        self.node_name = node_name
        self.address = address
        self.timestamp = timestamp
        self.protocol = protocol
        self.from_hub = False
        if services:
            self.services = services
        else:
            self.services = ServiceList()

        """
        print("MESSAGE <<< START >>>")
        dict1 = self.__dict__
        for x in dict1:
            print(x+":"+str(dict1[x]))
        print("MESSAGE <<< END >>>")
        """

    def add_service(self, new_service):
        self.services.append(new_service)

    def to_json(self):
        """
        Converts message to json format.
        Returns complete description message
        """
        data = {'name': self.node_name, 'address': {'ip': self.address[0], 'port': self.address[1]},
                'timestamp': self.timestamp,
                'services': self.services.to_list()}
        return data

    def to_discovery_json(self):
        """
        Converts message to json format but omits service descriptions.
        Returns a discovery message
        """
        data = {'name': self.node_name, 'address': {'ip': self.address[0], 'port': self.address[1]},
                'timestamp': self.timestamp,
                'services': self.services.to_discovery_list()}
        return data

    @staticmethod
    def to_object(json_string):
        data = json.loads(json_string)
        '''
        if 'protocol' not in data:
            raise ValueError("Protocol key not present in data!")
        elif data['protocol'] is not 'ssddp':
            raise ValueError("Not the correct protocol!")
        if 'message_type' not in data:
            raise ValueError("Message type missing!")
        if 'type' not in data:
            raise ValueError("Type missing")
        '''
        if 'name' not in data:
            raise ValueError("Node name key not present in data!")
        if 'address' not in data:
            raise ValueError("Address key not present in data!")
        if 'services' not in data:
            raise ValueError("Services key not present in data")

        # address = Address(data['address']['ip'], data['address']['port'])
        address = (data['address']['ip'], data['address']['port'])
        # TODO: Message type is hardcoded as "2"
        if data['services']:
            message = Message(2, data['name'], address, data['timestamp'], data['services'])
        else:
            message = Message(2, data['name'], address, data['timestamp'])
        if 'hub' in data:
            message.from_hub = True

        return message