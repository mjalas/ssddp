from threading import Thread
import sys

from app.ssddp import SSDDP
from protocol_testing.main_argument_handler import MainArgumentHandler
from protocol_testing.tester_config_handler import TesterConfigHandler
from protocol_testing.config_test_file import ConfigurationNode

from enum import Enum


class CommandType(Enum):
    exit = 1


class CommandHandler(object):
    """

    """
    def __init__(self):
        pass

    def handle_input(self, input):
        if input == "exit" or input == "quit":
            return CommandType.exit

    def usage(self):
        print("To exit test use: 'exit', 'quit'")

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
    for name in names:
        node = SSDDP(name)
        thread = Thread(target=node.start())
        #thread.start()

    print("Test setup complete.")
    command_handler = CommandHandler()
    for line in sys.stdin:
        command = command_handler.handle_input(line.strip())
        if command == CommandType.exit:
            print("Ending test!")
            exit()
        print(line)


