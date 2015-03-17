import json
import logging
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
        self.discovery_message_handler = discovery_message_handler
        self.self_node = self_node
        self.peer_list = peer_list
        self.udp_socket = Socket("UDP", self.self_node.name)
        self.hub_timestamp = Timestamp.create_timestamp()
        self.logger = logging.getLogger(self.self_node.name + ": " + __name__)
        self.logger.debug("Discovery Broadcast Loop initialized")

    def start_broadcast(self):
        """
        Runs the broadcast loop
        :return:
        """
        # Create discovery message from node info
        message = self.discovery_message_handler.create_message(self.self_node)

        # Convert message to json
        json_message = json.dumps(message.to_json())

        # Encode message to utf-8 for sending through socket
        data = json_message.encode()
        self.send_message(data)

        # Sleep and restart cycle
        sleep(BROADCAST_INTERVAL)
        self.start_broadcast()

    def send_message(self, message):
        """
        Sends the message to the hub.
        If the hub has timed out, sends the message also to all available ports.
        :return:
        """

        if self.hub_timestamp_expired():

            self.logger.info("Hub timestamp expired; Sending packet to all available ports.")
            # Hub has expired: Send message to all ports
            for port in AVAILABLE_PORTS:
                self.udp_socket.sendto(message, ("127.0.0.1", port))

        # Send to Hub regardless of timestamp
        # (This allows the hub to be recovered)
        self.logger.info("Sending Discovery packet to hub")
        self.udp_socket.sendto(message, HUB_ADDRESS)

    def update_timestamp(self):
        self.hub_timestamp = Timestamp.create_timestamp()

    def hub_timestamp_expired(self):
        current_time = Timestamp.create_timestamp()
        if (current_time - self.hub_timestamp) > HUB_TIMEOUT:
            return True
        return False