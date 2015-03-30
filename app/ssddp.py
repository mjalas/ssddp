import random
import select
import socket
import sys
import os
from queue import Queue
import logging

from app.argument_handler import ArgumentHandler
from app.globals import AVAILABLE_PORTS, BUFFER_SIZE
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
from app.globals import NodeCommands


def is_int(val):
    return isinstance(val, int)


class SSDDP(object):
    def __init__(self, name, external_command_input=None, external_output=None, remote_run=False, service_list_file=None):
        self.name = name

        if isinstance(external_command_input, socket.socket) and external_command_input is not None:
            self.command_input_socket = external_command_input
        elif external_command_input is not None:
            raise TypeError("External command input was not of type socket!")
        else:
            self.command_input_socket = None
        if is_int(external_output):
            self.external_output = external_output

        self.service_list_file = service_list_file
        self.node_manager_queue = Queue()
        self.broadcast_loop_queue = Queue()
        self.remote_run = remote_run
        self.listening_tcp_socket = None
        self.listening_udp_socket = None
        self.address = None
        self.node = None
        if not self.name:
            self.logger = logging.getLogger("UnnamedNode: " + __name__)
        else:
            self.logger = logging.getLogger(self.name + ": " + __name__)

    def stop(self):
        self.broadcast_loop_queue.put(NodeCommands.SHUTDOWN)
        self.node_manager_queue.put(NodeCommands.SHUTDOWN)
        if self.listening_tcp_socket:
            self.listening_tcp_socket.terminate()
        if self.listening_udp_socket:
            self.listening_udp_socket.terminate()

    def start(self):

        # Handle program arguments
        if not self.remote_run:
            ArgumentHandler.handle_arguments()

        # Logging and logs
        logfile = Logfile("logfile.log")
        self.logger.info("SSDDP started")

        # Select port and setup sockets
        while True:

            self.listening_tcp_socket = Socket("TCP", self.name)
            self.listening_udp_socket = Socket("UDP", self.name)

            port = random.choice(AVAILABLE_PORTS)

            try:
                self.logger.debug('Attempting to bind sockets to port %d', port)
                self.listening_tcp_socket.bind(port)
                self.listening_udp_socket.bind(port)
                self.listening_tcp_socket.listen()

            except socket.error as error:
                self.logger.error('Failed binding to port %d, (%d: %s)', port, error.errno, error.strerror)
                self.listening_tcp_socket.terminate()
                self.listening_udp_socket.terminate()
                continue

            self.logger.info('Sockets bound to port %d', port)
            break

        if not self.name:
            self.name = "Node"+str(port)
            self.listening_tcp_socket.update_logger_name(self.name)
            self.listening_udp_socket.update_logger_name(self.name)
            self.logger = logging.getLogger(self.name + ": " + __name__)
            self.logger.info("Unnamed node renamed to \"" + self.name + "\" according to port!")

        # Self node
        self.logger.debug("Initializing self node")
        self.address = ("127.0.0.1", port)
        self.node = Node(self.name, self.address, self.service_list_file)

        # Peer list
        self.logger.debug("Initializing an empty Peer Node List")
        peer_list = PeerNodeList()

        # Initialize Managers
        self.logger.debug("Initializing Discovery message handler")
        discovery_manager = DiscoveryMessageHandler()
        self.logger.debug("Initializing Discovery broadcast loop")
        broadcast_manager = DiscoveryBroadcastLoop(discovery_manager, peer_list, self.node, self.broadcast_loop_queue)

        # Start Discovery Loop
        self.logger.debug("Start Discovery Broadcast Loop")
        broadcast_manager.start()

        # Initialize message queue
        self.logger.debug("Initializing Message queue")
        # message_queue = Queue()

        # Initialize manager that updates peer node data
        self.logger.debug("Initializing Peer Node Manager")
        peer_node_manager = PeerNodeManager(self.node_manager_queue, peer_list)
        self.logger.debug("Running Peer Node Manager")
        peer_node_manager.start()

        if self.command_input_socket:
            print("here")
            input_list = [self.listening_udp_socket.socket, self.listening_tcp_socket.socket, self.command_input_socket]
        else:
            input_list = [self.listening_udp_socket.socket, self.listening_tcp_socket.socket, sys.stdin]

        self.logger.info("Start listening to sockets and standard input.")
        if self.command_input_socket:
            self.command_input_socket.sendall(bytes("Start listening to sockets and standard input.", 'UTF-8'))

        end_node = False

        while True:

            # listen (select UDP, TCP, STDIN)
            self.logger.debug("Select waiting for input...")
            input_ready, output_ready, except_ready = select.select(input_list, [], [])
            self.logger.debug("... Select detected input")
            for x in input_ready:
                if end_node:
                    print("End Node: " + str(end_node))
                    self.logger.info("Shutting down node!")
                    if self.remote_run:
                        print("Node is shutting down!")
                    exit(0)

                if x == self.listening_udp_socket.socket:
                    # UDP -> Discovery Manager
                    # (Receiving a UDP Discovery packet)
                    self.logger.info("Incoming data from UDP Socket.")
                    data, address = self.listening_udp_socket.read()
                    discovery_handler = DiscoveryListener(data, address, self.node_manager_queue, broadcast_manager,
                                                          self.node)
                    discovery_handler.start()

                elif x == self.listening_tcp_socket.socket:
                    # TCP -> Description Manager
                    # (Receiving a TCP Description Request)
                    self.logger.info("Incoming data from TCP Socket.")
                    connection, client_address = self.listening_tcp_socket.socket.accept()
                    try:
                        description_handler = DescriptionListener(connection, client_address, self.node)
                        description_handler.start()
                    except IOError as e:
                        self.logger.error(e.args[0])
                if self.remote_run:
                    if x == self.command_input_socket:
                        self.logger.info("Incoming data from external input.")
                        # command = os.read(self.command_input, 32)
                        command = self.command_input_socket.recv(BUFFER_SIZE).decode('UTF-8')
                        if command == NodeCommands.SHUTDOWN:
                            end_node = True
                            self.command_input_socket.sendall(bytes(NodeCommands.OK, 'UTF-8'))
                            continue
                        if self.remote_run:
                            print("Received command: " + command)
                            self.logger.debug("Read command [" + str(command) + "]")
                            input_listener = CommandHandler(command, self.node, peer_list, end_node)
                            input_listener.start()
                else:
                    if x == sys.stdin:  # TODO: handle user command
                        # STDIN -> Input Manager
                        self.logger.debug("Incoming data from Standard Input.")
                        command = sys.stdin.readline()

                        self.logger.debug("Read command [" + command[:-1] + "]")
                        input_listener = CommandHandler(command, self.node, peer_list, end_node)
                        input_listener.start()
                        # TODO: output response to user inside thread!!
