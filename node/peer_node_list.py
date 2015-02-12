

class PeerNodeList(object):
    """

    """
    def __init__(self):
        self.peers = []

    def get_count(self):
        return len(self.peers)

    def clear(self):
        self.peers.clear()

    def add(self, node):
        self.peers.append(node)