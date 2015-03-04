import select
import sys
from app.argument_handler import ArgumentHandler
from queue import Queue
from app.logfile import Logfile
from node import peer_node
from node.peer_node import PeerNode
from node.peer_node_list import PeerNodeList
from node.peer_node_manager import PeerNodeManager
from networking.socket import Socket
from message.description_request_list import DescriptionRequestList
from manager.description_message_handler import DescriptionMessageHandler
from manager.discovery_message_handler import DiscoveryMessageHandler
from manager.discovery_broadcast_loop import DiscoveryBroadcastLoop
from manager.discovery_listener import DiscoveryListener
from manager.description_listener import DescriptionListener
from manager.command_listener import CommandListener
from app.globals import TCP_LISTENING_PORT
from app.globals import UDP_LISTENING_PORT
from app.globals import BUFFER_SIZE
import logging; log = logging.getLogger(__name__)


class SSDDP(object):

    def __init__(self):
        pass

    @staticmethod
    def start():

        # Handle program arguments
        ArgumentHandler()

        # Logging and logs
        logfile = Logfile("logfile.log")
        log.info("SSDDP started")

        # Self node
        self_node = PeerNode()

        # Peer list
        peer_list = PeerNodeList()

        # Hub address ( todo: get from arguments or something)
        hub_address = ("127.0.0.1", 5678)

        # Initialize Managers
        discovery_manager = DiscoveryMessageHandler()
        broadcast_manager = DiscoveryBroadcastLoop(discovery_manager, peer_list, hub_address)

        input_manager = None  # Todo

        # Start Discovery Loop
        broadcast_manager.start_broadcast()  # Todo

        # Listening UDP and TCP socket setup
        listening_udp_socket = Socket("UDP")
        listening_udp_socket.bind(UDP_LISTENING_PORT)

        listening_tcp_socket = Socket("TCP")
        listening_tcp_socket.bind(TCP_LISTENING_PORT)
        listening_tcp_socket.listen(5)

        # Initialize message queue
        message_queue = Queue()

        # Initialize manager that updates peer node data
        peer_node_manager = PeerNodeManager(message_queue, peer_list)
        peer_node_manager.run()

        input_list = [listening_udp_socket.socket, listening_tcp_socket.socket, sys.stdin]

        while True:

            # listen (select UDP, TCP, STDIN)
            input_ready, output_ready, except_ready = select.select(input_list, [], [])

            for x in input_ready:

                if x == listening_udp_socket.socket:
                    # UDP -> Discovery Manager
                    # (Receiving a UDP Discovery packet)
                    data, address = listening_udp_socket.socket.recv(BUFFER_SIZE)
                    discovery_handler = DiscoveryListener(data, address, message_queue)
                    discovery_handler.run()

                elif x == listening_tcp_socket.socket:
                    # TCP -> Description Manager
                    # (Receiving a TCP Description Request)
                    connection, client_address = listening_tcp_socket.socket.accept()
                    description_handler = DescriptionListener(connection, client_address)
                    description_handler.run()

                elif x == sys.stdin:  # TODO: handle user command (create new socket for sending messages and free it if required)
                    # STDIN -> Input Manager
                    command = sys.stdin.read(1024)
                    input_listener = CommandListener(command)
                    input_listener.run()
                    # TODO: output response to user inside thread!!

if __name__ == "__main__":
    SSDDP.start()
