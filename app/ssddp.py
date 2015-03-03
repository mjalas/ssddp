import select
import sys
from node.peer_node_list import PeerNodeList
from networking.socket import Socket
from message.description_request_list import DescriptionRequestList
from manager.description_message_handler import DescriptionMessageHandler
from manager.discovery_message_manager import DiscoveryMessageManager
from manager.discovery_broadcast_loop import DiscoveryBroadcastLoop
from manager.discovery_listener import DiscoveryListener
from manager.description_manager import DescriptionManager

# UDP socket & TCP socket
listening_udp_socket = Socket("UDP")
listening_tcp_socket = Socket("TCP")

# Peer list
peer_list = PeerNodeList()

# List of pending outgoing TCP Description requests
description_request_list = DescriptionRequestList()

# Initialize Managers
discovery_manager = DiscoveryMessageManager()
description_manager = DescriptionMessageHandler()
broadcast_manager = DiscoveryBroadcastLoop(discovery_manager, peer_list)
discovery_handler = DiscoveryListener()
description_handler = DescriptionManager(description_manager)
input_manager = None    # Todo

# Start Discovery Loop
broadcast_manager.start_broadcast()    # Todo

input_list = [listening_udp_socket, listening_tcp_socket, sys.stdin]


while True:

    # listen (select UDP, TCP, STDIN)
    input_ready, output_ready, except_ready = select.select(input_list, [], [])

    for x in input_ready:

        if x == listening_udp_socket:
            # TODO: Handle incoming discovery message
            # UDP -> Discovery Manager
            # (Receiving a UDP Discovery packet)
            # discovery_handler.handle_discovery(udp_socket)
            pass

        elif x == listening_tcp_socket:
            # TODO: Create new TCP socket for client to handle the incoming request
            # TODO: -> handle request and send response in own thread/child process
            # TCP -> Description Manager
            # (Receiving a TCP Description Request)
            # description_handler.handle_description(tcp_socket, description_request_list)
            pass

        elif x == sys.stdin:
            # TODO: handle user command (create new socket for sending messages and free it if required)
            # STDIN -> Input Manager
            input_manager.handle_message(sys.stdin)    # Todo
