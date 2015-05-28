import sys
import os
import socket
import time
import json
from sys import exit
from random import choice

from app.ssddp_v2 import SSDDP
from protocol_testing.tester_config_handler import TesterConfigHandler
from app.globals import NodeCommand
from protocol_testing.node_process_cleanup import NodeProcessCleanUp
from printers_and_loggers.test_printer import TestPrinter
from printers_and_loggers.ui_printer import TestUIPrinter
from node.node_creation_type import NodeCreationType
from measurements.measurement_data import MeasurementData
from protocol_testing.test_command_handler import TestCommandHandler
from printers_and_loggers.node_printer import NodePrinter
from printers_and_loggers.measurement_logger import MeasurementLogger


TEST_BUFFER_SIZE = 1024
AVAILABLE_CMD_PARAMETERS = [NodeCommand.DESCRIBE, NodeCommand.DISPLAY, NodeCommand.HELP]


class BaseProtocolTesterV2(object):
    """
    Base class for creating protocol testers.
    """

    def __init__(self, test_script_file, measurer, log_file):
        self.available_cmd_parameters = AVAILABLE_CMD_PARAMETERS
        self.ui_printer = TestUIPrinter(log_file)
        self.remotes = {}
        self.printer = TestPrinter(log_file)
        self.command_handler = TestCommandHandler(self.printer)
        self.test_script_file = test_script_file
        self.input_list = []
        self.node_names = []
        self.previous_name = ""
        self.current_node_count = 0
        self.measurer = measurer

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
        self.node_names.append(node_name)
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
            return response  # Should improve code to validate response and return it.
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
            self.measurer.add_node(node_name, self.current_node_count)
            ssddp_node = SSDDP(name=node_name, measurer=self.measurer, services=node_services,
                               external_command_input=command_sock, remote_run=True)
            self.current_node_count += 1
            self.ui_printer.created_node(node_name)
            ssddp_node.remote_start()
            return NodeCreationType.SUCCESS
        except AttributeError as e:
            self.ui_printer.display(e.args)
        return NodeCreationType.FAILED

    def get_new_random_remote_name(self):
        old_name = self.previous_name
        name = self.previous_name
        while name is old_name:
            name = self.get_random_remote_name()
        return name

    def get_random_remote_name(self):

        self.previous_name = choice(list(self.remotes.keys()))
        return self.previous_name

    def get_remote_name_at(self, index):
        for i, k in enumerate(self.remotes):
            if i == index:
                self.previous_name = k
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
        print("Node count " + str(node_count))
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
        self.ui_printer.nodes_still_running()
        cleaner.get_node_pids()
        cleaner.kill_nodes(__name__)
        self.ui_printer.cleanup_complete()

    def shutdown_node(self, node_name):
        remote = self.remotes[node_name]
        self.send_shutdown_to_socket(remote, node_name)
        del self.remotes[node_name]

    def send_shutdown_to_socket(self, node_socket, node_name):
        try:
            node_socket.sendall(bytes(NodeCommand.SHUTDOWN, 'UTF-8'))
            res = node_socket.recv(TEST_BUFFER_SIZE).decode('UTF-8')
        except ConnectionResetError:
            self.ui_printer.display("Could not receive shutdown response from '{0}'".format(node_name))
            node_socket.close()
            return
        except BrokenPipeError:
            self.ui_printer.display("Could not send shutdown to '{0}'".format(node_name))
            return
        print("shutdown response: " + res)
        if res == NodeCommand.OK:
            self.ui_printer.shutdown_sent_success()
        else:
            self.ui_printer.shutdown_sent_failed()
        node_socket.close()

    def send_shutdown_to_sockets(self):
        if not self.remotes:
            self.ui_printer.no_sockets()
        #for node_socket in self.remotes.values():
        for node_name, node_socket in self.remotes.items():
            self.send_shutdown_to_socket(node_socket, node_name)

    def end_test(self, no_prompt=False):
        self.ui_printer.ending_test()
        self.send_shutdown_to_sockets()
        if no_prompt:
            self.cleanup_without_prompts()
        else:
            self.clean_up_sequence()
        self.ui_printer.end_test()
        exit(0)

    def start_remote_node(self, node_at_index, seconds_to_wait=3):
        remote_name = self.node_names[node_at_index]
        self.ui_printer.starting_node(remote_name)
        self.start_node(remote_name, self.current_node_count)
        self.current_node_count += 1
        self.ui_printer.node_started(remote_name)
        self.ui_printer.waiting_for_broadcast_test(seconds_to_wait)
        time.sleep(seconds_to_wait)


class BaseProtocolTester(object):
    """
    Base class for creating protocol testers.
    """

    def __init__(self, log_file, test_script_file, node_log_file=None, measurement_log_file=None):
        self.available_cmd_parameters = AVAILABLE_CMD_PARAMETERS
        self.ui_printer = TestUIPrinter(log_file)
        self.remotes = {}
        self.printer = TestPrinter(log_file)
        self.command_handler = TestCommandHandler(self.printer)
        self.test_script_file = test_script_file
        self.input_list = []
        self.node_names = []
        self.previous_name = ""
        self.current_node_count = 0
        self.log_file = log_file
        self.node_log_file = node_log_file
        self.measurement_logger = MeasurementLogger(measurement_log_file)

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
        self.node_names.append(node_name)
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
            return response  # Should improve code to validate response and return it.
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
            measurement_data = MeasurementData(node_name, self.current_node_count,
                                               NodePrinter(node_name, self.node_log_file, True),
                                               self.measurement_logger)
            ssddp_node = SSDDP(name=node_name, services=node_services,
                               external_command_input=command_sock, remote_run=True, nodes_in_test=0,
                               measurement_data=measurement_data, log_file=self.node_log_file)
            self.ui_printer.created_node(node_name)
            ssddp_node.remote_start()
            return NodeCreationType.SUCCESS
        except AttributeError as e:
            self.ui_printer.display(e.args)
        return NodeCreationType.FAILED

    def get_new_random_remote_name(self):
        old_name = self.previous_name
        name = self.previous_name
        while name is old_name:
            name = self.get_random_remote_name()
        return name

    def get_random_remote_name(self):

        self.previous_name = choice(list(self.remotes.keys()))
        return self.previous_name

    def get_remote_name_at(self, index):
        for i, k in enumerate(self.remotes):
            if i == index:
                self.previous_name = k
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
        print("Node count " + str(node_count))
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
        self.ui_printer.nodes_still_running()
        cleaner.get_node_pids()
        cleaner.kill_nodes(__name__)
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

    def start_remote_node(self, node_at_index, seconds_to_wait=3):
        remote_name = self.node_names[node_at_index]
        self.ui_printer.starting_node(remote_name)
        self.start_node(remote_name, self.current_node_count)
        self.current_node_count += 1
        self.ui_printer.node_started(remote_name)
        self.ui_printer.waiting_for_broadcast_test(seconds_to_wait)
        time.sleep(seconds_to_wait)

