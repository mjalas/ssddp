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
        print("PEER NODE LIST:")
        node_count = 0
        for peer_node in self.peers:
            node = peer_node.node
            node_count += 1
            print("#" + str(node_count) + ": \"" + node.name + "\" (seen " + peer_node.timestamp+")")
            for service in node.service_list.services:
                print(" - SERVICE: " + service.name)
                if service.description:
                    print(service.description)

    def get(self, node_name):
        for peer in self.peers:
            if peer.node.name == node_name:
                return peer
        raise PeerNodeNotFoundException("Peer node not found in list")

    def node_in_list(self, node):
        for peer in self.peers:
            if peer is node:
                return True
        return False