import socket
from app.globals import BUFFER_SIZE, TCP_BACKLOG

SOCKET_TYPE = {
    "UDP": socket.SOCK_DGRAM,
    "TCP": socket.SOCK_STREAM,
}


class Socket(object):
    def __init__(self, sock_type):
        self.type = sock_type
        self.socket = socket.socket(socket.AF_INET, SOCKET_TYPE[sock_type])
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def bind(self, port):
        self.socket.bind(('', port))

    def listen(self):
        self.socket.listen(TCP_BACKLOG)

    def accept(self):
        self.socket.accept()

    def send(self, message):
        if self.type == "TCP":
            self.socket.sendall(message)
        elif self.type == "UDP":
            self.socket.send(message)

    def sendto(self, message, address):
        self.socket.sendto(message, address)

    def read(self):
        if self.type == "TCP":
            return self.socket.recv(BUFFER_SIZE)
        elif self.type == "UDP":
            return self.socket.recvfrom(BUFFER_SIZE)

    def terminate(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()