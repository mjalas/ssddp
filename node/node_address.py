

class Address(object):
    """

    """
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_address(self):
        return [self.ip, self.port]