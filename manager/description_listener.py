import socket
import threading
import logging
from datetime import datetime

from app.globals import BUFFER_SIZE
from message.message import Message
from message.message_types import MessageType
from node.peer_node import PeerNode
from node.node import Node
from message.timestamp import Timestamp
from app.logfile import Logfile


class DescriptionListener(threading.Thread):
    """
        Manages descriptions.
        Handles incoming
    """
    def __init__(self, connection, client_address, node):
        if not isinstance(connection, socket.socket):
            raise IOError("Given connection not of type socket!")
        if not isinstance(node, Node):
            raise ValueError("Node argument was not of type PeerNode!")
        self.node = node
        self.connection = connection
        self.client_address = client_address
        self._target = self.respond_to_description_request
        self.filename = "description_" + self.node.name + ".log"

        self.logger = logging.getLogger(node.name + ": " + __name__)
        self.logger.info("Description Listener initialized")
        threading.Thread.__init__(self)

    def respond_to_description_request(self):
        """
        Handles the description request and sends a response.
        :return:
        """

        self.logger.debug("Responding to description request")
        data = self.connection.recv(BUFFER_SIZE).decode('UTF-8')
        print(self.node.name + " received a description request:\n" + data)

        with open(self.filename, 'a') as f:
            log_message = str(datetime.now()) + ": " + "Description request received"
            f.write(log_message)
            log_message = "\t\t" + data
            f.write(log_message)
            f.flush()

        if len(data) <= 0:
            return
        try:
            message = Message.to_object(data)
        except ValueError as e:
            self.logger.error(e.args[0])
            print(e.args)
            return
        if message.message_type is MessageType.description_request:
            response = Message(MessageType.description_response, self.node.name, self.node.address,
                               Timestamp.create_timestamp(), self.node.service_list)
            self.connection.socket.send(response.to_json())
        else:  # Handle wrong request!
            pass

    def run(self):
        # self._target()
        self.respond_to_description_request()