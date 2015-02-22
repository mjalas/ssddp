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

    def services_to_list(self):
        service_list = []
        for service in self.services.services:
            service_list.append(service.to_json())
        return service_list

    def to_json(self):
        data = {'name': self.node_name, 'address': {'ip': self.address.ip, 'tcp_port': self.address.tcp_port,
                                                    'udp_port': self.address.udp_port}, 'timestamp': self.timestamp,
                'services': self.services_to_list()}
        return data

    @staticmethod
    def to_object(json_string):
        data = json.loads(json_string)
        address = Address(data['address']['ip'], data['address']['udp_port'], data['address']['tcp_port'])
        message = Message(data['name'], address, data['timestamp'])
        return message