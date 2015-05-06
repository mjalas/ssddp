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
from app.globals import NodeCommand


def is_int(val):
    return isinstance(val, int)


class SSDDP(object):
    def __init__(self, name, external_command_input=None, external_output=None, remote_run=False,
                 service_list_file=None, services=None, debug_mode=True):
        self.name = name

        if isinstance(external_command_input, socket.socket) and external_command_input is not None:
            self.command_input_socket = external_command_input
        elif external_command_input is not None:
            raise TypeError("External command input was not of type socket!")
        else:
            self.command_input_socket = None
        if is_int(external_output):
            self.external_output = external_output

        self.services = services
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
        self.display_debug_message = debug_mode

    def log_debug(self, message):
        if self.display_debug_message:
            self.logger.debug(message)

    def log_info(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)

    def stop(self):
        self.broadcast_loop_queue.put(NodeCommand.SHUTDOWN)
        self.node_manager_queue.put(NodeCommand.SHUTDOWN)
        if self.listening_tcp_socket:
            self.listening_tcp_socket.terminate()
        if self.listening_udp_socket:
            self.listening_udp_socket.terminate()

    def init_sockets(self):
        port = -1
        # Select port and setup sockets
        while True:

            self.listening_tcp_socket = Socket("TCP", self.name)
            self.listening_udp_socket = Socket("UDP", self.name)

            port = random.choice(AVAILABLE_PORTS)

            try:
                self.log_debug('Attempting to bind sockets to port {0}'.format(port))
                self.listening_tcp_socket.bind(port)
                self.listening_udp_socket.bind(port)
                self.listening_tcp_socket.listen()

            except socket.error as error:
                self.log_error('Failed binding to port {0}, ({1}: {2})'.format(port, error.errno, error.strerror))
                self.listening_tcp_socket.terminate()
                self.listening_udp_socket.terminate()
                continue
            except OSError as error:
                self.log_error('Failed binding to port {0}, ({1}: {2})'.format(port, error.errno, error.strerror))
                self.listening_tcp_socket.terminate()
                self.listening_udp_socket.terminate()
                continue

            self.log_info('Sockets bound to port {0}'.format(port))
            break
        return port

    def init_node(self, port):
        # Self node
        self.log_debug("Initializing self node")
        self.address = ("127.0.0.1", port)
        if self.services:
            self.node = Node(self.name, self.address, services=self.services)
        else:
            self.node = Node(self.name, self.address, self.service_list_file)

    def set_name_if_not_set(self, port):
        if not self.name:
            self.name = "Node" + str(port)
            self.listening_tcp_socket.update_logger_name(self.name)
            self.listening_udp_socket.update_logger_name(self.name)
            self.logger = logging.getLogger(self.name + ": " + __name__)
            self.log_info("Unnamed node renamed to \"" + self.name + "\" according to port!")

    def init_input_list(self):
        if self.command_input_socket:
            print("here")
            input_list = [self.listening_udp_socket.socket, self.listening_tcp_socket.socket, self.command_input_socket]
        else:
            input_list = [self.listening_udp_socket.socket, self.listening_tcp_socket.socket, sys.stdin]
        return input_list

    def handle_udp_packet(self, broadcast_manager):
        # UDP -> Discovery Manager
        # (Receiving a UDP Discovery packet)
        self.log_info("Incoming data from UDP Socket.")
        data, address = self.listening_udp_socket.read()
        discovery_handler = DiscoveryListener(data, address, self.node_manager_queue, broadcast_manager,
                                              self.node)
        discovery_handler.start()

    def handle_tcp_packet(self):
        # TCP -> Description Manager
        # (Receiving a TCP Description Request)
        self.log_info("Incoming data from TCP Socket.")
        connection, client_address = self.listening_tcp_socket.socket.accept()
        try:
            description_handler = DescriptionListener(connection, client_address, self.node)
            description_handler.start()
        except IOError as e:
            self.log_error(e.args[0])

    def shutdown(self, end_node):
        print("End Node: " + str(end_node))
        self.log_info("Shutting down node!")
        if self.remote_run:
            print("Node is shutting down!")
        self.stop()
        exit(0)

    def handle_remote_command(self, end_node, peer_list):
        self.log_info("Incoming data from external input.")
        # command = os.read(self.command_input, 32)
        command = self.command_input_socket.recv(BUFFER_SIZE).decode('UTF-8')
        if command == NodeCommand.SHUTDOWN:
            self.command_input_socket.sendall(bytes(NodeCommand.OK, 'UTF-8'))
            self.shutdown(True)
        if self.remote_run:
            print("Received command: " + command)
            self.log_debug("Read command [" + str(command) + "]")
            input_listener = CommandHandler(command, self.node, peer_list, end_node,
                                            self.command_input_socket)
            input_listener.start()

    def start(self):

        # Handle program arguments
        if not self.remote_run:
            ArgumentHandler.handle_arguments()

        # Logging and logs
        logfile = Logfile("logfile.log")
        self.log_info("SSDDP started")

        port = self.init_sockets()

        self.set_name_if_not_set(port)

        self.init_node(port)

        # Peer list
        self.log_debug("Initializing an empty Peer Node List")
        peer_list = PeerNodeList(self.node)

        # Initialize Managers
        self.log_debug("Initializing Discovery message handler")
        discovery_manager = DiscoveryMessageHandler()
        self.log_debug("Initializing Discovery broadcast loop")
        broadcast_manager = DiscoveryBroadcastLoop(discovery_manager, peer_list, self.node, self.broadcast_loop_queue,
                                                   self.listening_udp_socket)

        # Start Discovery Loop
        self.log_debug("Start Discovery Broadcast Loop")
        broadcast_manager.start()

        # Initialize message queue
        self.log_debug("Initializing Message queue")
        # message_queue = Queue()

        # Initialize manager that updates peer node data
        self.log_debug("Initializing Peer Node Manager")
        peer_node_manager = PeerNodeManager(self.node_manager_queue, peer_list, self.node, broadcast_manager)
        self.log_debug("Running Peer Node Manager")
        peer_node_manager.start()

        input_list = self.init_input_list()

        self.log_info("Start listening to sockets and standard input.")
        if self.command_input_socket:
            self.command_input_socket.sendall(bytes("Start listening to sockets and standard input.", 'UTF-8'))

        end_node = False

        while True:

            # listen (select UDP, TCP, STDIN)
            self.log_debug("Select waiting for input...")
            input_ready, output_ready, except_ready = select.select(input_list, [], [])
            self.log_debug("... Select detected input")
            for x in input_ready:
                if end_node:
                    self.shutdown(end_node)

                if x == self.listening_udp_socket.socket:
                    self.handle_udp_packet(broadcast_manager)

                elif x == self.listening_tcp_socket.socket:
                    self.handle_tcp_packet()

                if self.remote_run:
                    if x == self.command_input_socket:
                        self.handle_remote_command(end_node, peer_list)

                else:
                    if x == sys.stdin:  # TODO: handle user command
                        # STDIN -> Input Manager
                        self.log_debug("Incoming data from Standard Input.")
                        command = sys.stdin.readline()

                        self.log_debug("Read command [" + command[:-1] + "]")
                        input_listener = CommandHandler(command, self.node, peer_list, end_node)
                        input_listener.start()
                        # TODO: output response to user inside thread!!
