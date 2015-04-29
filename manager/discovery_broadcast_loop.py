import json
import logging
import threading
from time import sleep

from app.globals import BROADCAST_INTERVAL, HUB_ADDRESS_TO, HUB_TIMEOUT, AVAILABLE_PORTS, PORT_SCAN_INTERVAL
from message.discovery_message_handler import DiscoveryMessageHandler
from message.timestamp import Timestamp
from networking.socket import Socket
from app.globals import NodeCommand


class DiscoveryBroadcastLoop(threading.Thread):
    """
    Broadcasts discovery messages to all peers via the hub.
    In the absence of hub, sends the messages to all available ports
    """
    def __init__(self, discovery_message_handler, peer_list, self_node, message_queue, udp_socket):
        if not isinstance(discovery_message_handler, DiscoveryMessageHandler):
            raise RuntimeError
        threading.Thread.__init__(self)
        self._target = self.start_broadcast
        self.discovery_message_handler = discovery_message_handler
        self.self_node = self_node
        self.peer_list = peer_list
        self.udp_socket = udp_socket
        self.hub_timestamp = Timestamp.create_timestamp()
        self.message_queue = message_queue
        self.port_scan_delay = 1
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
            json_message = json.dumps(message.to_discovery_json())
            # json_hub_message = json.dumps(message.to_discovery_json())[:-1]+", \"hub\": 1}"

            # Encode message to utf-8 for sending through socket
            data = json_message.encode()
            # hub_data = json_hub_message.encode() # Unnecessary now that udp socket ports are working
            # self.send_message(data, hub_data)
            self.send_message(data, data)

            # Check if any command message has been sent
            if not self.message_queue.empty():
                try:
                    message = self.message_queue.get(timeout=2)
                    if message == NodeCommand.SHUTDOWN:
                        self.logger.info("Received shutdown message, shutting down immediately.")
                        exit(0)
                except ValueError:
                    pass
            # Sleep and restart cycle
            sleep(BROADCAST_INTERVAL)
        # self.start_broadcast()

    def send_message(self, message, hub_message):
        """
        Sends the message to the hub.
        If the hub has timed out, sends the message also to all available ports.
        :return:
        """

        if self.hub_timestamp_expired():

            # Hub has expired
            self.port_scan_delay -= 1

            if self.port_scan_delay <= 0:
                # Reset scan interval & send message to all ports
                self.port_scan_delay = PORT_SCAN_INTERVAL
                self.logger.info("Discovery -> Hub + all ports, (hub expired)")
                self.port_scan(message)
            else:
                # Send message to all known peers
                self.logger.info("Discovery -> Known peers, (hub expired)")
                self.message_known_nodes(message)

        else:
            self.logger.info("Discovery -> Hub")

        # Send to Hub regardless of timestamp
        # (This allows the hub to be recovered)
        self.udp_socket.sendto(hub_message, HUB_ADDRESS_TO)

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

    def port_scan(self, message):
        """
        Send given message to all available ports
        """
        for port in AVAILABLE_PORTS:
            # ...Except our own port
            if port != self.self_node.address[1]:
                self.udp_socket.sendto(message, ("127.0.0.1", port))

    def message_known_nodes(self, message):
        """
        Send given message to all known peer addresses
        """
        self.peer_list.message_list(self.udp_socket, message)