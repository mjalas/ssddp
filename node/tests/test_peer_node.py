import unittest
from unittest import mock

from node.peer_node import PeerNode
from node.node_address import Address
from message.timestamp import Timestamp
from service.service_list import ServiceList
from message.message import Message
from message.message_types import MessageType


class TestPeerNode(unittest.TestCase):
    """
    Tests for PeerNode class initialization and class methods.
    """

    def test_init_no_services(self):
        test_name = "test name"
        mock_address = mock.create_autospec(Address)
        mock_timestamp = mock.create_autospec(Timestamp)
        node = PeerNode(test_name, mock_address, mock_timestamp)
        self.assertEqual(test_name, node.name)
        self.assertEqual(mock_address, node.address)
        self.assertEqual(mock_timestamp, node.timestamp)

    def test_init_services(self):
        test_name = "test name"
        mock_address = mock.create_autospec(Address)
        mock_timestamp = mock.create_autospec(Timestamp)
        mock_service_list = mock.create_autospec(ServiceList)
        node = PeerNode(test_name, mock_address, mock_timestamp, mock_service_list)
        self.assertEqual(test_name, node.name)
        self.assertEqual(mock_address, node.address)
        self.assertEqual(mock_timestamp, node.timestamp)
        self.assertEqual(mock_service_list, node.service_list)

    def test_create_node_from_message(self):
        message = "hello"
        self.assertRaisesRegex(ValueError, "Message not of type Message",
                               PeerNode.create_node_from_message, message)
        test_name = "test name"
        test_ip = "127.0.0.1"
        test_port = 8880
        test_address = Address(test_ip, test_port)
        test_timestamp = Timestamp.create_timestamp()
        message = Message(MessageType.description_response, test_name, test_address, test_timestamp)
        node = PeerNode.create_node_from_message(message)
        self.assertEqual(test_name, node.name)
        self.assertEqual(test_address, node.address)
        self.assertEqual(test_timestamp, node.timestamp)

    def test_update(self):
        test_name = "test name"
        hello = "hello"
        test_ip = "127.0.0.1"
        test_port = 8880
        test_address = Address(test_ip, test_port)
        test_timestamp = Timestamp.create_timestamp()
        node = PeerNode(hello, test_address, test_timestamp)
        message = Message(MessageType.description_response, test_name, test_address, test_timestamp)
        self.assertEqual(hello, node.name)
        node.update_node(message)
        self.assertEqual(test_name, node.name)
        # TODO: add more test to change the other values of the node!