import logging
import threading

from app.globals import NodeCommands

DESCRIBE_COMMAND = 'describe'     #   TODO: remove?
DISPLAY_COMMAND = 'display'       #   TODO: remove?
SHUTDOWN_COMMAND = 'shutdown'     #   TODO: remove?

AVAILABLE_COMMANDS = [DESCRIBE_COMMAND, DISPLAY_COMMAND]  #   TODO: remove?


class CommandHandler(threading.Thread):
    """
    Handles commands given in the terminal
    """
    def __init__(self, command, self_node, peer_list, end_parent):
        threading.Thread.__init__(self)
        self._target = self.handle_command
        self.peer_list = peer_list
        self.end_parent = end_parent
        # self.COMMANDS = AVAILABLE_COMMANDS     #   TODO: remove?
        self.received_command = command.split()
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
        self.peer_list.GetAddress(node_name)    # TODO: send description request to address in peer_list

    def end_node(self):
        self.end_parent = True

    COMMANDS = {
        'describe': request_description,
        'display':  display_node_list,
        NodeCommands.SHUTDOWN: end_node,
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
        command_function = self.COMMANDS.get(self.received_command[0])

        if not command_function:
            self.logger.warning("User command \"%s\" not recognized.", self.received_command)
            print("\"%s\" not recognized. Supported commands:", self.received_command[0])
            self.display_commands()
        else:
            self.logger.debug("Handling command \"%s\"", self.received_command)
            command_function(self)

    def run(self):
        # self._target()
        self.handle_command()