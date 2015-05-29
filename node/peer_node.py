from datetime import datetime

from app.globals import NODE_TIMEOUT
from message.message import Message
from message.timestamp import Timestamp
from node.node import Node
from service.service_list import ServiceList


class PeerNode(object):
    """

    """
    message_type_error_string = "Message not of type Message."

    def __init__(self, node, timestamp,):
        self.node = node
        self.timestamp = timestamp
        self.diff = timestamp - timestamp

    @staticmethod
    def create_node_from_message(message):
        if not isinstance(message, Message):
            raise ValueError(PeerNode.message_type_error_string)
        node = Node(message.node_name, message.address, None, message.services)
        peer_node = PeerNode(node, message.timestamp)
        return peer_node

    def update_node(self, message):

        if not isinstance(message, Message):
            raise ValueError(PeerNode.message_type_error_string)
        if self.node.name is not message.node_name:
            self.node.name = message.node_name
        if self.node.address is not message.address:
            self.node.address = message.address
        if self.timestamp < message.timestamp:
            self.timestamp = message.timestamp

        # Update old service list with new data
        new_service_list = ServiceList()
        new_service_list.from_dict(message.services)
        self.node.service_list.update_merge(new_service_list)

    def is_timed_out(self, timeout_boundary=NODE_TIMEOUT):
        """
        Checks whether the node has timed out
        """
        now = datetime.now()
        timestamp = Timestamp.timestamp_to_datetime(self.timestamp)
        diff = (now - timestamp)
        seconds = diff.seconds
        self.diff = seconds
        # print("Diff: {0}, timeout: {1}>{2} -> {3}".format(self.diff, seconds, timeout_boundary, seconds > timeout_boundary))
        if seconds > timeout_boundary:
            return True
        return False

    def time_since_last_discovery(self):
        now = Timestamp.create_timestamp()
        diff = (now - self.timestamp)
        return diff