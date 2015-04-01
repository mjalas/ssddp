import logging
import random
import socket
from app.globals import BUFFER_SIZE, TCP_BACKLOG, PACKET_DROP_RATE

SOCKET_TYPE = {
    "UDP": socket.SOCK_DGRAM,
    "TCP": socket.SOCK_STREAM,
}


class Socket(object):
    def __init__(self, sock_type, name):
        self.type = sock_type
        self.socket = socket.socket(socket.AF_INET, SOCKET_TYPE[sock_type])
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if name:
            self.logger = logging.getLogger(name + ": " + __name__ + "(" + self.type + ")")
        else:
            self.logger = logging.getLogger("UnnamedNode: " + __name__ + "(" + self.type + ")")
        self.logger.info("Socket initialized")

    def update_logger_name(self, name):
        self.logger = logging.getLogger(name + ": " + __name__ + "(" + self.type + ")")

    def bind(self, port):
        self.logger.debug("Binding to port %d", port)
        self.socket.bind(('', port))

    def listen(self):
        self.logger.debug("Listening to socket")
        self.socket.listen(TCP_BACKLOG)

    def accept(self):
        self.logger.debug("Accepting to socket")
        self.socket.accept()

    def connect(self, address, port):
        self.logger.debug("Connecting to {0}:{1}".format(address, port))
        self.socket.connect((address, port))

    def send(self, message):
        if random.random() > PACKET_DROP_RATE:
            if self.type == "TCP":
                self.logger.debug("Sending TCP message: "+str(message))
                self.socket.sendall(message)
            elif self.type == "UDP":
                self.logger.debug("Sending UDP message")
                self.socket.send(message)
        else:
            self.logger.debug("Packet dropped (Packet drop rate: "+str(PACKET_DROP_RATE)+")")

    def sendto(self, message, address):
        # Log message disabled for now to avoid 1000x message spam
        # self.logger.debug("Sending message to [" + str(address[0]) + ", " + str(address[1]) + "]")
        if random.random() > PACKET_DROP_RATE:
            try:
                self.socket.sendto(message, address)
            except BrokenPipeError as e:
                self.logger.debug("Tried to send {0} to {1} and got {2}".format(message, address, e.args))

        else:
            self.logger.debug("Packet dropped (Packet drop rate: "+str(PACKET_DROP_RATE)+")")

    def read(self):
        if self.type == "TCP":
            self.logger.debug("Reading TCP message")
            return self.socket.recv(BUFFER_SIZE)
        elif self.type == "UDP":
            self.logger.debug("Reading UDP message")
            return self.socket.recvfrom(BUFFER_SIZE)

    def terminate(self):
        try:
            self.logger.debug("Terminating")
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except OSError as error:
            self.logger.debug("{0}: {1}".format(error.errno, error.args))