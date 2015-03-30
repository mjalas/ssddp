import logging
import threading


class CommandHandler(threading.Thread):
    """
    Handles commands given in the terminal
    """
    def __init__(self, command, self_node, peer_list):
        threading.Thread.__init__(self)
        self._target = self.handle_command
        self.peer_list = peer_list
        self.command = command.split()
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
        node_name = self.command[1]
        self.peer_list.GetAddress(node_name)    # TODO: send description request to address in peer_list

    COMMANDS = {
        'describe': request_description(),
        'display':  display_node_list(),
    }

    def handle_command(self):
        command = self.COMMANDS.get(self.command[0])
        if not command:
            self.logger.warning("User command \"%s\" not recognized.", self.command)
            print("\"%s\" not recognized. Supported commands:", self.command[0])
            for cmd in self.COMMANDS:
                print("\"%s\"", cmd)
        else:
            self.logger.debug("Handling command \"%s\"", self.command)
            command()

    def run(self):
        # self._target()
        self.handle_command()