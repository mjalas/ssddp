import sys
import os
import socket
import select
import time
import json
from datetime import datetime
from sys import argv, exit
import logging

from app.ssddp import SSDDP
from protocol_testing.main_argument_handler import MainArgumentHandler
from protocol_testing.tester_config_handler import TesterConfigHandler
from app.globals import NodeCommand
from protocol_testing.node_process_cleanup import NodeProcessCleanUp


TEST_BUFFER_SIZE = 1024
AVAILABLE_CMD_PARAMETERS = [NodeCommand.DESCRIBE, NodeCommand.DISPLAY, NodeCommand.HELP]


class NodeCreationType():
    SUCCESS = "success"
    FAILED = "failed"


class TestPrinter(object):
    """
    """
    def __init__(self, log_file="protocol_test.log"):
        self.log_file = log_file

    def log(self, message, append=True):
        mode = 'w'
        if append:
            mode = 'a'

        with open(self.log_file, mode) as f:
            tmp = str(datetime.now()) + ": " + message
            f.write(tmp)
            f.flush()

    def display(self, message, log=False):
        if log:
            self.log(message)
        print(message)


class ProtocolTester(object):
    """
    A class to make protocol testing more convenient.
    """

    def __init__(self, log_file="protocol_test.log", test_data=None, config_file=None):
        self.available_cmd_parameters = AVAILABLE_CMD_PARAMETERS
        self.remote_sockets = None
        self.printer = TestPrinter(log_file)
        self.remotes = {}
        self.command_handler = TestCommandHandler(self.printer)
        self.names = {}
        self.test_data = test_data
        self.config_file = config_file
        self.input_list = []
        self.config_handler = None

    def display(self, message, log=False):
        self.printer.display(message, log)

    def log(self, message, append=True):
        self.printer.log(message, append)

    def node_process(self, ssddp_node_name, command_sock):
        try:
            ssddp_node = SSDDP(name=ssddp_node_name, external_command_input=command_sock, remote_run=True)
            ssddp_node.start()
            return NodeCreationType.SUCCESS
        except AttributeError as e:
            self.display(e.args)
        return NodeCreationType.FAILED

    def echo_node(self, command_sock):
        message = "Echo node waiting for command..."
        self.display(message)
        self.log(message)
        command_in = command_sock.recv(TEST_BUFFER_SIZE)
        command_sock.sendall(command_in)

    def show_dict(self, custom_dict):
        for key, value in custom_dict.items():
            message = "{0}: {1}".format(key, value)
            self.display(message)

    def send_shut_down_to_sockets(self):
        if not self.remotes:
            self.display("no sockets")
        for node_socket in self.remotes.values():
            node_socket.sendall(bytes(NodeCommand.SHUTDOWN, 'UTF-8'))
            res = node_socket.recv(TEST_BUFFER_SIZE).decode('UTF-8')
            if res == NodeCommand.OK:
                self.display("Successfully sent shutdown command!")
            else:
                self.display("Shutdown command failed!")
            node_socket.close()

    def clean_up_sequence(self):
        self.display("Letting nodes shutdown..")
        time.sleep(4)
        self.display("Clean up stage started!")
        cleaner = NodeProcessCleanUp(__file__)  # for verbose output -> set print_result=True
        given_input = input("Show status check [y/n]:")
        if given_input is 'y':
            cleaner.check_status()
        self.display("Found nodes still running...")
        cleaner.kill_nodes(__name__, False)
        given_input = input("Kill processes [y/n]:")
        if given_input is 'y':
            cleaner.kill_nodes(__name__)
        elif given_input is not 'n':
            self.display("Choice '" + given_input + "' not available")
            return
        given_input = input("Show status check [y/n]:")
        if given_input is 'y':
            cleaner.check_status()
        self.display("Clean up completed!")

    def handle_echo_command(self):
        echo_child, echo_parent = socket.socketpair()
        pid = os.fork()
        if pid:
            echo_child.close()
            time.sleep(4)
            user_input_echo = input("Give line to echo: ")
            echo_parent.sendall(bytes(user_input_echo, 'UTF-8'))
            echo_parent.settimeout(10)
            echo_message = echo_parent.recv(TEST_BUFFER_SIZE).decode('UTF-8')
            self.display("Echo: {0}\n".format(echo_message))
            echo_parent.close()
        else:
            echo_parent.close()
            self.echo_node(echo_child)
            echo_child.close()
            exit()

    def select_node_name(self):
        self.show_dict(self.names)
        user_input_describe = input("Choose node to send command: ")
        user_choice_describe = int(user_input_describe)
        return user_choice_describe

    def select_destination_node(self, obj_desc):
        destination_nodes = {}
        for j, name_desc in enumerate(obj_desc):
            destination_nodes[j+1] = name_desc
            self.display("{0}. {1}".format(j+1, name_desc))
        user_input_describe = input("Choose node to send description request:")
        user_choice_describe = int(user_input_describe)
        destination_node = destination_nodes[user_choice_describe]
        return destination_node

    def handle_describe_command(self, desc_command):
        self.display(desc_command)
        self.display(self.names)
        user_choice_describe = self.select_node_name()
        try:
            self.display(self.names[user_choice_describe])
            node_name_desc = self.names[user_choice_describe]
            sock_desc = self.remotes[node_name_desc]
            # Get nodes peers
            sock_desc.sendall(bytes(NodeCommand.PEERS, 'UTF-8'))
            message = sock_desc.recv(TEST_BUFFER_SIZE).decode('UTF-8')
            self.display("Nodes peers:")
            self.display(message)
            obj_desc = json.loads(message)
            self.display("Nodes available:")
            destination_node = self.select_destination_node(obj_desc)
            self.display(destination_node)
            desc_command += " " + destination_node
            self.display(desc_command)
            sock_desc.sendall(bytes(desc_command, 'UTF-8'))

        except KeyError:
            self.display("Not a valid option")

    def init_nodes(self):
        self.input_list = [sys.stdin]
        failed_count = 0
        success_count = 0
        for i, name in self.names.items():
            self.display(name)
            child, parent = socket.socketpair()
            pid = os.fork()
            if pid:
                self.display("Created node " + name + ".")
                self.input_list.append(parent)
                child.close()
                self.remotes[name] = parent
                # parent.settimeout(8)
                response = parent.recv(TEST_BUFFER_SIZE).decode('UTF-8')
                self.display("Received message from child: " + response)
                if response == NodeCreationType.FAILED:
                    failed_count += 1
                else:
                    success_count += 1

            else:
                self.display("Created node " + name + ".")
                parent.close()
                result = self.node_process(name, child)
                self.display("Result: " + result)
                if result == NodeCreationType.FAILED:
                    child.sendall(bytes(result, 'UTF-8'))
                child.close()
                exit()

        if failed_count == len(self.names):
            self.display("All node initialization failed!\nEnding test!")
            for sock in self.remotes.values():
                sock.close()
            exit(0)
        else:
            self.display("Initialized {0} nodes.".format(success_count))
        return self.input_list

    def get_config_file(self):
        if self.config_file:
            file = self.config_file
        else:
            argument_handler = MainArgumentHandler()
            file = argument_handler.handle_arguments()
        return file

    def create_config_handler(self):
        config_handler = None
        if self.test_data:
            config_handler = TesterConfigHandler(self.test_data)
        else:
            file = self.get_config_file()
            if not file:
                self.display("No configuration file was given.")
                # logger.info("No configuration file was given.")
                exit()
            else:
                try:
                    config_handler = TesterConfigHandler(file)
                except FileNotFoundError:
                    self.display("Configuration file not found! Please check that file exists or path is correct!")
                    # logger.info("Configuration file not found! Please check that file exists or path is correct!")
                    exit()
        return config_handler

    def display_available_cmd_parameters(self):
        self.display("Command parameters available:")
        for i, cmd in enumerate(self.available_cmd_parameters):
            self.display("{0}: {1}".format(i+1, cmd))

    def setup_test(self):
        self.display("Setting up test.")
        self.config_handler = self.create_config_handler()

        if not self.config_handler:
            exit()
        self.names = self.config_handler.get_node_names()
        if self.names is None:
            exit()

        self.config_handler = None
        self.display("Initializing input list.")
        self.init_nodes()
        self.display("Input list initialized.")

        self.display("Test setup complete.")
        self.display("Starting testing stage.")
        self.command_handler.choices()

    def start(self):
        try:
            self.setup_test()
            while True:

                    input_ready, output_ready, except_ready = select.select(self.input_list, [], [])

                    for x in input_ready:

                        if x == sys.stdin:
                            line = sys.stdin.readline()
                            self.display("Read command: " + line)
                            command = self.command_handler.handle_input(line.strip())
                            if command == NodeCommand.INCOMPLETE_COMMAND:
                                self.display("Add command parameter!")
                                self.display("Command parameters:")
                                self.display_available_cmd_parameters()
                            elif command == NodeCommand.EXIT:
                                self.end_test()
                            elif command == NodeCommand.DESCRIBE:
                                self.handle_describe_command(command)
                            elif command == NodeCommand.DISPLAY:
                                self.display("Command not yet available..")
                            elif command == NodeCommand.HELP:
                                self.display_available_cmd_parameters()
                            elif command == NodeCommand.ECHO:
                                self.handle_echo_command()
                            self.command_handler.choices()
                        else:
                            for sock in self.remotes:
                                if x == sock:
                                    message = sock.recv()
                                    self.display(message)

        except KeyboardInterrupt:
            for sock in self.remotes:
                sock.close()
            self.user_interruption()

    def end_test(self):
        self.display("Ending test...")
        self.send_shut_down_to_sockets()
        self.clean_up_sequence()
        self.display("Test ended!")
        exit(0)

    def user_interruption(self):
        self.display("\n")
        self.display("User interrupted test!")
        self.clean_up_sequence()
        self.display("Ending test!")


class TestCommandHandler(object):
    """
    A class for handling commands in protocol testing.
    """

    def __init__(self, printer,):
        self.command_list = []
        self.logger = logging.getLogger("Tester")
        self.printer = printer

    def display(self, message):
        self.printer.display(message)

    def handle_input(self, input_line):
        # print(input_line)
        if input_line == "exit" or input_line == "quit":
            return NodeCommand.EXIT
        if input_line == "cmd" or input_line.startswith("cmd"):
            return self.handle_command(input_line)
        if input_line == "echo":
            return NodeCommand.ECHO

    def handle_command(self, input_line):
        parameters = input_line.split(' ')
        if parameters[0].strip() == "cmd":
            if len(parameters) == 1:
                return NodeCommand.INCOMPLETE_COMMAND
            if parameters[1].strip() == NodeCommand.DESCRIBE:
                return NodeCommand.DESCRIBE
            elif parameters[1].strip() == NodeCommand.DISPLAY:
                return NodeCommand.DISPLAY
            elif parameters[1].strip() == NodeCommand.HELP:
                return NodeCommand.HELP

    def usage(self):
        self.display("Type cmd --help to get list of commands.")
        self.display("To end test use: 'exit' or 'quit'")

    @staticmethod
    def command_usage():
        return "cmd <command>"

    def choices(self):
        self.display("Valid input formats:")
        self.display("1. {0}".format(self.command_usage()))
        self.display("2. exit")


