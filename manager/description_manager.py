from manager.description_message_handler import DescriptionMessageHandler
from message.description_request_list import DescriptionRequestList
from networking.socket import Socket
from app.globals import BUFFER_SIZE

class DescriptionManager(object):
    """
        Manages descriptions.
        Handles incoming
    """
    def __init__(self, description_manager):
        if not isinstance(description_manager, DescriptionMessageHandler):
            raise RuntimeError
        self.description_manager = description_manager

    def respond_to_description_request(self, tcp_socket, description_request_list):
        """

        :return:
        """
        if not isinstance(description_request_list, DescriptionRequestList):
            raise RuntimeError
        if not isinstance(tcp_socket, Socket):
            raise RuntimeError

        tcp_socket.socket.recv(BUFFER_SIZE)
        # TODO: Continue implementing method!!

    def send_description_request(self, tcp_socket):
        """

        :param tcp_socket:
        :return:
        """
