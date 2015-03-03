import select
import sys
from node import peer_node
from node.peer_node import PeerNode
from node.peer_node_list import PeerNodeList
from networking.socket import Socket
from message.description_request_list import DescriptionRequestList
from manager.description_message_handler import DescriptionMessageHandler
from manager.discovery_message_handler import DiscoveryMessageManager
from manager.discovery_broadcast_loop import DiscoveryBroadcastLoop
from manager.discovery_listener import DiscoveryListener
from manager.description_manager import DescriptionManager
from app.globals import TCP_LISTENING_PORT
from app.globals import UDP_LISTENING_PORT


# Self node
self_node = PeerNode()

# Peer list
peer_list = PeerNodeList()

# List of pending outgoing TCP Description requests
description_request_list = DescriptionRequestList()

# Initialize Managers
discovery_manager = DiscoveryMessageManager()
description_message_handler = DescriptionMessageHandler()
broadcast_manager = DiscoveryBroadcastLoop(discovery_manager, peer_list)
discovery_handler = DiscoveryListener()
description_handler = DescriptionManager(description_message_handler)
input_manager = None    # Todo

# Start Discovery Loop
broadcast_manager.start_broadcast()    # Todo

# Listening UDP and TCP socket setup
listening_udp_socket = Socket("UDP")
listening_udp_socket.socket.bind(('', UDP_LISTENING_PORT))

listening_tcp_socket = Socket("TCP")
listening_tcp_socket.socket.bind(('', TCP_LISTENING_PORT))
listening_tcp_socket.socket.listen(5)

input_list = [listening_udp_socket.socket, listening_tcp_socket.socket, sys.stdin]


while True:

    # listen (select UDP, TCP, STDIN)
    input_ready, output_ready, except_ready = select.select(input_list, [], [])

    for x in input_ready:

        if x == listening_udp_socket.socket:
            # TODO: Handle incoming discovery message
            # UDP -> Discovery Manager
            # (Receiving a UDP Discovery packet)
            # discovery_handler.handle_discovery(udp_socket)
            pass

        elif x == listening_tcp_socket.socket:
            # TODO: Create new TCP socket for client to handle the incoming request
            # TODO: -> handle request and send response in own thread/child process
            # TCP -> Description Manager
            # (Receiving a TCP Description Request)
            connection, client_address = listening_tcp_socket.socket.accept()
            description_handler.handle_description(connection, description_request_list)
            pass

        elif x == sys.stdin:
            # TODO: handle user command (create new socket for sending messages and free it if required)
            # STDIN -> Input Manager
            input_manager.handle_message(sys.stdin)    # Todo
