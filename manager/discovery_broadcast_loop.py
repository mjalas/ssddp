from manager.discovery_message_handler import DiscoveryMessageManager
from networking.socket import Socket


class DiscoveryBroadcastLoop(object):
    """

    """
    def __init__(self, discovery_message_manager, peer_list, ):
        if not isinstance(discovery_message_manager, DiscoveryMessageManager):
            raise RuntimeError
        self.discovery_message_manager = discovery_message_manager
        self.previous_message = None
        self.peer_list = peer_list
        self.udp_socket = Socket("UDP")

    def start_broadcast(self):
        """

        :return:
        """
        # preliminary logic - CAN BE CHANGED

        if self.found_new_services() or self.previous_message is None:
            message = self.discovery_message_manager.create_message()
        else:
            message = self.previous_message
        self.send_message(message)
        self.previous_message = message

    def found_new_services(self):  # TODO: Implement real logic
        """

        :return:
        """
        return True

    def send_message(self, message):  # TODO: Implement method
        """

        :return:
        """
        pass