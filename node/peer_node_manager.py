import threading

from message.message import Message
from node.peer_node_list import PeerNodeList


class PeerNodeManager(threading.Thread):
    """

    """
    def __init__(self, message_queue, node_list):
        self.message_queue = message_queue
        self.node_list = node_list
        self.keep_alive = True
        threading.Thread.__init__(self)


    def run(self):
        while self.keep_alive:
            message = self.message_queue.get()
            if isinstance(message, Message):
                node = self.node_list.get(message.node_name)[0]
                node.update_node(message)
            self.message_queue.task_done()