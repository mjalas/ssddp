import random
import select
import socket
import sys
from queue import Queue
import logging

from app.argument_handler import ArgumentHandler
from app.globals import AVAILABLE_PORTS
from app.logfile import Logfile
from node.node import Node
# from node.peer_node import PeerNode
from node.peer_node_list import PeerNodeList
from node.peer_node_manager import PeerNodeManager
from networking.socket import Socket
from message.discovery_message_handler import DiscoveryMessageHandler
from manager.discovery_broadcast_loop import DiscoveryBroadcastLoop
from manager.discovery_listener import DiscoveryListener
from manager.description_listener import DescriptionListener
from manager.command_handler import CommandHandler


class SSDDP(object):
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(self.name + ": " + __name__)


    def start(self):

        # Handle program arguments
        ArgumentHandler.handle_arguments()

        # Logging and logs
        logfile = Logfile("logfile.log")
        self.logger.info("SSDDP started")

        # Select port and setup sockets
        while True:

            listening_tcp_socket = Socket("TCP", self.name)
            listening_udp_socket = Socket("UDP", self.name)

            port = random.choice(AVAILABLE_PORTS)

            try:
                self.logger.debug('Attempting to bind sockets to port %d', port)
                listening_tcp_socket.bind(port)
                listening_udp_socket.bind(port)
                listening_tcp_socket.listen()

            except socket.error as error:
                self.logger.error('Failed binding to port %d, (%d: %s)', port, error.errno, error.strerror)
                listening_tcp_socket.terminate()
                listening_udp_socket.terminate()
                continue

            self.logger.info('Sockets bound to port %d', port)
            break

        # Self node
        self.logger.debug("Initializing self node")
        self_address = ("127.0.0.1", port)
        self_node = Node(self.name, self_address)

        # Peer list
        self.logger.debug("Initializing an empty Peer Node List")
        peer_list = PeerNodeList()

        # Initialize Managers
        self.logger.debug("Initializing Discovery message handler")
        discovery_manager = DiscoveryMessageHandler()
        self.logger.debug("Initializing Discovery broadcast loop")
        broadcast_manager = DiscoveryBroadcastLoop(discovery_manager, peer_list, self_node)

        # Start Discovery Loop
        self.logger.debug("Start Discovery Broadcast Loop")
        broadcast_manager.start()

        # Initialize message queue
        self.logger.debug("Initializing Message queue")
        message_queue = Queue()

        # Initialize manager that updates peer node data
        self.logger.debug("Initializing Peer Node Manager")
        peer_node_manager = PeerNodeManager(message_queue, peer_list)
        self.logger.debug("Running Peer Node Manager")
        peer_node_manager.start()

        input_list = [listening_udp_socket.socket, listening_tcp_socket.socket, sys.stdin]
        self.logger.info("Start listening to sockets and stdin.")

        while True:

            # listen (select UDP, TCP, STDIN)
            self.logger.debug("Select waiting for input...")
            input_ready, output_ready, except_ready = select.select(input_list, [], [])
            self.logger.debug("... Select detected input")
            for x in input_ready:

                if x == listening_udp_socket.socket:
                    # UDP -> Discovery Manager
                    # (Receiving a UDP Discovery packet)
                    self.logger.info("Incoming data from UDP Socket.")
                    data, address = listening_udp_socket.read()
                    discovery_handler = DiscoveryListener(data, address, message_queue, broadcast_manager, self_node)
                    discovery_handler.start()

                elif x == listening_tcp_socket.socket:
                    # TCP -> Description Manager
                    # (Receiving a TCP Description Request)
                    self.logger.info("Incoming data from TCP Socket.")
                    connection, client_address = listening_tcp_socket.socket.accept()
                    try:
                        description_handler = DescriptionListener(connection, client_address, self_node)
                        description_handler.start()
                    except IOError as e:
                        self.logger.error(e.args[0])

                elif x == sys.stdin:  # TODO: handle user command (create new socket for sending messages and free it if required)
                    # STDIN -> Input Manager
                    self.logger.info("Incoming data from Standard Input.")
                    command = sys.stdin.readline()
                    self.logger.debug("Read command [" + command + "]")
                    input_listener = CommandHandler(command, self_node)
                    input_listener.start()
                    # TODO: output response to user inside thread!!



