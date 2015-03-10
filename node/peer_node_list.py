

class PeerNodeList(object):
    """

    """
    def __init__(self):
        self.peers = []

    def count(self):
        return len(self.peers)

    def clear(self):
        self.peers.clear()

    def add(self, node):
        self.peers.append(node)

    def get(self, node_name):
        return (node for node in self.peers if node.name == node_name)