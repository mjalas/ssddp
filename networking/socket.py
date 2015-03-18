import logging
import socket
from app.globals import BUFFER_SIZE, TCP_BACKLOG

SOCKET_TYPE = {
    "UDP": socket.SOCK_DGRAM,
    "TCP": socket.SOCK_STREAM,
}


class Socket(object):
    def __init__(self, sock_type, name):
        self.type = sock_type
        self.socket = socket.socket(socket.AF_INET, SOCKET_TYPE[sock_type])
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.logger = logging.getLogger(name + ": " + __name__ + "(" + self.type + ")")
        self.logger.info("Socket initialized")

    def bind(self, port):
        self.logger.debug("Binding to port %d", port)
        self.socket.bind(('', port))

    def listen(self):
        self.logger.debug("Listening to socket")
        self.socket.listen(TCP_BACKLOG)

    def accept(self):
        self.logger.debug("Accepting to socket")
        self.socket.accept()

    def send(self, message):
        if self.type == "TCP":
            self.logger.debug("Sending TCP message")
            self.socket.sendall(message)
        elif self.type == "UDP":
            self.logger.debug("Sending UDP message")
            self.socket.send(message)

    def sendto(self, message, address):
        self.logger.debug("Sending message to [" + str(address[0]) + ", " + str(address[1]) + "]")
        self.socket.sendto(message, address)

    def read(self):
        if self.type == "TCP":
            self.logger.debug("Reading TCP message")
            return self.socket.recv(BUFFER_SIZE)
        elif self.type == "UDP":
            self.logger.debug("Reading UDP message")
            return self.socket.recvfrom(BUFFER_SIZE)

    def terminate(self):
        self.logger.debug("Terminating")
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()