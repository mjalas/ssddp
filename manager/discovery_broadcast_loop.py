
from time import sleep
from app.globals import BROADCAST_INTERVAL

from manager.discovery_message_handler import DiscoveryMessageHandler

from networking.socket import Socket


class DiscoveryBroadcastLoop(object):
    """
        Broadcasts discovery messages to all peers via the hub.
    """
    def __init__(self, discovery_message_handler, peer_list, self_node, hub_address):
        if not isinstance(discovery_message_handler, DiscoveryMessageHandler):
            raise RuntimeError
        self.discovery_message_manager = discovery_message_handler
        self.previous_message = None
        self.self_node = self_node
        self.peer_list = peer_list
        self.udp_socket = Socket("UDP")

    def start_broadcast(self):
        """
        Runs the broadcast loop
        :return:
        """
        # preliminary logic - CAN BE CHANGED

        if self.found_new_services() or self.previous_message is None:
            message = self.discovery_message_manager.create_message()
        else:
            message = self.previous_message
        self.send_message(message)
        self.previous_message = message

        sleep(BROADCAST_INTERVAL)
        self.start_broadcast()

    def found_new_services(self):  # TODO: Implement real logic
        """
        New service found
        :return:
        """

        return self.self_node.has_new_services()

    def send_message(self, message):  # TODO: Implement method
        """

        :return:
        """
        if self.hub_address:
            self.udp_socket.sendto(message, self.hub_address)
        else:
            # TODO: Phase 2 port scanning
            pass