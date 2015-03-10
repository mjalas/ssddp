import unittest
from unittest import mock

from node.peer_node_list import PeerNodeList
from node.peer_node import PeerNode
from node.node_address import Address
from message.timestamp import Timestamp
from node.exceptions.node_exceptions import PeerNodeNotFoundException


class TestPeerNodeList(unittest.TestCase):
    """
    Tests for PeerNodeList class init and class methods.
    """

    def test_init(self):
        peer_list = PeerNodeList()
        self.assertFalse(peer_list.peers)

    def test_add(self):
        node = mock.create_autospec(PeerNode)
        peer_list = PeerNodeList()
        peer_list.add(node)
        self.assertTrue(peer_list.peers)

    def test_clear(self):
        node1 = mock.create_autospec(PeerNode)
        node2 = mock.create_autospec(PeerNode)
        peer_list = PeerNodeList()

        peer_list.add(node1)
        peer_list.add(node2)
        self.assertTrue(peer_list.peers)
        peer_list.clear()
        self.assertFalse(peer_list.peers)

    def test_get(self):
        test_name = "hello"
        mock_address = mock.create_autospec(Address)
        mock_timestamp = mock.create_autospec(Timestamp)
        node = PeerNode(test_name, mock_address, mock_timestamp)
        peer_list = PeerNodeList()
        peer_list.add(node)
        self.assertEqual(node, peer_list.get(test_name))
        self.assertRaises(PeerNodeNotFoundException, peer_list.get, "no name")

    def test_count(self):
        node1 = mock.create_autospec(PeerNode)
        node2 = mock.create_autospec(PeerNode)
        peer_list = PeerNodeList()

        peer_list.add(node1)
        peer_list.add(node2)
        self.assertEqual(2, peer_list.count())