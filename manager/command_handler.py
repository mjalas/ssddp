import logging
import threading
import json

from app.globals import NodeCommand
from node.node import NodeEncoder
from message.message import Message
from message.message_types import MessageType
from message.timestamp import Timestamp
from networking.socket import Socket

DESCRIBE_COMMAND = 'describe'     #   TODO: remove?
DISPLAY_COMMAND = 'display'       #   TODO: remove?
SHUTDOWN_COMMAND = 'shutdown'     #   TODO: remove?

AVAILABLE_COMMANDS = [DESCRIBE_COMMAND, DISPLAY_COMMAND]  #   TODO: remove?


class CommandHandler(threading.Thread):
    """
    Handles commands given in the terminal
    """
    def __init__(self, command, self_node, peer_list, end_parent, remote_socket=None):
        threading.Thread.__init__(self)
        self._target = self.handle_command
        self.node = self_node
        self.peer_list = peer_list
        self.end_parent = end_parent
        # self.COMMANDS = AVAILABLE_COMMANDS     #   TODO: remove?
        self.received_command = command.split()
        self.output_socket = Socket("TCP", self.node.name)
        self.remote_socket = remote_socket
        self.logger = logging.getLogger(self_node.name + ": " + __name__)
        self.logger.info("Discovery Listener initialized")

    def display_node_list(self):
        """
        Displays all detected nodes, their services and service descriptions.
        """
        self.peer_list.display()

    def request_description(self):
        """
        Request description of a node's services.
        Expects name of the node.

        """
        if len(self.received_command) != 2:
            print("Wrong argument count! Expected \"describe node_name\".")
            return
        node_name = self.received_command[1]
        address = self.peer_list.get_node_address(node_name)    # TODO: send description request to address in peer_list
        self.logger.info("Sending description request to "+str(address))
        # Create message and send it.
        message = Message(MessageType.description_request, node_name, address, Timestamp.create_timestamp())
        data = message.to_json()
        data_str = json.dumps(data)
        self.output_socket.connect(address[0], address[1])
        self.output_socket.send(bytes(data_str, 'UTF-8'))
        response = self.output_socket.read()
        response_str = response.decode('UTF-8')
        if self.remote_socket:
            self.remote_socket.sendall(response)
        else:
            print(response_str)
        #message = Message.to_object(response_str)

        return None

    def end_node(self):
        self.end_parent = True
        return None

    def display_node(self):
        obj = {'name': self.node.name, 'address': self.node.address, 'services': self.node.service_list}
        if self.remote_socket:
            output = json.dumps(obj, indent=4, separators=(',', ': '))
            self.remote_socket.sendall(bytes(output, 'UTF-8'))

    def display_peers(self):
        peers = {}
        for peer in self.peer_list.peers:
            peers[peer.node.name] = peer.node
        if self.remote_socket:
            output = json.dumps(peers, cls=NodeEncoder, indent=4, separators=(',', ': '))
            self.remote_socket.sendall(bytes(output, 'UTF-8'))

    COMMANDS = {
        NodeCommand.DESCRIBE: request_description,
        NodeCommand.DISPLAY:  display_node_list,
        NodeCommand.SHUTDOWN: end_node,
        NodeCommand.DISPLAY_NODE: display_node,
        NodeCommand.PEERS: display_peers,
    }

    def call_command_func(self, command):
        if command is DESCRIBE_COMMAND:
            self.logger.debug("Handling command \"%s\"", self.received_command)
            self.request_description()
        elif command is DISPLAY_COMMAND:
            self.logger.debug("Handling command \"%s\"", self.received_command)
            self.display_node_list()
        elif command is SHUTDOWN_COMMAND:
            self.end_parent = True
            return
        else:
            self.logger.warning("User command \"%s\" not recognized.", self.received_command)
            print("\"%s\" not recognized. Supported commands:", self.received_command[0])
            self.display_commands()

    def display_commands(self):
        for cmd in self.COMMANDS:
            print("%s", cmd)

    def handle_command(self):
        # command_function = self.COMMANDS[self.received_command[0]]
        if len(self.received_command) > 0:
            command_function = self.COMMANDS.get(self.received_command[0])

            if not command_function:
                self.logger.warning("User command \"%s\" not recognized.", self.received_command)
                print("\"%s\" not recognized. Supported commands:", self.received_command[0])
                self.display_commands()

            else:
                self.logger.debug("Handling command \"%s\"", self.received_command)
                output = command_function(self)
                return output

        return None

    def run(self):
        # self._target()
        self.handle_command()