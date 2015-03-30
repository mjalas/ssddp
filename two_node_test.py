from threading import Thread
import sys
import os
import socket
import select
import time
import json


import getopt
from sys import argv, exit

from enum import Enum
import logging

from app.ssddp import SSDDP
from protocol_testing.main_argument_handler import MainArgumentHandler
from protocol_testing.tester_config_handler import TesterConfigHandler
from protocol_testing.config_test_file import ConfigurationNode
from manager.command_handler import DESCRIBE_COMMAND, DISPLAY_COMMAND, AVAILABLE_COMMANDS
from app.globals import NodeCommand
from protocol_testing.node_process_cleanup import NodeProcessCleanUp

TEST_BUFFER_SIZE = 1024


class NodeCreationType():
    SUCCESS = "success"
    FAILED = "failed"


class TestCommandHandler(object):
    """

    """

    def __init__(self):
        self.command_list = [DESCRIBE_COMMAND, DISPLAY_COMMAND]
        self.logger = logging.getLogger("Tester")

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
                print("Add command parameter!")
                print("Command parameters:")
                for available_command in AVAILABLE_COMMANDS:
                    print(available_command)
                return None
            if parameters[1].strip() == DESCRIBE_COMMAND:
                return NodeCommand.DESCRIBE
            elif parameters[1].strip() == DISPLAY_COMMAND:
                return NodeCommand.DISPLAY

    def usage(self):
        print("Type cmd --help to get list of commands.")
        print("To end test use: 'exit' or 'quit'")

    def command_usage(self):
        return "cmd <command>"

    def choices(self):
        print("Valid input formats:")
        print("1. {0}".format(self.command_usage()))
        print("2. exit")


def node_process(ssddp_node_name, command_sock):
    try:
        ssddp_node = SSDDP(name=ssddp_node_name, external_command_input=command_sock, remote_run=True)
        ssddp_node.start()
        return NodeCreationType.SUCCESS
    except AttributeError as e:
        print(e.args)
    return NodeCreationType.FAILED


def echo_node(command_sock):
    print("Echo node waiting for command...")
    command_in = command_sock.recv(TEST_BUFFER_SIZE)
    command_sock.sendall(command_in)


def show_dict(custom_dict):
    for key, value in custom_dict.items():
        print("{0}: {1}".format(key, value))


def send_shut_down_to_sockets(node_sockets):
    if not node_sockets:
        print("no sockets")
    for node_socket in node_sockets.values():
        node_socket.sendall(bytes(NodeCommand.SHUTDOWN, 'UTF-8'))
        res = node_socket.recv(TEST_BUFFER_SIZE).decode('UTF-8')
        if res == NodeCommand.OK:
            print("Successfully sent shutdown command!")
        else:
            print("Shutdown command failed!")
        node_socket.close()


def clean_up_sequence():
    print("Clean up stage started!")
    cleaner = NodeProcessCleanUp(__file__)  # for verbose output -> set print_result=True
    if cleaner.get_node_pids():
        print("Found nodes still running...")
        cleaner.kill_nodes(False)
        given_input = input("Kill processes [y/n]:")
        if given_input is 'y':
            cleaner.kill_nodes()
        elif given_input is not 'n':
            print("Choice '" + given_input + "' not available")
            return
    given_input = input("Show status check [y/n]:")
    if given_input is 'y':
        cleaner.check_status()
    print("Clean up completed!")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("Setting up test.")
    sockets = {}
    try:
        print("Setting up test.")
        argument_handler = MainArgumentHandler()
        file = argument_handler.handle_arguments()
        config_handler = None
        if not file:
            print("No configuration file was given.")
            # logger.info("No configuration file was given.")
            exit()
        try:
            config_handler = TesterConfigHandler(file)
        except FileNotFoundError:
            print("Configuration file not found! Please check that file exists or path is correct!")
            # logger.info("Configuration file not found! Please check that file exists or path is correct!")
            exit()
        names = config_handler.get_node_names()
        if names is None:
            exit()

        # pipes = {}

        print("Initializing input list.")
        input_list = [sys.stdin]
        failed_count = 0
        success_count = 0

        for i, name in names.items():
            print(name)
            # child, parent = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)
            child, parent = socket.socketpair()
            pid = os.fork()
            if pid:
                print("Created node " + name + ".")
                input_list.append(parent)
                child.close()
                sockets[name] = parent
                # parent.settimeout(8)
                message = parent.recv(TEST_BUFFER_SIZE).decode('UTF-8')
                print("Received message from child: " + message)
                if message == NodeCreationType.FAILED:
                    failed_count += 1
                else:
                    success_count += 1

            else:
                print("Created node " + name + ".")
                parent.close()
                result = node_process(name, child)
                print("Result: " + result)
                if result == NodeCreationType.FAILED:
                    child.sendall(bytes(result, 'UTF-8'))
                child.close()
                exit()

        if failed_count == len(names):
            print("All node initialization failed!\nEnding test!")
            for sock in sockets.values():
                sock.close()
            exit(0)
        else:
            print("Initialized {0} nodes.".format(success_count))

        print("Input list initialized.")

        print("Test setup complete.")
        command_handler = TestCommandHandler()
        command_handler.choices()

        print("Starting testing stage.")
        while True:

                input_ready, output_ready, except_ready = select.select(input_list, [], [])

                for x in input_ready:

                    if x == sys.stdin:
                        line = sys.stdin.readline()
                        print("Read command: " + line)
                        command = command_handler.handle_input(line.strip())
                        if command == NodeCommand.EXIT:
                            print("Ending test...")
                            send_shut_down_to_sockets(sockets)
                            print("Test ended!")
                            exit(0)
                        elif command == NodeCommand.DESCRIBE:
                            print(command)
                            print(names)
                            show_dict(names)
                            user_input = input("Choose node to send command: ")
                            user_choice = int(user_input)
                            try:
                                print(names[user_choice])
                                node_name = names[user_choice]
                                sock = sockets[node_name]
                                # Get nodes peers
                                sock.sendall(bytes(NodeCommand.PEERS, 'UTF-8'))
                                message = sock.recv(TEST_BUFFER_SIZE).decode('UTF-8')
                                print("Nodes peers:")
                                print(message)
                                obj = json.loads(message)
                                print("Nodes available:")
                                for i, name in enumerate(obj):
                                    print("{0}. {1}".format(i+1, name))
                                user_input = input("Choose node to send description request:")
                                user_choice = int(user_input)
                                dest_node = obj[user_choice-1].name
                                print(dest_node)
                                command += command + " " + dest_node
                                sock.sendall(bytes(command, 'UTF-8'))
                                break
                            except KeyError:
                                print("Not a valid option")
                        elif command == NodeCommand.DISPLAY:
                            pass
                        elif command == NodeCommand.ECHO:
                            echo_child, echo_parent = socket.socketpair()
                            pid = os.fork()
                            if pid:
                                echo_child.close()
                                time.sleep(4)
                                user_input = input("Give line to echo: ")
                                echo_parent.sendall(bytes(user_input, 'UTF-8'))
                                echo_parent.settimeout(10)
                                message = echo_parent.recv(TEST_BUFFER_SIZE).decode('UTF-8')
                                print("Echo: {0}\n".format(message))
                                echo_parent.close()
                                break
                            else:
                                echo_parent.close()
                                echo_node(echo_child)
                                echo_child.close()
                                exit()
                    else:
                        for sock in sockets:
                            if x == sock:
                                message = sock.recv()
                                print(message)

                command_handler.choices()
                # command = ""

    except KeyboardInterrupt:
        for s in sockets:
            s.close()
        print("\n")
        print("User interrupted test!")
        clean_up_sequence()
        print("Ending test!")


