"""                     Helping Scripts for Assignment 1
                        S-38.3159 Protocol Design: Aalto University
"""

''' This script provides a udp broadcaster that listens at a specific port, which can be specified by the user
    It broadcasts the incoming messages to all other nodes it is aware of. If a node does not send any message
    for "timeout" interval, it is removed from the list of connected nodes. 
    The hub is created for a localhost address and is meant to be used with nodes at the same host
    Usage: python udp_hub.py -r 8000 -s 5000 -t 30 -v 
'''

'''        
                    Tested with Python 2.7.6 and Ubuntu 14.04  
'''

import argparse
import socket
import time
import select
import logging

local_ip = "localhost"
recv_port = 9000
send_port = 9001
default_timeout = 10


class Node:
    def __init__(self, ip, port, last_seen):
        self.ip = ip
        self.port = port
        self.last_seen = last_seen

    def update_last_seen(self, last_seen):
        self.last_seen = last_seen

    def time_left(self):
        return self.last_seen + default_timeout - time.time()

    def get_address(self):
        return [self.ip, self.port]

    def is_node(self, ip, port):
        return self.ip == ip and self.port == port

    def print_info(self):
        s = "Node %s:%d \t time left to timeout .. %d seconds" % (self.ip, self.port, self.time_left())
        return s


def parse_arguments():
    global recv_port
    global send_port
    global default_timeout

    recv_help = "Receiving Port of the hub -- default: %d " % recv_port
    send_help = "Sending Port of hub -- default: %d " % send_port
    timeout_help = "Timeout value for inactive nodes (in seconds) -- default: %d seconds " % default_timeout

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--recvport", type=int, help=recv_help)
    parser.add_argument("-s", "--sendport", type=int, help=send_help)
    parser.add_argument("-t", "--timeout", type=float, help=timeout_help)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()

    if args.recvport:
        if args.recvport < 1023:
            print("select port greater than 1024")
            exit()
        recv_port = args.recvport
        print("receiving port : ", recv_port)
    else:
        print("No Receiving Port specified, using default :", recv_port)

    if args.sendport:
        if args.sendport < 1023:
            print("select port greater than 1024")
            exit()
        send_port = args.sendport
        print("sending port : ", send_port)
    else:
        print("No Sending Port specified, using default :", send_port)

    if args.timeout:
        if args.timeout <= 0:
            print("timeout should be > 0")
            exit()
        default_timeout = args.timeout
        print("node timeout :", default_timeout)
    else:
        print("No timeout specified, using default : %.2f seconds" % default_timeout)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)


def update_list(ip, port):
    global node_list
    for n in node_list:
        if n.is_node(ip, port):
            logging.debug("Node already exists")
            n.update_last_seen(time.time())
            update_timer()
            return

    new_node = Node(ip, port, time.time())
    print("new entry created for %s:%d" % (ip, port))
    node_list.append(new_node)
    update_timer()


def update_timer():
    global timer
    logging.debug("updating timers")
    for n in node_list:
        node_timeleft = n.time_left()
        if node_timeleft < 0:
            print("time out for node ", n.ip + " :", n.port)
            node_list.remove(n)
            timer = default_timeout
    for n in node_list:
        node_timeleft = n.time_left()
        if node_timeleft < timer:
            timer = node_timeleft
    logging.debug("new timer = %d", timer)


def create_sockets():
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind((local_ip, recv_port))
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.bind((local_ip, send_port))
    return (recv_sock, send_sock)


def broadcast(data, sender):
    logging.debug("Broadcasting to node_list")
    for n in node_list:
        ip, port = n.get_address()
        if sender != (ip, port):
            send_sock.sendto(data, (ip, port))
            logging.debug("broadcast to %s " % n.print_info())


def echo_data(data, sender):
    logging.debug("Echo sent to %s:%d" % (sender[0], sender[1]))
    send_sock.sendto(data, sender)


def print_node_list():
    for n in node_list:
        print(n.print_info())


if __name__ == "__main__":
    parse_arguments()
    [recv_sock, send_sock] = create_sockets()
    node_list = []
    timer = default_timeout
    incoming = [recv_sock]
    outgoing = []
    MTU_SIZE = 1500
    echo_string = "echo"
    print("UDP HUB started \n*** Listening at %s:%d ***" % (local_ip, recv_port))

    while incoming:
        logging.debug("Waiting for the next event --")
        readable = select.select(incoming, outgoing, [], timer)
        if readable[0]:
            [data, addr] = recv_sock.recvfrom(MTU_SIZE);
            logging.debug("received  \n %s \n from %s:%d " % (data, addr[0], addr[1]))
            update_list(addr[0], addr[1])
            print("data is %s" % data.lower())
            if data.lower() == echo_string.lower():
                echo_data(data, addr)
            else:
                broadcast(data, addr)
        else:
            logging.debug("timeout occurred.. updating timer and node_list")
            update_timer()
            logging.debug(print_node_list())