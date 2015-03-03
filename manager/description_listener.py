from message.description_request_list import DescriptionRequestList
import socket
import threading


class DescriptionListener(threading.Thread):
    """
        Manages descriptions.
        Handles incoming
    """
    def __init__(self, connection, client_address):
        if not isinstance(connection, socket.socket):
            raise RuntimeError
        self.connection = connection
        self.client_address = client_address
        self._target = self.respond_to_description_request
        threading.Thread.__init__(self)

    def respond_to_description_request(self, description_request_list):
        """

        :return:
        """
        if not isinstance(description_request_list, DescriptionRequestList):
            raise RuntimeError

        # TODO: Finish response creation
        response = ""
        # TODO: Send response
        self.connection.socket.send(response)

    def run(self):
        self._target()