from time import sleep

from app.globals import BROADCAST_INTERVAL, HUB_ADDRESS
from message.discovery_message_handler import DiscoveryMessageHandler
from networking.socket import Socket


class DiscoveryBroadcastLoop(object):
    """
    Broadcasts discovery messages to all peers via the hub.
    In the absence of hub, sends the messages to all available ports
    """
    def __init__(self, discovery_message_handler, peer_list, self_node):
        if not isinstance(discovery_message_handler, DiscoveryMessageHandler):
            raise RuntimeError
        self.discovery_message_manager = discovery_message_handler
        self.previous_message = None
        self.self_node = self_node
        self.peer_list = peer_list
        self.udp_socket = Socket("UDP")
        self.hub_available = True

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
        if self.hub_available:
            self.udp_socket.sendto(message, HUB_ADDRESS)
        else:
            # TODO: Phase 2 port scanning
            pass

    def hub_status(self, hub_availability):
        """
        Used to notify the loop whether or not hub can be used
        :param hub_availability:
        :return:
        """
        self.hub_available = hub_availability