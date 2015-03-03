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
udp_socket = Socket("UDP")
tcp_socket = Socket("TCP")

# Peer list
peer_list = PeerNodeList()

# List of pending outgoing TCP Description requests
description_request_list = DescriptionRequestList()

# Initialize Managers
discovery_manager = DiscoveryMessageManager()
description_manager = DescriptionMessageHandler()
broadcast_manager = DiscoveryBroadcastLoop(discovery_manager, peer_list, udp_socket)
discovery_handler = DiscoveryListener()
description_handler = DescriptionManager(description_manager)
input_manager = None    # Todo

# Start Discovery Loop
broadcast_manager.start_broadcast()    # Todo

input_list = [udp_socket, tcp_socket, sys.stdin]
output_list = [tcp_socket]

while True:

    # listen (select UDP, TCP, STDIN)
    input_ready, output_ready, except_ready = select.select(input_list, output_list, [])

    for x in input_ready:

        if x == udp_socket:
            # UDP -> Discovery Manager
            # (Receiving a UDP Discovery packet)
            discovery_handler.handle_discovery(udp_socket)

        elif x == tcp_socket:
            # TCP -> Description Manager
            # (Receiving a TCP Description Request or Response)
            description_handler.handle_description(tcp_socket, description_request_list)

        elif x == sys.stdin:
            # STDIN -> Input Manager
            input_manager.handle_message(sys.stdin)    # Todo

    for x in output_ready:

        if x == tcp_socket:
            # Outgoing Description Request
            # (Append to Desc)
            description_request_list.append()   # Todo: append message to list