import socket
from app.globals import BUFFER_SIZE

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

    def listen(self, backlog):
        self.socket.listen(backlog)

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
        return self.socket.recv(BUFFER_SIZE)