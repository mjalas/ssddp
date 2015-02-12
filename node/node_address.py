

class Address(object):
    """

    """
    def __init__(self, ip, udp_port, tcp_port):
        self.ip = ip
        self.udp_port = udp_port
        self.tcp_port = tcp_port

    def get_tcp_address(self):
        return [self.ip, self.tcp_port]

    def get_udp_address(self):
        return [self.ip, self.udp_port]