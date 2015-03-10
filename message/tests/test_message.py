import unittest
from message.message import Message
from message.message_types import MessageType
from message.timestamp import Timestamp
from node.node_address import Address


class TestMessage(unittest.TestCase):
    """

    """

    def setUp(self):
        address = Address('192.168.0.10', 8880)
        self.timestamp = Timestamp.create_timestamp()
        self.message = Message(MessageType.description_request,'test_node', address, self.timestamp)
        self.test_data = {'name': 'test_node', 'address': {'ip': '192.168.0.10', 'port': 8880},
                          'timestamp': self.timestamp}

    def test_constructor(self):
        address = Address('192.168.0.10', 8880)
        timestamp = Timestamp.create_timestamp()
        message = Message(MessageType.description_request, 'test_node', address, timestamp)
        self.assertEqual(MessageType.description_request, message.message_type)
        self.assertEqual('test_node', message.node_name)
        self.assertEqual('192.168.0.10', message.address.ip)
        self.assertEqual(8880, message.address.port)
        self.assertEqual(timestamp, message.timestamp)

    def test_add_service(self):
        pass  # need to be implemented

if __name__ == '__main__':
    unittest.main()