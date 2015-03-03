from manager.discovery_manager import DiscoveryManager


class DiscoveryReceiveManager(object):
    """

    """
    def __init__(self, discovery_manager):
        if not isinstance(discovery_manager, DiscoveryManager):
            raise RuntimeError
        self.discovery_manager = discovery_manager

    def handle_discovery(self, udp_socket):  # TODO: Implement method
        """
        Handles the incoming discovery message.
        :return:
        """
        pass