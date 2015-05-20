import sys
import os
import socket
import select
import time
import json
from datetime import datetime
from sys import argv, exit
import logging
from random import choice

from app.ssddp import SSDDP
from protocol_testing.main_argument_handler import MainArgumentHandler
from protocol_testing.tester_config_handler import TesterConfigHandler
from app.globals import NodeCommand
from protocol_testing.node_process_cleanup import NodeProcessCleanUp
from protocol_testing.config_test_file import ConfigurationNode
from protocol_testing.test_printer import TestPrinter
from protocol_testing.ui_printer import TestUIPrinter
from node.node_creation_type import NodeCreationType

TEST_BUFFER_SIZE = 1024
AVAILABLE_CMD_PARAMETERS = [NodeCommand.DESCRIBE, NodeCommand.DISPLAY, NodeCommand.HELP]


class BaseProtocolTester(object):
    """
    Base class for creating protocol testers.
    """

    def __init__(self, node_count, log_file, test_script_file):
        self.available_cmd_parameters = AVAILABLE_CMD_PARAMETERS
        self.ui_printer = TestUIPrinter(log_file)
        self.remotes = {}
        self.printer = TestPrinter(log_file)
        self.command_handler = TestCommandHandler(self.printer)
        self.node_count = node_count
        self.test_script_file = test_script_file
        self.input_list = []

    def init_nodes_from_config_nodes(self, config_nodes):
        self.input_list = [sys.stdin]
        failed_count = 0
        success_count = 0
        for config_node in config_nodes:
            self.ui_printer.display(config_node.name)
            result = self.init_node(config_node.name, config_node.services)
            if result == NodeCreationType.SUCCESS:
                success_count += 1
            else:
                failed_count += 1

        if failed_count == len(config_nodes):
            self.ui_printer.all_nodes_init_failed()
            for sock in self.remotes.values():
                sock.close()
            exit(0)
        else:
            self.ui_printer.nodes_initialized(success_count)

    def init_node(self, node_name, node_services):
        result = NodeCreationType.FAILED
        child, parent = socket.socketpair()
        pid = os.fork()
        if pid:
            result = self.handle_parent_part(child, parent, node_name)
        else:
            self.handle_child_part(child, parent, node_name, node_services)
            exit()
        return result

    def setup_nodes_from_config_file(self, config_file):
        config_handler = TesterConfigHandler.create_config_handler_from_file(config_file)
        self.init_nodes_from_config_nodes(config_handler.config_nodes)

    def handle_parent_part(self, child, parent, node_name):
        # self.ui_printer.created_node(node_name)
        child.close()
        self.remotes[node_name] = parent
        # parent.settimeout(8)
        response = parent.recv(TEST_BUFFER_SIZE).decode('UTF-8')
        self.ui_printer.received_message_from_child(response)
        if response == NodeCreationType.FAILED:
            return response                     # Should improve code to validate response and return it.
        else:
            return NodeCreationType.SUCCESS

    def handle_child_part(self, child, parent, node_name, node_services):
        # self.ui_printer.created_node(node_name)
        parent.close()
        result = self.create_node_process(node_name, node_services, child)
        self.ui_printer.result(result)
        if result == NodeCreationType.FAILED:
            child.sendall(bytes(result, 'UTF-8'))
            child.close()

    def create_node_process(self, node_name, node_services, command_sock):
        try:

            ssddp_node = SSDDP(name=node_name, services=node_services,
                               external_command_input=command_sock, remote_run=True, nodes_in_test=0)
            self.ui_printer.created_node(node_name)
            ssddp_node.remote_start()
            return NodeCreationType.SUCCESS
        except AttributeError as e:
            self.ui_printer.display(e.args)
        return NodeCreationType.FAILED

    def get_random_remote_name(self):
        return choice(list(self.remotes.keys()))

    def get_remote_name_at(self, index):
        for i, k in enumerate(self.remotes):
            if i == index:
                return k
        raise IndexError("Index out of bound")

    def get_peers_for_node(self, node_name):
        node_sock = self.remotes[node_name]
        node_sock.sendall(bytes(NodeCommand.PEERS, 'UTF-8'))
        message = node_sock.recv(TEST_BUFFER_SIZE).decode('UTF-8')
        self.ui_printer.nodes_peers()
        self.ui_printer.display(message)
        obj_desc = json.loads(message)
        destination_nodes = []
        for name in obj_desc:
            destination_nodes.append(name)
        return destination_nodes

    def get_random_peer_for_node(self, node_name):
        peers = self.get_peers_for_node(node_name)
        return choice(peers)

    def start_node(self, node_name, node_count):
        remote = self.remotes[node_name]
        command = NodeCommand.START + ":" + str(node_count)
        remote.sendall(bytes(command, 'UTF-8'))
        response = remote.recv(TEST_BUFFER_SIZE).decode('UTF-8')
        if response == NodeCommand.START_SUCCESS:
            self.ui_printer.successfully_started_node(node_name)
        else:
            self.ui_printer.failed_to_start_node(node_name)

    def get_measurements(self, node_name):
        pass

    def send_description_request(self, sender, receiver):
        remote = self.remotes[sender]
        command = "{0} {1}".format(NodeCommand.DESCRIBE, receiver)
        remote.sendall(bytes(command, 'UTF-8'))
        self.ui_printer.printer.display("Sent '{0}' to {1}".format(command, sender))
        response = remote.recv(TEST_BUFFER_SIZE).decode('UTF-8')
        self.ui_printer.printer.display("Received '{0}' from {1}".format(response, receiver))

    def clean_up_sequence(self):
        self.ui_printer.letting_nodes_shutdown()
        time.sleep(4)
        self.ui_printer.cleanup_started()
        cleaner = NodeProcessCleanUp(self.test_script_file)  # for verbose output -> set print_result=True
        given_input = input("Show status check [y/n]:")
        if given_input is 'y':
            cleaner.check_status()
        self.ui_printer.nodes_still_running()
        cleaner.get_node_pids()
        cleaner.kill_nodes(__name__, False)
        given_input = input("Kill processes [y/n]:")
        if given_input is 'y':
            cleaner.kill_nodes(__name__)
        elif given_input is not 'n':
            self.ui_printer.choice_not_available(given_input)
            return
        given_input = input("Show status check [y/n]:")
        if given_input is 'y':
            cleaner.check_status()
        self.ui_printer.cleanup_complete()

    def cleanup_without_prompts(self):
        self.ui_printer.letting_nodes_shutdown()
        time.sleep(4)
        self.ui_printer.cleanup_started()
        cleaner = NodeProcessCleanUp(self.test_script_file)  # for verbose output -> set print_result=True
        cleaner.check_status()
        self.ui_printer.nodes_still_running()
        cleaner.get_node_pids()
        cleaner.kill_nodes(__name__)
        cleaner.check_status()
        self.ui_printer.cleanup_complete()

    def send_shut_down_to_sockets(self):
        if not self.remotes:
            self.ui_printer.no_sockets()
        for node_socket in self.remotes.values():
            node_socket.sendall(bytes(NodeCommand.SHUTDOWN, 'UTF-8'))
            res = node_socket.recv(TEST_BUFFER_SIZE).decode('UTF-8')
            print("shutdown response: " + res)
            if res == NodeCommand.OK:
                self.ui_printer.shutdown_sent_success()
            else:
                self.ui_printer.shutdown_sent_failed()
            node_socket.close()

    def end_test(self, no_prompt=False):
        self.ui_printer.ending_test()
        self.send_shut_down_to_sockets()
        if no_prompt:
            self.cleanup_without_prompts()
        else:
            self.clean_up_sequence()
        self.ui_printer.end_test()
        exit(0)


class ProtocolTester(object):
    """
    A class to make protocol testing more convenient.
    """

    def __init__(self, log_file="protocol_test.log", test_data=None, config_file=None, display_outputs=True):
        self.available_cmd_parameters = AVAILABLE_CMD_PARAMETERS
        self.remote_sockets = None
        self.printer = TestPrinter(log_file)
        self.remotes = {}
        self.command_handler = TestCommandHandler(self.printer)
        self.names = {}
        self.node_names = []
        self.test_data = test_data
        self.config_file = config_file
        self.input_list = []
        self.config_handler = None
        self.services = {}
        self.ui_printer = TestUIPrinter()

    def node_process(self, ssddp_node_name, command_sock):
        try:
            if self.services:
                services = self.services[ssddp_node_name]
                ssddp_node = SSDDP(name=ssddp_node_name, external_command_input=command_sock, remote_run=True,
                                   services=services)
            else:
                ssddp_node = SSDDP(name=ssddp_node_name, external_command_input=command_sock, remote_run=True)
            ssddp_node.start()
            return NodeCreationType.SUCCESS
        except AttributeError as e:
            self.ui_printer.display(e.args)
        return NodeCreationType.FAILED

    def echo_node(self, command_sock):
        self.ui_printer.echo_node_waiting()
        command_in = command_sock.recv(TEST_BUFFER_SIZE)
        command_sock.sendall(command_in)

    def show_dict(self, custom_dict):
        for key, value in custom_dict.items():
            self.ui_printer.show_key_value_pair(key, value)

    def send_shut_down_to_sockets(self):
        if not self.remotes:
            self.ui_printer.no_sockets()
        for node_socket in self.remotes.values():
            node_socket.sendall(bytes(NodeCommand.SHUTDOWN, 'UTF-8'))
            res = node_socket.recv(TEST_BUFFER_SIZE).decode('UTF-8')
            if res == NodeCommand.OK:
                self.ui_printer.shutdown_sent_success()
            else:
                self.ui_printer.shutdown_sent_failed()
            node_socket.close()

    def clean_up_sequence(self):
        self.ui_printer.letting_nodes_shutdown()
        time.sleep(4)
        self.ui_printer.cleanup_started()
        cleaner = NodeProcessCleanUp(__file__)  # for verbose output -> set print_result=True
        given_input = input("Show status check [y/n]:")
        if given_input is 'y':
            cleaner.check_status()
        self.ui_printer.nodes_still_running()
        cleaner.get_node_pids()
        cleaner.kill_nodes(__name__, False)
        given_input = input("Kill processes [y/n]:")
        if given_input is 'y':
            cleaner.kill_nodes(__name__)
        elif given_input is not 'n':
            self.ui_printer.choice_not_available(given_input)
            return
        given_input = input("Show status check [y/n]:")
        if given_input is 'y':
            cleaner.check_status()
        self.ui_printer.cleanup_complete()

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
            self.ui_printer.echo_received(echo_message)
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
        destination_nodes = self.show_node_selection(obj_desc)
        user_input_describe = input("Choose node to send description request:")
        user_choice_describe = int(user_input_describe)
        destination_node = destination_nodes[user_choice_describe]
        return destination_node

    def show_node_selection(self, object_description):
        destination_nodes = {}
        for j, name_desc in enumerate(object_description):
            destination_nodes[j + 1] = name_desc
            self.ui_printer.show_node_enumeration(j + 1, name_desc)
        return destination_nodes

    def select_node(self):
        try:
            self.ui_printer.display(self.names)
            user_choice = self.select_node_name()
            self.ui_printer.display(self.names[user_choice])
            node_name = self.names[user_choice]
            return self.remotes[node_name]
        except KeyError:
            self.ui_printer.option_not_valid()
            return None

    def handle_describe_command(self, desc_command):
        self.ui_printer.display(desc_command)
        if not self.names:
            self.ui_printer.node_names_not_available()
            return

        sock_desc = self.select_node()
        if sock_desc:
            # Get nodes peers
            sock_desc.sendall(bytes(NodeCommand.PEERS, 'UTF-8'))
            message = sock_desc.recv(TEST_BUFFER_SIZE).decode('UTF-8')
            self.ui_printer.nodes_peers()
            self.ui_printer.display(message)
            obj_desc = json.loads(message)
            self.ui_printer.nodes_available()
            destination_node = self.select_destination_node(obj_desc)
            self.ui_printer.display(destination_node)
            desc_command += " " + destination_node
            self.ui_printer.display(desc_command)
            sock_desc.sendall(bytes(desc_command, 'UTF-8'))
            self.ui_printer.communication_wait()
            time.sleep(4)

    def handle_display_command(self):
        if not self.names:
            self.ui_printer.node_names_not_available()
            return

        sock_disp = self.select_node()
        if sock_disp:
            sock_disp.sendall(bytes(NodeCommand.DISPLAY, 'UTF-8'))
            message = sock_disp.recv(TEST_BUFFER_SIZE).decode('UTF-8')
            self.ui_printer.display(message)
            time.sleep(4)

    def init_nodes(self):
        self.input_list = [sys.stdin]
        failed_count = 0
        success_count = 0
        for i, name in self.names.items():
            self.ui_printer.display(name)
            child, parent = socket.socketpair()
            pid = os.fork()
            if pid:
                self.ui_printer.created_node(name)
                self.input_list.append(parent)
                child.close()
                self.remotes[name] = parent
                # parent.settimeout(8)
                response = parent.recv(TEST_BUFFER_SIZE).decode('UTF-8')
                self.ui_printer.received_message_from_child(response)
                if response == NodeCreationType.FAILED:
                    failed_count += 1
                else:
                    success_count += 1

            else:
                self.ui_printer.created_node(name)
                parent.close()
                result = self.node_process(name, child)
                self.ui_printer.result(result)
                if result == NodeCreationType.FAILED:
                    child.sendall(bytes(result, 'UTF-8'))
                child.close()
                exit()

        if failed_count == len(self.names):
            self.ui_printer.all_nodes_init_failed()
            for sock in self.remotes.values():
                sock.close()
            exit(0)
        else:
            self.ui_printer.nodes_initialized(success_count)
        return self.input_list

    def handle_parent_part(self, child, config_node, failed_count, parent, success_count):
        self.ui_printer.display("Created node " + config_node.name + ".")
        self.input_list.append(parent)
        child.close()
        self.remotes[config_node.name] = parent
        # parent.settimeout(8)
        response = parent.recv(TEST_BUFFER_SIZE).decode('UTF-8')
        self.ui_printer.received_message_from_child(response)
        if response == NodeCreationType.FAILED:
            failed_count += 1
        else:
            success_count += 1
        return failed_count, success_count

    def handle_child_part(self, child, config_node, parent):
        self.ui_printer.created_node(config_node.name)
        parent.close()
        result = self.create_node_process(config_node, child)
        self.ui_printer.result(result)
        if result == NodeCreationType.FAILED:
            child.sendall(bytes(result, 'UTF-8'))
            child.close()

    def init_nodes_from_config_nodes(self, config_nodes):
        self.input_list = [sys.stdin]
        failed_count = 0
        success_count = 0
        for config_node in config_nodes:
            self.ui_printer.display(config_node.name)
            child, parent = socket.socketpair()
            pid = os.fork()
            if pid:
                failed_count, success_count = self.handle_parent_part(child, config_node, failed_count, parent,
                                                                      success_count)
            else:
                self.handle_child_part(child, config_node, parent)
                exit()

        if failed_count == len(config_nodes):
            self.ui_printer.all_nodes_init_failed()
            for sock in self.remotes.values():
                sock.close()
            exit(0)
        else:
            self.ui_printer.nodes_initialized(success_count)
        return self.input_list

    def create_node_process(self, config_node, command_sock):
        if not isinstance(config_node, ConfigurationNode):
            raise ValueError("No ConfigurationNode given")
        try:
            ssddp_node = SSDDP(name=config_node.name, services=config_node.services,
                               external_command_input=command_sock,
                               remote_run=True)
            ssddp_node.start()
            return NodeCreationType.SUCCESS
        except AttributeError as e:
            self.ui_printer.display(e.args)
        return NodeCreationType.FAILED

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
                self.ui_printer.config_missing()
                # logger.info("No configuration file was given.")
                exit()
            else:
                try:
                    config_handler = TesterConfigHandler(file, use_config_nodes=True)
                except FileNotFoundError:
                    self.ui_printer.config_not_found()
                    # logger.info("Configuration file not found! Please check that file exists or path is correct!")
                    exit()
        return config_handler

    def display_available_cmd_parameters(self):
        self.ui_printer.available_command_parameters()
        for i, cmd in enumerate(self.available_cmd_parameters):
            self.ui_printer.display("{0}: {1}".format(i + 1, cmd))

    def setup_test(self):
        self.ui_printer.setup_test()
        self.config_handler = self.create_config_handler()

        if not self.config_handler:
            exit()
        self.names = self.config_handler.get_node_names()
        self.services = self.config_handler.get_services_for_nodes()
        if self.names is None:
            exit()

        self.config_handler = None
        self.ui_printer.init_input_list()
        self.init_nodes()
        self.ui_printer.init_input_list(False)

        self.ui_printer.setup_complete()
        self.ui_printer.start_testing()
        self.command_handler.choices()

    def setup_test_v2(self):
        self.ui_printer.setup_test()
        self.config_handler = self.create_config_handler()

        if not self.config_handler:
            exit()

        # add node names to self.names
        for i, node in enumerate(self.config_handler.config_nodes):
            self.names[i] = node.name
        # self.config_handler = None
        self.ui_printer.init_input_list()
        self.init_nodes_from_config_nodes(self.config_handler.config_nodes)
        self.ui_printer.init_input_list(False)

        self.ui_printer.setup_complete()
        self.ui_printer.start_testing()
        self.command_handler.choices()

    def start(self):
        try:
            self.setup_test_v2()
            # self.setup_test()
            while True:

                input_ready, output_ready, except_ready = select.select(self.input_list, [], [])

                for x in input_ready:

                    if x == sys.stdin:
                        line = sys.stdin.readline()
                        self.ui_printer.read_command(line)
                        command = self.command_handler.handle_input(line.strip())
                        if command == NodeCommand.INCOMPLETE_COMMAND:
                            self.ui_printer.add_command_parameter()
                            self.ui_printer.command_parameters()
                            self.display_available_cmd_parameters()
                        elif command == NodeCommand.EXIT:
                            self.end_test()
                        elif command == NodeCommand.DESCRIBE:
                            self.handle_describe_command(command)
                        elif command == NodeCommand.DISPLAY:
                            self.handle_display_command()
                        elif command == NodeCommand.HELP:
                            self.display_available_cmd_parameters()
                        elif command == NodeCommand.ECHO:
                            self.handle_echo_command()
                        self.command_handler.choices()
                    else:
                        for sock in self.remotes:
                            if x == sock:
                                message = sock.recv()
                                self.ui_printer.display(message)

        except KeyboardInterrupt:
            for sock in self.remotes:
                sock.close()
            self.user_interruption()

    def end_test(self):
        self.ui_printer.ending_test()
        self.send_shut_down_to_sockets()
        self.clean_up_sequence()
        self.ui_printer.end_test()
        exit(0)

    def user_interruption(self):
        self.ui_printer.new_line()
        self.ui_printer.user_interrupted_test()
        self.clean_up_sequence()
        self.ui_printer.ending_test()


class TestCommandHandler(object):
    """
    A class for handling commands in protocol testing.
    """

    def __init__(self, printer, ):
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


