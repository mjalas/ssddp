from threading import Thread
import sys
import os
import socket

import getopt
from sys import argv, exit

from enum import Enum

from app.ssddp import SSDDP
from protocol_testing.main_argument_handler import MainArgumentHandler
from protocol_testing.tester_config_handler import TesterConfigHandler
from protocol_testing.config_test_file import ConfigurationNode
from manager.command_handler import DESCRIBE_COMMAND, DISPLAY_COMMAND


class CommandType(Enum):
    exit = 1


class TestCommandHandler(object):
    """

    """

    def __init__(self):
        self.command_list = [DESCRIBE_COMMAND, DISPLAY_COMMAND]

    def handle_input(self, input_line):

        if input == "exit" or input == "quit":
            return CommandType.exit


    def usage(self):
        print("Type cmd --help to get list of commands.")
        print("To end test use: 'exit' or 'quit'")


def node_process(ssddp_node):
    if not isinstance(ssddp_node, SSDDP):
        exit(0)
    ssddp_node.start()


if __name__ == "__main__":
    print("Setting up test.")
    argument_handler = MainArgumentHandler()
    file = argument_handler.handle_arguments()
    if not file:
        print("No configuration file was given.")
        exit()
    try:
        config_handler = TesterConfigHandler(file)
    except FileNotFoundError:
        print("Configuration file not found! Please check that file exists or path is correct!")
        exit()
    names = ConfigurationNode.get_names_from_node_list(config_handler.test_configuration.nodes)
    if names is None:
        exit()

    # pipes = {}
    sockets = {}
    for name in names:
        # pipein, pipeout = os.pipe()
        (child, parent) = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        if os.fork() == 0:
            # ssddp_node = SSDDP(name, pipeout)
            ssddp_node = SSDDP(name, child)
            ssddp_node.start()
            exit()
        else:
            # pipes[name] = pipein
            sockets[name] = parent
            continue

    print("Test setup complete.")
    command_handler = TestCommandHandler()
    command_handler.usage()
    for line in sys.stdin:
        command = command_handler.handle_input(line.strip())
        if command == CommandType.exit:
            print("Ending test!")
            exit()
        print(line)


