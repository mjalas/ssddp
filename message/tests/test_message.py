import unittest
from message.message import Message
from message.timestamp import Timestamp
from node.node_address import Address


class TestMessage(unittest.TestCase):
    """

    """

    def setUp(self):
        address = Address('192.168.0.10', 5560, 5561)
        self.timestamp = Timestamp.create_timestamp()
        self.message = Message('test_node', address, self.timestamp)
        self.test_data = {'name': 'test_node', 'address': {'ip': '192.168.0.10', 'udp_port': 5560,
                                                           'tcp_port': 5561}, 'timestamp': self.timestamp}

    def test_constructor(self):
        address = Address('192.168.0.10', 5560, 5561)
        timestamp = Timestamp.create_timestamp()
        message = Message('test_node', address, timestamp)
        self.assertEqual('test_node', message.node_name)
        self.assertEqual('192.168.0.10', message.address.ip)
        self.assertEqual(5560, message.address.udp_port)
        self.assertEqual(5561, message.address.tcp_port)
        self.assertEqual(timestamp, message.timestamp)

    def test_add_service(self):
        pass  # need to be implemented

if __name__ == '__main__':
    unittest.main()