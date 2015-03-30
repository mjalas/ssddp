import logging
import threading

DESCRIBE_COMMAND = 'describe'
DISPLAY_COMMAND = 'display'
SHUTDOWN_COMMAND = 'shutdown'

AVAILABLE_COMMANDS = [DESCRIBE_COMMAND, DISPLAY_COMMAND]


class CommandHandler(threading.Thread):
    """
    Handles commands given in the terminal
    """
    def __init__(self, command, self_node, peer_list, end_parent):
        threading.Thread.__init__(self)
        self._target = self.handle_command
        self.peer_list = peer_list
        self.end_parent = end_parent
        self.COMMANDS = AVAILABLE_COMMANDS
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
        if len(self.command) != 2:
            print("Wrong argument count! Expected \"describe node_name\".")
            return
        node_name = self.command[1]
        self.peer_list.GetAddress(node_name)    # TODO: send description request to address in peer_list


    COMMANDS = {
        'describe': request_description,
        'display':  display_node_list,
    }


    def call_command_func(self, command):
        if command is DESCRIBE_COMMAND:
            self.logger.debug("Handling command \"%s\"", self.command)
            self.request_description()
        elif command is DISPLAY_COMMAND:
            self.logger.debug("Handling command \"%s\"", self.command)
            self.display_node_list()
        elif command is SHUTDOWN_COMMAND:
            self.end_parent = True
            return
        else:
            self.logger.warning("User command \"%s\" not recognized.", self.command)
            print("\"%s\" not recognized. Supported commands:", self.command[0])
            self.display_commands()

    def display_commands(self):
        for cmd in self.COMMANDS:
            print("%s", cmd)

    def handle_command(self):
        command = self.COMMANDS.get(self.command[0])
        if not command:
            self.logger.warning("User command \"%s\" not recognized.", self.command)
            print("\"%s\" not recognized. Supported commands:", self.command[0])
            self.display_commands()
        else:
            self.logger.debug("Handling command \"%s\"", self.command)
            command(self)


    def run(self):
        # self._target()
        self.handle_command()