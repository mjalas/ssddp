import json
import logging
import threading
from time import sleep

from app.globals import BROADCAST_INTERVAL, HUB_ADDRESS, HUB_TIMEOUT, AVAILABLE_PORTS
from message.discovery_message_handler import DiscoveryMessageHandler
from message.timestamp import Timestamp
from networking.socket import Socket
from app.globals import NodeCommands


class DiscoveryBroadcastLoop(threading.Thread):
    """
    Broadcasts discovery messages to all peers via the hub.
    In the absence of hub, sends the messages to all available ports
    """
    def __init__(self, discovery_message_handler, peer_list, self_node, message_queue):
        if not isinstance(discovery_message_handler, DiscoveryMessageHandler):
            raise RuntimeError
        threading.Thread.__init__(self)
        self._target = self.start_broadcast
        self.discovery_message_handler = discovery_message_handler
        self.self_node = self_node
        self.peer_list = peer_list
        self.udp_socket = Socket("UDP", self.self_node.name)
        self.hub_timestamp = Timestamp.create_timestamp()
        self.message_queue = message_queue
        self.logger = logging.getLogger(self.self_node.name + ": " + __name__)
        self.logger.debug("Discovery Broadcast Loop initialized")

    def start_broadcast(self):
        """
        Runs the broadcast loop
        :return:
        """
        while True:
            # Create discovery message from node info
            message = self.discovery_message_handler.create_message(self.self_node)

            # Convert message to json
            json_message = json.dumps(message.to_json())

            # Encode message to utf-8 for sending through socket
            data = json_message.encode()
            self.send_message(data)

            # Check if any command message has been sent
            if not self.message_queue.empty():
                try:
                    message = self.message_queue.get(timeout=2)
                    if message == NodeCommands.SHUTDOWN:
                        self.logger.info("Received shutdown message, shutting down immediately.")
                        exit(0)
                except ValueError:
                    pass
            # Sleep and restart cycle
            sleep(BROADCAST_INTERVAL)
        # self.start_broadcast()

    def send_message(self, message):
        """
        Sends the message to the hub.
        If the hub has timed out, sends the message also to all available ports.
        :return:
        """

        if self.hub_timestamp_expired():

            self.logger.info("Discovery -> Hub + all ports, (hub expired)")
            # Hub has expired: Send message to all ports
            for port in AVAILABLE_PORTS:
                # ...Except our own port
                if port != self.self_node.address[1]:
                    self.udp_socket.sendto(message, ("127.0.0.1", port))
        else:
            self.logger.info("Discovery -> Hub")

        # Send to Hub regardless of timestamp
        # (This allows the hub to be recovered)
        self.udp_socket.sendto(message, HUB_ADDRESS)

    def update_timestamp(self):
        self.hub_timestamp = Timestamp.create_timestamp()

    def hub_timestamp_expired(self):
        current_time = Timestamp.create_timestamp()
        if (current_time - self.hub_timestamp) > HUB_TIMEOUT:
            return True
        return False

    def run(self):
        # self._target()
        self.start_broadcast()