from time import sleep

from app.globals import BROADCAST_INTERVAL, HUB_ADDRESS, HUB_TIMEOUT, AVAILABLE_PORTS
from message.discovery_message_handler import DiscoveryMessageHandler
from message.timestamp import Timestamp
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
        self.timestamp = Timestamp.create_timestamp()

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

    def send_message(self, message):
        """
        Sends the message to the hub.
        If the hub has timed out, sends the message also to all available ports.
        :return:
        """

        if self.hub_timestamp_expired():

            # Hub has expired: Send message to all ports
            for port in AVAILABLE_PORTS:
                self.udp_socket.sendto(message, ("127.0.0.1", port))

        # Send to Hub regardless of timestamp
        # (This allows the hub to be recovered)
        self.udp_socket.sendto(message, HUB_ADDRESS)

    def update_timestamp(self):
        self.timestamp = Timestamp.create_timestamp()

    def hub_timestamp_expired(self):
        current_time = Timestamp.create_timestamp()
        if (current_time - self.timestamp) > HUB_TIMEOUT:
            return True
        return False