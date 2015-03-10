import unittest
from unittest import mock
from queue import Queue

from node.peer_node_manager import PeerNodeManager, UpdateResult
from node.peer_node import PeerNode
from node.peer_node_list import PeerNodeList
from node.node_address import Address
from message.message import Message
from message.timestamp import Timestamp
from message.message_types import MessageType


class TestPeerNodeManager(unittest.TestCase):
    """
    Tests for the PeerNodeManager class.
    """

    def setUp(self):
        self.message_queue = Queue()
        self.node_list = PeerNodeList()
        self.address = Address("127.0.0.1", 8880)
        self.timestamp = Timestamp.create_timestamp()
        self.node_name = "hello node"
        self.node1 = PeerNode(self.node_name, self.address, self.timestamp)

    def test_init(self):
        self.assertRaisesRegex(ValueError, PeerNodeManager.queue_error_string,
                               PeerNodeManager, "queue", "node_list")
        self.assertRaisesRegex(ValueError, PeerNodeManager.node_list_error_string,
                               PeerNodeManager, self.message_queue, "node_list")
        manager = PeerNodeManager(self.message_queue, self.node_list)
        self.assertEqual(self.message_queue, manager.message_queue)
        self.assertEqual(self.node_list, manager.node_list)
        self.assertTrue(manager.keep_alive)

    def test_read_message_from_queue(self):
        message = mock.create_autospec(Message)
        manager = PeerNodeManager(self.message_queue, self.node_list)
        self.message_queue.put_nowait(message)
        message_from_queue = manager.read_message_from_queue()
        manager.message_queue.task_done()
        self.assertEqual(message, message_from_queue)

    def test_update_node_list(self):
        self.assertRaises(ValueError, self.node1.update_node, "hello")
        test_name = "bye node"
        test_ip = "127.0.0.1"
        test_port = 8880
        test_address = Address(test_ip, test_port)
        test_timestamp = Timestamp.create_timestamp()
        message1 = Message(MessageType.description_response, test_name, test_address, test_timestamp)
        message2 = Message(MessageType.description_response, self.node_name, test_address, test_timestamp)

        manager = PeerNodeManager(self.message_queue, self.node_list)
        self.assertEqual(0, manager.node_list.count())
        self.assertEqual(UpdateResult.added_new_node, manager.update_node_list(message1))
        self.assertEqual(1, manager.node_list.count())
        manager.node_list.add(self.node1)
        self.assertEqual(UpdateResult.updated_existing_node, manager.update_node_list(message2))

