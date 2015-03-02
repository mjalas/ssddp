from socket import socket
import select
import sys
from node.peer_node_list import PeerNodeList

# UDP socket & TCP socket
udp_socket = Create_UDP_Socket()    # Todo
tcp_socket = Create_TCP_Socket()    # Todo

# Peer list
peer_list = PeerNodeList()

# Start Discovery Loop
Start_Discovery_Loop(peer_list, udp_socket)    # Todo

input_list = [udp_socket, tcp_socket, sys.stdin]

while True:

    # listen (select UDP, TCP, STDIN)
    input_ready, output_ready, except_ready = select.select(input_list, [], [])

    for x in input_ready:

        if x == udp_socket:
            # UDP -> Discovery Manager
            discovery_manager(udp_socket)    # Todo

        elif x == tcp_socket:
            # TCP -> Description Manager
            description_manager(tcp_socket)    # Todo

        elif x == sys.stdin:
            # STDIN -> Input Manager
            input_manager(sys.stdin)    # Todo
