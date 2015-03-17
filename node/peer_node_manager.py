from enum import Enum
import threading
from queue import Queue
import logging

from message.message import Message
from node.peer_node_list import PeerNodeList
from node.peer_node import PeerNode
from node.exceptions.node_exceptions import PeerNodeNotFoundException

log = logging.getLogger(__name__)


class PeerNodeManager(threading.Thread):
    """

    """
    queue_error_string = "Given Message Queue is not of type Queue."
    node_list_error_string = "Given node list is not of type PeerNodeList."

    def __init__(self, message_queue, node_list):
        if not isinstance(message_queue, Queue):
            raise ValueError(PeerNodeManager.queue_error_string)
        if not isinstance(node_list, PeerNodeList):
            raise ValueError(PeerNodeManager.node_list_error_string)
        self.message_queue = message_queue
        self.node_list = node_list
        self.keep_alive = True
        self._target = self.handle_queue
        threading.Thread.__init__(self)

    def read_message_from_queue(self):
        message = self.message_queue.get()
        if not isinstance(message, Message):
            raise ValueError("Message not of type Message!")
        return message

    def update_node_list(self, message):
        added_new = False
        try:
            node = self.node_list.get(message.node_name)
            node.update_node(message)
        except PeerNodeNotFoundException:
            node = PeerNode.create_node_from_message(message)
            self.node_list.add(node)
            added_new = True

        if added_new:
            return UpdateResult.added_new_node
        else:
            return UpdateResult.updated_existing_node

    def handle_queue(self):
        while self.keep_alive:
            message = self.read_message_from_queue()
            self.update_node_list(message)
            self.message_queue.task_done()

    def run(self):
        # self._target()
        self.handle_queue()



class UpdateResult(Enum):
    added_new_node = 1
    updated_existing_node = 2