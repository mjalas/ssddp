from manager.discovery_message_handler import DiscoveryMessageManager
from app.globals import BUFFER_SIZE


class DiscoveryListener(object):
    """
        Listens to incoming discovery messages and handles them
    """
    def __init__(self, discovery_manager):
        if not isinstance(discovery_manager, DiscoveryMessageManager):
            raise RuntimeError
        self.discovery_manager = discovery_manager

    def handle_discovery(self, udp_socket):  # TODO: Implement method
        """
        Handles the incoming discovery message.
        :return:
        """
        udp_socket.socket.recv(BUFFER_SIZE)
        pass