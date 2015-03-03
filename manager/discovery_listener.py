import threading

from networking.socket import Socket
from message.message import Message


class DiscoveryListener(threading.Thread):
    """
        Listens to incoming discovery messages and handles them
    """
    def __init__(self, data, address, message_queue):
        self._target = self.handle_discovery
        self.data = data
        self.address = address
        self.message_queue = message_queue
        threading.Thread.__init__(self)

    def handle_discovery(self):  # TODO: Implement method
        """
        Handles the incoming discovery message.
        Creates a message object from the data
        :return:
        """
        message = self.handle_data()
        if message:
            self.message_queue.put(message)

    def handle_data(self):
        message = None
        if self.data:
            message = Message.to_object(self.data)
        return message

    def run(self):
        self._target()