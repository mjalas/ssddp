import unittest
from node.node_address import Address


class TestAddress(unittest.TestCase):
    """

    """

    def test_init(self):
        test_ip = "127.0.0.1"
        test_port = 8880
        address = Address(test_ip, test_port)
        [ip, port] = address.get_address()
        self.assertEqual(test_ip, ip)
        self.assertEqual(test_port, port)