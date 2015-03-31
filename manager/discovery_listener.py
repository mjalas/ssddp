import logging
import threading
from app.globals import HUB_ADDRESS

from networking.socket import Socket
from message.message import Message


class DiscoveryListener(threading.Thread):
    """
        Listens to incoming discovery messages and handles them
    """

    def __init__(self, data, address, message_queue, broadcast_manager, self_node):
        self._target = self.handle_discovery
        self.data = data
        self.address = address
        self.message_queue = message_queue
        self.broadcast_manager = broadcast_manager
        self.logger = logging.getLogger(self_node.name + ": " + __name__)
        self.logger.info("Discovery Listener initialized")
        threading.Thread.__init__(self)

    def handle_discovery(self):  # TODO: Implement method
        """
        Handles the incoming discovery message.
        Creates a message object from the data
        :return:
        """
        self.logger.debug("Incoming message")
        message = self.handle_data()
        if message:
            if message.from_hub:
                self.update_broadcast_timestamp()
            self.logger.debug("Message: %s", message)
            self.message_queue.put(message)

    def handle_data(self):
        self.logger.debug("Handling incoming data")
        message = None
        if self.data:
            self.logger.debug("Incoming discovery data from (" + str(self.address[0]) + ", " + str(
                self.address[1]) + "):\n<<<START>>>\n" + self.data.decode() + "\n<<<END>>>")
            message = Message.to_object(self.data.decode())
        return message

    def update_broadcast_timestamp(self):
        self.logger.debug("Updating broadcast timestamp")
        self.broadcast_manager.update_timestamp()

    def run(self):
        # self._target()
        self.handle_discovery()