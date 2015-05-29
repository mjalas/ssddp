import json
import logging
import threading
from time import sleep

from app.globals import BROADCAST_INTERVAL, HUB_ADDRESS_TO, HUB_TIMEOUT, AVAILABLE_PORTS, PORT_SCAN_INTERVAL
from message.discovery_message_handler import DiscoveryMessageHandler
from message.timestamp import Timestamp
from networking.socket import Socket
from app.globals import NodeCommand
from measurements.measurement_data import MeasurementData


class DiscoveryBroadcastLoop(threading.Thread):
    """
    Broadcasts discovery messages to all peers via the hub.
    In the absence of hub, sends the messages to all available ports
    """
    def __init__(self, discovery_message_handler, peer_list, self_node, message_queue, udp_socket, measurer, logger):
        if not isinstance(discovery_message_handler, DiscoveryMessageHandler):
            raise RuntimeError
        threading.Thread.__init__(self)
        self._target = self.start_broadcast
        self.discovery_message_handler = discovery_message_handler
        self.measurer = measurer
        self.self_node = self_node
        self.peer_list = peer_list
        self.udp_socket = udp_socket
        self.hub_timestamp = Timestamp.create_timestamp()
        self.message_queue = message_queue
        self.port_scan_delay = 1
        self.logger = logger
        self.logger.info("Discovery Broadcast Loop initialized")

    def start_broadcast(self):
        """
        Runs the broadcast loop
        """
        self.measurer.start_discovery(self.self_node.name)

        while True:
            # Create discovery message from node info
            encoded_message = self.create_discovery_message()
            portscan_message = self.create_discovery_message(True)

            #self.send_message(encoded_message, encoded_message, portscan_message)
            self.send_message(encoded_message, encoded_message, encoded_message)
            # TODO: Message types must be implemented before enabling portscan_messages!
            # (Otherwise recipient will not distinguish between regular and
            # simplified discovery messages. This will cause the recipient to
            # think the sender has removed all their services.)

            # Check if any command message has been sent
            if not self.message_queue.empty():
                try:
                    message = self.message_queue.get(timeout=2)
                    # print(message)
                    if message == NodeCommand.SHUTDOWN:
                        self.logger.info("Received shutdown message, shutting down immediately.")
                        # print("{0}: broadcast received shutdown".format(self.self_node.name))
                        exit(0)
                except ValueError:
                    pass
            # Sleep and restart cycle
            sleep(BROADCAST_INTERVAL)
        # self.start_broadcast()

    def create_discovery_message(self, portscan_version=False):
        """
        Create and return discovery message from node info
        """
        if portscan_version:
            message = self.discovery_message_handler.create_portscan_message(self.self_node)
        else:
            message = self.discovery_message_handler.create_message(self.self_node)

        # Convert message to json
        json_message = json.dumps(message.to_discovery_json())

        # Encode message to utf-8 for sending through socket
        encoded_message = json_message.encode()

        return encoded_message

    def send_message(self, message, hub_message, portscan_message):
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
                self.port_scan(portscan_message)
            else:
                # Send message to all known peers
                self.logger.info("Discovery -> Hub + known peers, (hub expired)")
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

    def message_address(self, address):
        encoded_message = self.create_discovery_message()
        self.udp_socket.sendto(encoded_message, address)