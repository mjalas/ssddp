import select
import sys
from node.peer_node_list import PeerNodeList
from networking.socket import Socket
from message.description_request_list import DescriptionRequestList

# UDP socket & TCP socket
udp_socket = Socket("UDP")
tcp_socket = Socket("TCP")

# Peer list
peer_list = PeerNodeList()

# List of pending outgoing TCP Description requests
description_request_list = DescriptionRequestList()

# Start Discovery Loop
Start_Discovery_Loop(peer_list, udp_socket)    # Todo

input_list = [udp_socket, tcp_socket, sys.stdin]
output_list = [tcp_socket]

while True:

    # listen (select UDP, TCP, STDIN)
    input_ready, output_ready, except_ready = select.select(input_list, output_list, [])

    for x in input_ready:

        if x == udp_socket:
            # UDP -> Discovery Manager
            # (Receiving a UDP Discovery packet)
            discovery_manager(udp_socket)    # Todo

        elif x == tcp_socket:
            # TCP -> Description Manager
            # (Receiving a TCP Description Request or Response)
            description_manager(tcp_socket, description_request_list)    # Todo

        elif x == sys.stdin:
            # STDIN -> Input Manager
            input_manager(sys.stdin)    # Todo

    for x in output_ready:

        if x == tcp_socket:
            # Outgoing Description Request
            # (Append to Desc)
            description_request_list.append()   # Todo: append message to list