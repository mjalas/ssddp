from node.exceptions.node_exceptions import PeerNodeNotFoundException


class PeerNodeList(object):
    """
    List of discovered peers.
    """
    def __init__(self):
        self.peers = []

    def count(self):
        return len(self.peers)

    def clear(self):
        self.peers.clear()

    def add(self, node):
        self.peers.append(node)

    def display(self):
        """
        Prints every node in the list, their services and service descriptions.
        """
        for peer_node in self.peers:
            node = peer_node.node
            print("NODE [%s] (seen %s)", node.name, peer_node.timestamp)
            for service in node.service_list:
                print(" - SERVICE: %s", service.name)
                if service.description:
                    print("%s", service.description)

    def get(self, node_name):
        for node in self.peers:
            if node.name == node_name:
                return node
        raise PeerNodeNotFoundException("Peer node not found in list")

    def node_in_list(self, node):
        for peer in self.peers:
            if peer is node:
                return True
        return False