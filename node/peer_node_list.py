
from node.exceptions.node_exceptions import PeerNodeNotFoundException
from app.globals import NODE_TIMEOUT


class PeerNodeList(object):
    """
    List of discovered peers.
    """

    def __init__(self, self_node, measurer, logger, timeout_duration=NODE_TIMEOUT):
        self.peers = []
        self.self_node = self_node
        self.measurer = measurer
        self.logger = logger
        self.timeout_duration = timeout_duration

    def count(self):
        return len(self.peers)

    def clear(self):
        self.peers.clear()

    def add(self, node):
        message = "{0}: Added '{1}' to peers.".format(self.self_node.name, node.node.name)
        self.logger.info(message)
        self.peers.append(node)
        self.clean_list()

    def display(self):
        """
        Prints every node in the list, their services and service descriptions.
        """
        print("PEER NODE LIST:")
        node_count = 0
        for peer_node in self.peers:
            node = peer_node.node
            node_count += 1
            print("  #" + str(node_count) + ": \"" + str(node.name) + "\" (seen " + str(peer_node.timestamp) + ")")
            for service in node.service_list:
                print("   - SERVICE: " + service.name)
                # TODO: AttributeError: 'dict' object has no attribute 'name'
                # TODO: (happens only after receiving a couple of discovery messages)
                # TODO: (probably peer list update changes service from object to dict)
                # TODO: (OR the service should be dict but it works as object somehow first time)
                if service.description:
                    print((4 * ' ') + service.description.replace('\n', '\n' + (4 * ' ')))

    def node_to_str(self):
        str_list = []
        for i, peer_node in enumerate(self.peers):
            line = "{0}: {1} (seen {2})\n".format(i, peer_node.node.name, peer_node.timestamp)
            str_list.append(line)
            line = "\tServices:\n"
            str_list.append(line)
            for j, service in enumerate(peer_node.node.service_list):
                line = "\t\t{0}: {1}\n".format(j, service.name)
                str_list.append(line)
                if service.description:
                    description = "description: "
                    line = "\t{0}{1}".format(description,
                                             service.description.replace('\n', '\n\t' + (len(description) * '')))
                    str_list.append(line)
        return ''.join(str_list)

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

    def get_node_address(self, node_name):
        peer = self.get(node_name)
        return peer.node.address

    def update_node(self, node_name, message):
        """
        Finds node by name and updates it with the json message contents
        """
        for peer in self.peers:
            if peer.node.name == node_name:
                peer.update_node(message)

    def clean_list(self):
        """
        Clean node list of timed out nodes
        """
        self.logger.info("Cleaning timed out peers from peer list")
        for peer in self.peers:
            # print("Timeout duration: {0}".format(self.timeout_duration))
            if peer.is_timed_out(self.timeout_duration):
                self.measurer.discovered_node_missing(self.self_node.name, peer.node.name)
                self.logger.info("Peer {0} timed out".format(peer.node.name))
                self.peers.remove(peer)
            # else:
                # message = "{0} received discovery message from {1}  '{2}' seconds ago".format(self.self_node.name,
                #                                                                              peer.node.name, peer.diff)
                # print(message)

    def message_list(self, udp_socket, message):
        """
        Sends the message to all known addresses
        Also cleans timed out nodes first
        """
        self.clean_list()
        for peer in self.peers:
            self.logger.info("Discovery -> Known peers, (hub expired)")
            udp_socket.sendto(message, peer.node.address)